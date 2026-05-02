---
name: retail-product-search
description: >-
  Creates product search agents with semantic search, RAG, and voice on Google
  Cloud (Vertex AI Vector Search, BigQuery, embeddings). Use when building
  e-commerce search, catalog discovery, or shopping assistant agents. Handles
  data ingestion, multi-agent orchestration, evaluation, and deployment.
deps:
  - source: agents-cli
    type: cli
---

# Product Search Agent

Creates product search agents with semantic search, RAG, and optional voice
on Google Cloud. Guides the user conversationally through setup -- ask
questions progressively, not all upfront.

## Execution Rules

Follow these rules strictly when executing this skill:

1. **Execute steps in order.** Do NOT jump ahead or skip steps.
2. **Verify each step succeeded** before moving to the next. If a command
   fails, stop and tell the user -- do NOT proceed.
3. **Wait for user answers.** Ask one question at a time. Do NOT assume
   defaults without confirming with the user.
4. **Do NOT use `agents-cli data-ingestion`.** Use the retail skill scripts
   in `scripts/` instead.
5. **Copy scripts into the project** immediately after scaffolding (Step 7).
   The project is NOT ready until scripts and design-spec.md are copied.
7. **Save all answers to `assets/design-spec.md`** as you collect them.
   After the interview, run `python scripts/setup.py --config assets/design-spec.md`
   to execute the full pipeline. The setup script reads the design-spec and
   runs only the steps that match the user's choices.
6. **Confirm completion** of each step with the user before proceeding:
   "Step N is done. Ready for Step N+1?"

## When to Use

- Building **e-commerce product search** or **shopping assistant** agents
- Implementing **semantic catalog discovery** with natural language queries
- Adding **voice-based product search** (Gemini Live)

Do NOT use for generic document search (use ADK `agentic_rag`), simple keyword
search, or non-retail domains.

## Step 1: Understand the Product Domain

Ask these one at a time. Wait for answers before proceeding.

**Q1. Industry and project name**
Ask what products are searchable and what industry. Default: General Retail.
Project name defaults to `{industry}-search`.

**Q2. Product fields level**
Default: Standard (product_id, name, price, description, category, brand, image_url).
Extended adds rating, stock, manufacturer. Full adds variants, tags, specs, reviews.

**Q3. Searchable vs. filterable fields**
Free-text search fields (default: `name, description`) vs exact-match filters
(default: `brand, category`).

**Q4. Price config**
Default: decimal prices, USD.

**Q5. Variants**
Default: No.

## Step 2: Gate Question -- Search Architecture

Ask: "Do you have an existing product search API on GCP, or build from scratch?"

- **Yes** -> Path A (API integration)
- **No** (default) -> Path B (database + vector search)
- **Both** -> Path B then Path A

### Path A: API Integration

Only if user has an existing API. Ask progressively.

| # | Question | Default |
|---|----------|---------|
| A1 | API base URL? | (required) |
| A2 | Auth method? | Google OAuth |
| A3 | Search endpoint + HTTP method? | `GET /products/search` |
| A4 | Query parameters? | `q, category, brand, price_min, price_max, sort, page, limit` |
| A5 | Pagination? | `page + limit` |
| A6 | Supports vector search natively? | No |
| A7 | Zero results format? | Empty array with `total: 0` |
| A8 | Error handling? | Retry once with backoff |
| A9 | Rate limit? | Unknown |
| A10 | Cloud Logging? | Yes |
| A11 | Excluded categories? | None |

### Path B: Database + Vector Search

Only if building from scratch. Ask progressively.

| # | Question | Default |
|---|----------|---------|
| B1 | GCP database? | BigQuery |
| B2 | Catalog size? | 1K-50K. 500K+ may need Dataflow. |
| B3 | Catalog change frequency? | Daily (Cloud Scheduler) |
| B4 | Product images? | No images. If yes: ask about visual search + images per product. |
| B5 | Text-only or multimodal? | Text only |
| B6 | Fields to embed? | `name, description, category, brand` |
| B7 | Index update mode? | Batch (scheduled rebuild) |
| B8 | Embedding model? | `gemini-embedding-001` (auto-embedded by VS 2.0). |
| B9 | GCP region? | `us-central1` |
| B10 | Filter strategy? | Pre-filter (Vertex AI metadata) |
| B11 | Deletion handling? | Hard delete from index |
| B12 | Vector DB? | Vertex AI Vector Search |

