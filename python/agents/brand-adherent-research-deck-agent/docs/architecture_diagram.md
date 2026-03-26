# Presentation Expert Agent - Architecture Diagram

This document illustrates the high-level multi-agent architecture of the Presentation Expert Agent. It highlights the unified data model, enterprise-grade state persistence, and advanced layout safety mapping.

```mermaid
graph TD
    %% User Interaction & Security Layer
    User((User)) <-->|Prompt, Approval, & Edits| ModelArmor{Google Cloud\nModel Armor\nSecurity Interceptor}
    ModelArmor <-->|Sanitized I/O| Orchestrator[Orchestrator Agent\nGemini 2.5 Flash\nSelf-Correction Logic]
    
    %% Persistence Layer (The "Memory" of the Stateless Agent)
    Orchestrator <-->|Save/Load State| ArtifactStore[[ADK Artifact Store\nPersistent JSON Storage]]
    ArtifactStore -.->|Turn-to-Turn Continuity| ArtifactStore

    %% Phase 1: Research & Strategy
    subgraph Phase 1: Context & Research
        Orchestrator -->|Internal IP| RAG[Internal RAG Agent]
        RAG -.->|Retrieval| VertexSearch[(Vertex AI Search)]
        
        Orchestrator -->|Fast Fact Lookup| FastSearch[Google Search Tool]
        Orchestrator -->|Complex Analysis| DeepResearch[Deep Research Agent]
    end
    
    %% Phase 2: Dual Workflow Execution
    subgraph Phase 2: Dual Workflow Execution
        %% Create Workflow
        Orchestrator -->|Workflow 1: Create| OutlineAgent[Outline Specialist Agent]
        OutlineAgent -->|Unified 'slides' Array| ArtifactStore
        
        Orchestrator -->|Generate Approved Plan| BatchWriter[Batch Slide Writer Tool\nasyncio Parallel Execution]
        BatchWriter -->|Concurrent Slide Generation| SlideWriter[Slide Writer Agents]
        SlideWriter -->|Professional Bullets| ArtifactStore
        
        %% Edit Workflow
        Orchestrator -->|Workflow 2: Edit| PPTXEditor[Surgical Editor Tools\nadd, delete, replace, layout]
        PPTXEditor --> ArtifactStore
    end
    
    %% Phase 3: Assembly & Rendering
    subgraph Phase 3: Rendering & Delivery
        PPTXEngine[Python-PPTX Engine]
        
        ArtifactStore -->|Final DeckSpec| PPTXEngine
        PPTXEngine -.->|Smart Layout Mapping| LayoutSafe{Anti-Squeeze\nLogic Mapping}
        LayoutSafe -->|Forced Image Box| PPTXEngine
        
        PPTXEngine -.->|Fetch Template| Template[(User / Default GCS)]
        PPTXEngine -.->|Generate Visuals| Imagen[Imagen 3 Model]
        Imagen -->|Hybrid Path| GCSBackup[(GCS Backup)]
    end
    
    %% Delivery
    PPTXEngine -->|application/octet-stream| User
    ArtifactStore -->|Reference| User

    %% Styling
    classDef agent fill:#f9f0ff,stroke:#6a1b9a,stroke-width:2px;
    classDef storage fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef system fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef security fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px;
    
    class Orchestrator,RAG,FastSearch,DeepResearch,OutlineAgent,SlideWriter agent;
    class VertexSearch,Template,GCSBackup storage;
    class ArtifactStore,PPTXEditor,PPTXEngine,Imagen,BatchWriter system;
    class ModelArmor security;
```

### Architectural Highlights

1. **Stateless State Persistence:** Unlike standard agents that rely on ephemeral memory, this agent uses the **ADK Artifact Store** to persist its state as physical JSON files. This ensures that a 15-slide presentation survives cloud worker node rotations and turn-to-turn transitions.
2. **Unified Data Model (`slides`):** To prevent model confusion and "Malformed Function Call" errors, the entire system uses a single consistent data structure. The same `SlideSpec` model is used for planning (focus instruction) and final output (professional bullets).
3. **Enterprise Security (Model Armor):** All incoming user prompts and outgoing LLM responses pass through asynchronous interceptors (`model_armor.py`). This guarantees fail-closed protection against prompt injections.
4. **Anti-Squeeze Layout Safety:** The rendering engine features a **Smart Layout Guard**. It automatically overrides "squeezed" layout requests (like "Title and Chart") and remaps them to professional alternatives (like "Title and Image") to physically guarantee high-quality visual spacing.
5. **Self-Correction Protocol:** The Orchestrator is equipped with a **3-retry Self-Correction loop**. If a tool call fails due to syntax or network stale connections, the agent autonomously reflects on the error and retries the call with corrected parameters.
6. **Parallel Content Generation:** Latency is minimized by offloading synthesis to the `batch_slide_writer_tool`, which utilizes Python's `asyncio.gather` to generate content for an entire deck concurrently.
