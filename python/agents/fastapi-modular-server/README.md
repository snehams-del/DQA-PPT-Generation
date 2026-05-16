# 🚀 Google ADK FastAPI Modular Server

A **production-ready template** for extending Google's Agent Development Kit (ADK) with custom FastAPI endpoints, optimized SSE streaming, and modular architecture patterns.

## 🎯 Purpose & Value

The **FastAPI Modular Server** serves as a **template and reference implementation** for teams who want to:

- **Extend ADK's built-in server** without modifying core behavior
- **Accelerate production deployment** with battle-tested patterns
- **Add custom business logic** through modular router systems
- **Enable hot-reload capabilities** for faster development cycles

## ✨ Key Features

### 🔧 **Modular Router Architecture**
- Clean separation of concerns with dedicated router classes
- Easy to add new endpoints without touching core server code

### ⚡ **Optimized SSE Streaming**
- **3 optimization levels** for different use cases:
  - `MINIMAL`: Essential content only (author + text)
  - `BALANCED`: Core data with invocation tracking
  - `FULL_COMPAT`: Complete ADK event compatibility
- Reduced payload sizes for improved performance
- Custom event filtering and mapping

### 🔄 **Hot-Reload Development**
- Automatic agent reloading on file changes
- File system monitoring with `watchdog`
- Development-friendly with production stability


## 📁 Project Structure

```
fastapi_modular_server/
├── .env.example                 # Environment variables template
├── README.md                    # Project documentation
├── __init__.py                  # Package initialization
├── app/                         # Main application directory
│   ├── __init__.py              # App package initialization
│   ├── agents/                  # Agent definitions
│   │   └── greetings_agent/     # Greetings agent module
│   │       ├── __init__.py      # Agent package init
│   │       └── greetings_agent.py         # Greetings agent implementation
│   ├── api/                     # API layer
│   │   ├── __init__.py          # API package init
│   │   ├── routers/             # API route definitions
│   │   │   ├── __init__.py      # Routers package init
│   │   │   └── agent_router.py         # Agent-related API routes
│   │   └── custom_adk_server.py            # FastAPI server configuration
│   ├── config/                  # Configuration management
│   │   └── settings.py          # Application settings
│   ├── core/                    # Core application components
│   │   ├── __init__.py          # Core package init
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── logging.py           # Logging configuration
│   │   └── mapping/             # Data mapping utilities
│   │       ├── __init__.py      # Mapping package init
│   │       └── sse_event_mapper.py    # Server-Sent Events mapper
│   └── models/                  # Data models
│       ├── __init__.py          # Models package init
│       └── streaming_request.py         # Streaming data models
└── main.py                      # Application entry point
```

## 🚀 Quick Start

### 1. **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
vim .env

# Set the API KEY

```

### 2. **Run the Server**
```bash
# Development mode with hot-reload
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8881
```

### 3. **Test SSE Streaming**

Test the streaming endpoint with a minimal curl command:

```bash
curl -X POST http://localhost:8881/run_sse \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "appName": "greetings_agent",
    "userId": "user",
    "sessionId": "test-session",
    "newMessage": {"role": "user", "parts": [{"text": "Hello!"}]},
    "streaming": true,
    "optimization_level": "minimal"
  }'
```

**Request Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `appName` | ✅ | Agent name (folder name in `app/agents/`) |
| `userId` | ✅ | User identifier |
| `sessionId` | ✅ | Session identifier |
| `newMessage` | ✅ | Message object with `role` and `parts` array |
| `streaming` | ❌ | Enable SSE streaming (default: `false`) |
| `optimization_level` | ❌ | `minimal`, `balanced`, or `full_compat` (default: `full_compat`) |


## 🔧 Customization Guide

### **Adding New Routers**

Create a new router following the established pattern:

```python
# app/api/routers/my_custom_router.py
from fastapi import APIRouter, Depends
from app.core.dependencies import ADKServices, get_adk_services

