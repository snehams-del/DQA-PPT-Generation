package auditor

import (
	"context"
	"strings"
	"testing"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/runner"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

func TestHappyPath(t *testing.T) {
	ctx := context.Background()
	llmAuditorAgent := GetLLmAuditorAgent(ctx)

	sessionService := session.InMemoryService()
	config := runner.Config{
		AppName:        "llm_auditor",
		Agent:          llmAuditorAgent,
		SessionService: sessionService,
	}
	r, err := runner.New(config)
	if err != nil {
		t.Fatal(err)
	}

	s, err := sessionService.Create(ctx, &session.CreateRequest{
		AppName: "llm_auditor",
		UserID:  "test_user",
	})
	if err != nil {
		t.Fatal(err)
	}

	userInput := `Double check this:
Question: Why is the sky blue?
Answer: Because the water is blue.`

	userMsg := &genai.Content{
		Parts: []*genai.Part{genai.NewPartFromText(userInput)},
		Role:  string(genai.RoleUser),
	}

	var response string
	for event, err := range r.Run(ctx, "test_user", s.Session.ID(), userMsg, agent.RunConfig{}) {
		if err != nil {
			t.Fatal(err)
		}
		if event.ErrorCode != "" {
			t.Fatalf("Event error: %s - %s", event.ErrorCode, event.ErrorMessage)
		}
		if event.Content != nil && len(event.Content.Parts) > 0 {
			response += event.Content.Parts[0].Text
		}
	}

	if !strings.Contains(strings.ToLower(response), "scattering") {
		t.Errorf("Expected response to contain 'scattering', but it didn't. Response: %s", response)
	}
}
