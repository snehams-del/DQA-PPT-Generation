// Package main is the entry point for the researcher service, orchestrating multiple AI agents
// (Researcher, Guide, Discovery) to assist with sailing voyage planning.
package main

import (
	"context"
	_ "embed"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/joho/godotenv"
	"github.com/tpryan/navalplan/services/researcher/config"
	"github.com/tpryan/navalplan/services/researcher/logging"
	"github.com/tpryan/navalplan/services/researcher/tools"
	"google.golang.org/adk/agent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/server/adkrest"
	"google.golang.org/adk/session"
	"google.golang.org/adk/tool"
)

//go:embed prompts/search_specialist.md
var _searchSpecialistPrompt string

//go:embed prompts/stop_agent.md
var _stopAgentPrompt string

//go:embed prompts/voyage_agent.md
var _voyageAgentPrompt string

//go:embed prompts/discovery_agent.md
var _discoveryAgentPrompt string

const maxOutputTokens = 65536

type Provider interface {
	Close() error
}

type Server struct {
	config *config.Config
	mu     sync.Mutex

	providers []Provider
}

func (s *Server) Close() {
	for _, p := range s.providers {
		if err := p.Close(); err != nil {
			slog.Error("Failed to close provider", "error", err)
		}
	}
}

func main() {
	// Load .env file (try current dir, then project root)
	godotenv.Load(".env")

	cfg, err := config.New(os.Getenv)
	if err != nil {
		slog.Error("Failed to load config", "error", err)
		os.Exit(1)
	}

	logging.InitLogging(cfg.Env)

	slog.Info("config", "modelName", cfg.ModelName)
	slog.Info("config", "port", cfg.Port)
	if len(cfg.MapsAPIKey) > 5 {
		slog.Info("config", "MapsAPIKey", cfg.MapsAPIKey[:5]+"...")
	}

	ctx := context.Background()
	srv := &Server{
		config: cfg,
	}
	defer srv.Close()

	if err := srv.run(ctx); err != nil {
		slog.Error("Application error", "error", err)
		os.Exit(1)
	}
}

func (s *Server) run(ctx context.Context) error {
	researcherTools, err := s.setupTools()
	if err != nil {
		return fmt.Errorf("setting up tools: %w", err)
	}

	toolMonitor := NewToolMonitor()

	voyageAgent, err := NewVoyageAgent(ctx, s.config, toolMonitor)
	if err != nil {
		return fmt.Errorf("creating guide agent: %w", err)
	}

	stopAgent, err := NewStopAgent(ctx, s.config, toolMonitor, researcherTools)
	if err != nil {
		return fmt.Errorf("creating researcher agent: %w", err)
	}

	discoveryAgent, err := NewDiscoveryAgent(ctx, s.config, toolMonitor)
	if err != nil {
		return fmt.Errorf("creating discovery agent: %w", err)
	}

	loader, err := agent.NewMultiLoader(stopAgent, voyageAgent, discoveryAgent)
	if err != nil {
		return fmt.Errorf("creating multi loader: %w", err)
	}

	config := &launcher.Config{
		AgentLoader:    loader,
		SessionService: session.InMemoryService(),
	}

	// Create the ADK HTTP Handler
	adkHandler := adkrest.NewHandler(config, 120*time.Second)

	// Start Custom Server
	mux := http.NewServeMux()

	// Mount ADK under /api/
	mux.Handle("/api/", http.StripPrefix("/api", adkHandler))

	slog.Info("Starting custom server", "port", s.config.Port)
	// Apply Trace Middleware then Logging Middleware
	return http.ListenAndServe(":"+s.config.Port, traceMiddleware(s.config.Project, loggingMiddleware(mux)))
}

func (s *Server) setupTools() ([]tool.Tool, error) {
	weatherTool, wp, err := tools.NewWeatherTool()
	if err != nil {
		return nil, err
	}
	s.providers = append(s.providers, wp)

	tideTool, tp, err := tools.NewTideTool()
	if err != nil {
		return nil, err
	}
	s.providers = append(s.providers, tp)

	sunriseTool, sp, err := tools.NewSunriseTool(s.config.MapsAPIKey)
	if err != nil {
		return nil, err
	}
	s.providers = append(s.providers, sp)

	placesTool, pp, err := tools.NewPlacesTool(s.config.MapsAPIKey)
	if err != nil {
		return nil, err
	}
	s.providers = append(s.providers, pp)

	return []tool.Tool{weatherTool, tideTool, sunriseTool, placesTool}, nil
}

var _ http.ResponseWriter = (*responseWriter)(nil)

type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseWriter) Flush() {
	if f, ok := rw.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		ww := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

		defer func() {
			timesince := time.Since(start)
			str := timesince.String()

			level := slog.LevelInfo
			if ww.statusCode >= 400 {
				level = slog.LevelWarn
			}
			if ww.statusCode >= 500 {
				level = slog.LevelError
			}

			slog.Log(r.Context(), level, "Request handled",
				"method", r.Method,
				"path", r.URL.Path,
				"status", ww.statusCode,
				"duration", str,
				"remote_addr", r.RemoteAddr,
			)
		}()

		next.ServeHTTP(ww, r)
	})
}

// traceMiddleware exists to make sure when running on Cloud Run, trace
// ids are propegated so that you can get debugging and analysis.
func traceMiddleware(projectID string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		traceHeader := r.Header.Get("X-Cloud-Trace-Context")
		traceParts := strings.Split(traceHeader, "/")
		if len(traceParts) > 0 && len(traceParts[0]) > 0 {
			traceID := traceParts[0]
			var trace string
			if projectID != "" {
				trace = fmt.Sprintf("projects/%s/traces/%s", projectID, traceID)
			} else {
				trace = traceID
			}
			ctx := logging.AddTraceToContext(r.Context(), trace)
			next.ServeHTTP(w, r.WithContext(ctx))
			return
		}
		next.ServeHTTP(w, r)
	})
}