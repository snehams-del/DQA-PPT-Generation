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
		Parts: []genai.Part{genai.Text(userInput)},
		Role:  string(genai.RoleUser),
	}

	var response string
	for event := range r.Run(ctx, "test_user", s.Session.ID(), userMsg, agent.RunConfig{}) {
		if event.Err != nil {
			t.Fatal(event.Err)
		}
		if event.Content != nil && len(event.Content.Parts) > 0 {
			if text, ok := event.Content.Parts[0].(genai.Text); ok {
				response += string(text)
			}
		}
	}

	if !strings.Contains(strings.ToLower(response), "scattering") {
		t.Errorf("Expected response to contain 'scattering', but it didn't. Response: %s", response)
	}
}
