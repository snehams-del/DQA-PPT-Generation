# Technical Documentation Suite - Advanced ADK Multi-Agent Example

This example demonstrates advanced multi-agent orchestration patterns using Google's Agent Development Kit (ADK). It showcases a production-ready technical documentation generation system that coordinates multiple specialized AI agents to create comprehensive documentation from code repositories.

## Key Features

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent (Orchestrator + 6 Specialized Agents) |
| **Components:**  | AgentTools, Memory, State Management |
| **Vertical:**  | Developer Tools & Documentation |

## Architecture Overview

The system uses an **orchestrator-driven architecture** where a central agent coordinates multiple specialized agents through a structured 6-phase workflow:

```
Technical Documentation Orchestrator
├── Phase 1: Code Analyzer (Repository structure & analysis)
├── Phase 2: Documentation Writer (Content creation)
├── Phase 3: Diagram Generator (Visual representations)
├── Phase 4: Translation Agent (Multi-language support)
├── Phase 5: Quality Assurance (Review & validation)
└── Phase 6: Feedback Collector (User feedback & improvement)
```

### Agent Specialization

Each agent is highly specialized for its specific documentation task:

- **🔍 Code Analyzer**: Extracts code structure, dependencies, and architectural patterns
- **📝 Documentation Writer**: Creates comprehensive technical content with examples
- **📊 Diagram Generator**: Produces Mermaid diagrams and visual architecture representations
- **🌐 Translation Agent**: Provides multi-language documentation support
- **✅ Quality Assurance**: Reviews content for accuracy, completeness, and usability
- **📋 Feedback Collector**: Gathers user feedback and identifies improvement opportunities

## Advanced ADK Patterns Demonstrated

### 1. **Orchestrator-Driven Coordination**
```python
# Main orchestrator uses AgentTools to coordinate specialized agents
root_agent = Agent(
    model="gemini-2.5-flash",
    name="technical_documentation_orchestrator",
    tools=[
        code_analyzer_tool,
        documentation_writer_tool,
        diagram_generator_tool,
        # ... more specialized agent tools
    ],
)
```

### 2. **Structured Output with Pydantic Schemas**
```python
class CodeAnalysisResult(BaseModel):
    repository_url: Optional[str] = None
    primary_language: str
    languages_detected: List[str]
    framework_patterns: List[str]
    # ... comprehensive structured output
```

### 3. **Session State Management**
- Persistent workflow state across agent transitions
- Context preservation between phases
- Error recovery and resumption capabilities

### 4. **Agent Tool Integration**
```python
# Each specialized agent becomes a tool for the orchestrator
code_analyzer_tool = AgentTool(agent=code_analyzer)
documentation_writer_tool = AgentTool(agent=documentation_writer)
```

## Quick Start

### Prerequisites

- Python 3.11+
- Google Agent Development Kit 1.0+ (`pip install google-adk`)
- Google Cloud Project (for Vertex AI) OR Gemini API key
- Poetry (recommended) or pip

### Installation

1. **Clone the ADK samples repository:**
   ```bash
   git clone https://github.com/google/adk-samples.git
   cd adk-samples/python/agents/technical-documentation-suite
   ```

2. **Install dependencies:**
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

   **For Vertex AI (recommended):**
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

   **For Gemini API:**
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=0
   GOOGLE_API_KEY=your-gemini-api-key
   ```

4. **Authenticate (if using Vertex AI):**
   ```bash
   gcloud auth application-default login
   ```

### Basic Usage

#### Using ADK CLI
```bash
# Interactive chat interface
adk run technical_documentation_suite

# Web interface
adk web
```

#### Programmatic Usage
```python
from examples.simple_usage import run_simple_example
run_simple_example()
```

#### Quick Test
```bash
# Run the provided examples
python examples/simple_usage.py
```

## Example Workflows

### 1. **Repository Documentation Generation**
```
User: "Generate comprehensive documentation for https://github.com/example/fastapi-project"

Orchestrator: 
├── Delegates to Code Analyzer → Extracts FastAPI structure, endpoints, models
├── Delegates to Documentation Writer → Creates API docs, user guides, setup instructions  
├── Delegates to Diagram Generator → Produces architecture diagrams
├── Delegates to Quality Assurance → Reviews and validates all content
└── Returns complete documentation package
```

### 2. **Code Snippet Analysis**
```
User: "Analyze this Python code and create quick documentation"