## Step 3: Search Behavior

| # | Question | Default |
|---|----------|---------|
| S1 | Vague query handling? | Ask 1-2 clarifying questions |
| S2 | Priority filters for clarification? | Price range, Category, Brand |
| S3 | Sort order? | Relevance (similarity score) |
| S4 | Show out-of-stock? | No -- filter via Vertex AI metadata |
| S5 | Multi-language? | No |
| S6 | Remember filters across turns? | Yes |

## Step 4: UI and Rendering

| # | Question | Default |
|---|----------|---------|
| U1 | UI delivery? | Cloud Run web app |
| U2 | Result card fields? | image, price, name, description, stock badge, rating, add-to-cart |
| U3 | Results per page? | 6 |
| U4 | Brand color? | `#4285F4` |
| U5 | Zero results fallback? | Vertex AI ANN fallback (widen search radius) |

## Step 5: Post-Search Actions

| # | Question | Default |
|---|----------|---------|
| P1 | Add to Cart action? | Redirect to product URL |
| P2 | Proactive recommendations? | No |
| P3 | Logged-in user? | No -- anonymous session |
| P4 | Voice capabilities? | No |

## Step 6: GCP Configuration

| # | Question | Default |
|---|----------|---------|
| G1 | GCP project ID? | (required) |
| G2 | Billing confirmed? | Yes |
| G3 | GCP region? (if not set in Path B) | `us-central1` |

## Step 7: Scaffold the Project

```bash
agents-cli init \
  --agent-type agentic_rag \
  --datastore vertex_ai_vector_search \
  --deployment-target cloud_run \
  --prototype \
  -y
```

Deployment target mapping: CLI -> `none`, Web UI -> `cloud_run`,
Voice -> `agent_engine`, Custom API -> `cloud_run`.

**⚠️ CRITICAL -- DO THIS IMMEDIATELY AFTER SCAFFOLDING. DO NOT PROCEED TO ANY OTHER STEP UNTIL DONE.**

You MUST copy the retail skill scripts and assets into the project RIGHT NOW.
Failure to do this will cause the agent to return generic AI answers instead
of actual product data.

**DO NOT run `agents-cli data-ingestion`.** It creates a generic document
pipeline that is incompatible with product catalogs. The retail skill scripts
below are the ONLY correct way to ingest product data.

Run these commands right after `agents-cli init`:

```bash
# REQUIRED: Copy retail scripts and sample data into the scaffolded project
mkdir -p {project_name}/scripts {project_name}/data
cp samples/retail-product-search/scripts/*.py {project_name}/scripts/
cp samples/retail-product-search/assets/design-spec.md {project_name}/design-spec.md
cp samples/retail-product-search/assets/sample-products.csv {project_name}/data/
```

If the skill files are installed globally, use the GEMINI.md directory as the source path.

Then customize the agent code:
1. Rewrite `app/agent.py` -- see [agent-example.md](references/agent-example.md)
2. Rewrite `app/retrievers.py` with product-specific fields
3. If Path A (existing API): configure `scripts/api_connector.py` with your API details
4. Add Pub/Sub sync if real-time -- see `scripts/pubsub_sync.py`
5. Add audio layer if voice -- see [audio-integration.md](references/audio-integration.md)

After copying, the project structure MUST look like this:

```text
{project_name}/
  design-spec.md             # REQUIRED: source of truth (from assets/)
  app/
    agent.py              # Customized search agent
    retrievers.py         # Vector Search retrieval
    audio/                # (conditional: voice)
  scripts/
    ingest_bigquery.py    # REQUIRED: from retail skill scripts/
    ingest_gcs.py         # From retail skill (multimodal only)
    ingest_vertex_search.py  # REQUIRED: from retail skill scripts/
    validate_schema.py    # REQUIRED: from retail skill scripts/
    api_connector.py      # From retail skill (Path A only)
    cleanup.py            # From retail skill scripts/
  data/
    sample-products.csv   # REQUIRED: from retail skill assets/
  # evalset lives at repo root: evals/sets/retail-product-search.evalset.json
  deployment/terraform/dev/
    products.tf
```