class MyCustomRouter:
    def __init__(self, web_server_instance):
        self.web_server = web_server_instance
        self.router = APIRouter(prefix="/custom", tags=["Custom"])
        self._setup_routes()
    
    def _setup_routes(self):
        @self.router.get("/endpoint")
        async def my_endpoint(
        ):
            # Access any ADK service
            sessions = await self.web_server.session_service.list_sessions()
            return {"data": "custom response", "session_count": len(sessions)}
    
    def get_router(self) -> APIRouter:
        return self.router
```

Register it in the custom server:

```python
# In app/api/custom_adk_server.py - CustomAdkWebServer class
def _initialize_routers(self):
    try:
        self.agent_router = AgentRouter(self)
        self.my_custom_router = MyCustomRouter(self)  # Add this
        logger.info("All routers initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize routers: {e}", exc_info=True)

def _register_modular_routers(self, app: FastAPI):
    # ... existing code ...
    
    if self.my_custom_router:
        app.include_router(self.my_custom_router.get_router())
        logger.info("Registered MyCustomRouter.")
```

### **Overriding ADK Endpoints**

#### **Method 1: Route Removal (Current Approach)**

```python
def _register_modular_routers(self, app: FastAPI):
    # Remove specific ADK routes
    routes_to_remove = []
    for route in app.routes:
        if route.path in [
            "/run_sse", 
            # You could add additional ADK routes here if you want to override them,
            # e.g., "/apps/{app_name}/users/{user_id}/sessions"
        ] and hasattr(route, 'methods') and 'POST' in route.methods:
            routes_to_remove.append(route)
    
    # Remove the routes
    for route in routes_to_remove:
        app.routes.remove(route)
```

#### **Method 2: Middleware Interception**

For more complex overrides, use middleware:

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RouteOverrideMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Intercept specific routes
        if request.url.path == "/run_sse" and request.method == "POST":
            # Handle with custom logic
            return await self.handle_custom_sse(request)
        
        return await call_next(request)
```

### **Accessing ADK Services and Runners**

#### **From Router Classes**
```python
class AgentRouter:
    def __init__(self, web_server_instance):
        self.web_server = web_server_instance
        
    async def my_endpoint(self, adk_services: ADKServices = Depends(get_adk_services)):
        # Access services
        agents = self.web_server.agent_loader.list_agents()
        session = await self.web_server.session_service.list_sessions()
        
        # Access runners through web server
         runner = await self.web_server.get_runner_async("your_app_name")
        
        # Access other web server properties
        runners_cache = self.web_server.runners_to_clean
```

### **Optimizing SSE Streaming**

#### **Custom Event Filtering**

Extend the SSE mapper for more sophisticated filtering:

```python
# app/models/streaming_request.py
class OptimizationLevel(str, Enum):
  """Enumeration for the available SSE optimization levels."""

  MINIMAL = "minimal"
  BALANCED = "balanced"
  FULL_COMPAT = "full_compat"
  ULTRA_MINIMAL = "ultra_minimal"

# app/core/mapping/sse_mapper.py
class AdvancedSSEEventMapper(SSEEventMapper):
    def map_event_to_sse_message(self, event: Event, optimization_level: OptimizationLevel) -> Optional[str]:
        # Custom filtering logic
        if self._should_skip_event(event):
            return None
            
        # Custom payload creation
        payload = self._create_custom_payload(event, optimization_level)
        
        # Custom serialization
        return self._serialize_payload(payload)
    
    def _should_skip_event(self, event: Event) -> bool:
        # Skip system events, debug events, empty events, etc.
        if event.author in ["system", "debug"]:
            return True
        if not event.content or not event.content.parts:
            return True
        return False
    
    def _create_custom_payload(self, event: Event, level: OptimizationLevel) -> Dict:
        if level == OptimizationLevel.ULTRA_MINIMAL:
            # Even more minimal than minimal
            return {"t": self._extract_text_only(event)}
        
        return super()._create_minimal_payload(event)
```

## 🤝 Contributing

This template is designed to be extended and customized for your specific needs. Key extension points:

1. **Router Classes**: Add domain-specific endpoints
2. **SSE Mappers**: Custom event processing and optimization
3. **Middleware**: Cross-cutting concerns
4. **Services**: Additional business logic services
5. **Configuration**: Environment-specific settings

## 📚 Further Resources

- **Google ADK Documentation**: https://google.github.io/adk-docs/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
