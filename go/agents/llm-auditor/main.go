// limitations under the License.

package main

import (
	"context"
	"fmt"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/artifact"
	"google.golang.org/adk/cmd/launcher/adk"
	"google.golang.org/adk/cmd/launcher/web"
	"google.golang.org/adk/cmd/restapi/services"
	"google.golang.org/adk/session"
)

func main() {
	ctx := context.Background()
	llmAuditorAgent := GetLLmAuditorAgent(ctx)

	sessionService := session.InMemoryService()
	artifactservice := artifact.InMemoryService()

	agentLoader := services.NewStaticAgentLoader(
		llmAuditorAgent,
		map[string]agent.Agent{
			"llm_auditor": llmAuditorAgent,
		},
	)

	webConfig, _, _ := web.ParseArgs([]string{})
	fmt.Println(webConfig)
	web.Serve(webConfig, &adk.Config{
		SessionService:  sessionService,
		AgentLoader:     agentLoader,
		ArtifactService: artifactservice,
	})
}