Orchestrator:
├── Code Analyzer → Identifies patterns, dependencies, structure
├── Documentation Writer → Creates concise documentation outline
└── Returns structured analysis and documentation recommendations
```

## Advanced Usage Patterns

### Custom Orchestration Logic
The orchestrator demonstrates sophisticated coordination patterns:

- **Conditional delegation** based on code analysis results
- **State preservation** across agent transitions  
- **Error handling** with graceful degradation
- **Progress tracking** with real-time updates

### Production Deployment Patterns
- **Persistent state management** for long-running workflows
- **Timeout handling** for complex documentation tasks
- **Quality thresholds** and validation checkpoints
- **Multi-format output** (Markdown, HTML, JSON)

## Value for ADK Community

This example provides the ADK ecosystem with:

### **🎯 Production-Ready Patterns**
- Battle-tested orchestration from actual cloud deployment
- Comprehensive error handling and recovery strategies
- State management patterns for complex workflows

### **📚 Educational Value** 
- Progressive examples from simple to advanced patterns
- Clear documentation of ADK best practices
- Reusable components for other multi-agent systems

### **🔧 Practical Applications**
- Real-world documentation automation use case
- Demonstrates ADK's potential for enterprise applications
- Scalable architecture suitable for production deployment

### **🚀 Innovation Showcase**
- Advanced agent specialization techniques
- Sophisticated workflow orchestration
- Integration of multiple AI capabilities

## Testing

### Run Unit Tests
```bash
# Using Poetry
poetry run pytest tests/ -v

# Using pip
python -m pytest tests/ -v
```

### Test Coverage
```bash
poetry run pytest tests/ --cov=technical_documentation_suite --cov-report=html
```

## File Structure

```
technical-documentation-suite/
├── README.md                           # This file
├── pyproject.toml                      # Project configuration
├── .env.example                        # Environment variables template
├── technical_documentation_suite/      # Main package
│   ├── __init__.py                     # Package initialization
│   ├── agent.py                        # Main orchestrator agent
│   ├── prompt.py                       # Agent instructions and prompts
│   └── sub_agents/                     # Specialized agents
│       ├── __init__.py
│       ├── code_analyzer.py            # Repository analysis agent
│       ├── documentation_writer.py     # Content creation agent
│       ├── diagram_generator.py        # Visual diagram agent
│       ├── translation_agent.py        # Multi-language agent
│       ├── quality_assurance.py        # Review and validation agent
│       └── feedback_collector.py       # User feedback agent
├── examples/                           # Usage examples
│   └── simple_usage.py                 # Basic orchestration example
├── tests/                              # Test suite
│   ├── __init__.py
│   └── test_orchestrator.py           # Agent coordination tests
└── deployment/                         # Production deployment configs
```

## Contributing

This example welcomes contributions! Areas for enhancement:

### **Adding New Agents**
1. Create new agent in `sub_agents/` directory
2. Define Pydantic output schema
3. Add to orchestrator's tools list
4. Update documentation and tests

### **Extending Orchestration**
1. Enhance conditional delegation logic
2. Add parallel processing capabilities
3. Implement custom workflow patterns
4. Create domain-specific orchestrators

### **Improving Quality**
1. Add more comprehensive test coverage
2. Enhance error handling and recovery
3. Optimize performance for large repositories
4. Add monitoring and observability

## Performance Considerations

### **Optimization Tips**
- Use structured outputs to minimize token usage
- Implement agent result caching for repeated operations
- Optimize prompts for specific documentation types
- Monitor session state size for large workflows

### **Scaling Guidelines**
- Horizontal scaling via multiple ADK instances
- Database-backed state storage for high availability
- Load balancing for concurrent documentation requests
- Monitoring and alerting for production deployments

## Troubleshooting

### **Common Issues**

1. **Agent timeout errors**
   - Increase timeout settings in environment
   - Break large repositories into smaller chunks
   - Use incremental documentation generation

2. **API rate limits**
   - Implement exponential backoff
   - Use batch processing for multiple files
   - Consider Vertex AI for higher limits

3. **Memory issues with large codebases**
   - Process repositories in segments
   - Implement selective file analysis
   - Use streaming for large outputs

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable ADK debug logging
import os
os.environ["ADK_DEBUG"] = "true"
```

## License

Apache 2.0 License - see [LICENSE](../../LICENSE) file for details.

## Support & Community

- **ADK Documentation**: [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/)
- **GitHub Issues**: [https://github.com/google/adk-samples/issues](https://github.com/google/adk-samples/issues)
- **Community Discussions**: [ADK Community Forum](https://groups.google.com/g/adk-community)

---

**This example demonstrates ADK's full potential for sophisticated AI systems, bridging the gap between simple tutorials and enterprise-grade applications.** 🚀✨ 