## Step 8: Configure and Ingest Data

**⚠️ DO NOT use `agents-cli data-ingestion`. It runs a generic document
pipeline that is INCOMPATIBLE with product catalogs. Use the retail skill
scripts below -- they are the ONLY correct ingestion method.**

First, set the GCP project ID in design-spec.md:

```bash
cd {project_name}

# Set your GCP project ID (REQUIRED before running any script)
# Edit design-spec.md and replace the empty gcp_project_id with your project
# Example: gcp_project_id: "my-gcp-project-123"
```

Then run these commands in order. Do NOT skip any step:

```bash
# Step 8a: Validate sample data (MUST pass before ingestion)
python scripts/validate_schema.py --file data/sample-products.csv --fields-level Extended

# Step 8b: Load products into BigQuery
python scripts/ingest_bigquery.py --config design-spec.md --local-file data/sample-products.csv

# Step 8c: Create Vector Search 2.0 Collection and ingest products (2-5 min)
# This creates a Collection with auto-embeddings and inserts all products.
# No manual embedding generation needed -- VS 2.0 handles it automatically.
python scripts/ingest_vertex_search.py --config design-spec.md
```

After Step 8c completes, set the `VECTOR_SEARCH_COLLECTION` environment
variable in your agent to the collection path printed by the script:

```bash
export VECTOR_SEARCH_COLLECTION="projects/$PROJECT_ID/locations/us-central1/collections/products-collection"
```

## Step 9: Test

```bash
adk web .
```

Test queries:
1. `"wireless headphones under $100"` -- price filter
2. `"I need a gift"` -- clarification flow
3. `"Which one has the best battery life?"` -- RAG detail
4. `"laptop for video editing"` -- semantic search

## Step 10: Evaluate

```bash
adk eval
```

Expect 5-10+ iterations. See [evaluation-guide.md](references/evaluation-guide.md)
for metrics and methodology.

## Step 11: Deploy

```bash
agents-cli enhance . \
  --deployment-target agent_engine \
  --cicd-runner github_actions \
  -y

make deploy
```

**Never deploy without explicit human approval.**

## Gotchas

- **Vector Search returns no results**: Collection empty or `VECTOR_SEARCH_COLLECTION`
  env var not set. Verify products were ingested by re-running `ingest_vertex_search.py`.
- **BigQuery ingestion fails**: Schema mismatch or missing required fields
  (product_id, name, price). Validate with `scripts/validate_schema.py`.
- **Slow search**: Use `tree_ah` algorithm for >1K products. Increase shard size.
- **Prototype first**: Use `--prototype` flag, add deployment infra later.
- **Real data only**: Don't test with placeholder/lorem ipsum products.
- **Prices are sacred**: Never fabricate or estimate prices.

## Completion Checklist

- [ ] Product domain understood (industry, fields, data source)
- [ ] Search architecture decided (API vs. vector search)
- [ ] Project scaffolded with agents-cli
- [ ] Data ingestion running, Vector Search populated
- [ ] Search + clarification agents working
- [ ] Evaluation passes success criteria
- [ ] Edge cases handled (see [architecture.md](references/architecture.md))
- [ ] Deployed (if beyond prototype)

## References

- [architecture.md](references/architecture.md) -- Multi-agent design, success criteria, edge cases, constraints
- [agent-example.md](references/agent-example.md) -- Example agent.py and retrievers.py
- [audio-integration.md](references/audio-integration.md) -- Voice interface with Gemini Live
- [evaluation-guide.md](references/evaluation-guide.md) -- Eval metrics and methodology
- [ingestion-scripts.md](references/ingestion-scripts.md) -- Detailed script docs
- [terraform-example.md](references/terraform-example.md) -- Example Terraform config
