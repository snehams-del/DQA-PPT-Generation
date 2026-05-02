# Google Agent CLI Recipe: Retail Product Search

A production-ready retail agent built with ADK that combines semantic product search with virtual try-on, recommendations, and content generation on Google Cloud.

**One foundation, three revenue levers** -- semantic product search at the base, with virtual try-on, recommendations, and content generation layered on top.

## Features

| Capability | Description | Model |
|-----------|-------------|-------|
| **Product Search** | Semantic search with Vector Search 2.0 + BigQuery | gemini-2.5-flash |
| **Virtual Try-On** | Overlay clothing on user photos | virtual-try-on-001 (Imagen) |
| **Recommendations** | "You might also like" via collaborative/content-based/LLM | gemini-2.5-flash |
| **Content Generation** | Product descriptions, SEO, marketing copy | gemini-2.5-flash |
| **Voice** | Native audio via Gemini Live API | gemini-live-2.5-flash-native-audio |

## Prerequisites

- Python 3.10+
- Google Cloud project with Vertex AI + BigQuery APIs enabled
- `gcloud auth application-default login`

## Quick Start

### 1. Set up environment

```bash
cd python/agents/google-agent-cli-recipe
cp .env.example .env
# Edit .env and set GOOGLE_CLOUD_PROJECT
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Ingest sample data

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
python deployment/setup.py --config data/design-spec.md
```

This validates sample products, loads them into BigQuery, and creates a Vector Search index (~2-5 minutes).

### 4. Run the agent

```bash
adk web .
```

Open http://localhost:8000 and try:

```
show me products under $100
do you have any keyboards?
do you sell cars?
```

### Voice Mode

```bash
ENABLE_VOICE=true adk web .
```

Uses `gemini-live-2.5-flash-native-audio` for real-time voice interaction.

### Virtual Try-On Setup (Optional)

```bash
python deployment/setup_tryon.py --config data/design-spec.md --project-id $GOOGLE_CLOUD_PROJECT
```

Then set the env vars printed by the script and restart the agent. Try:

```
I want to try on product prod-001, my photo is at gs://your-bucket/photo.jpg
```

## Architecture

```
User query
    |
    v
root_agent (gemini-2.5-flash / gemini-live for voice)
    |-- retrieve_docs tool --> Vector Search 2.0 Collection
    |                          (auto-embedded, no manual embedding needed)
    |-- try_on_product tool --> virtual-try-on-001 (Imagen VTO)
    |                           or gemini-*-image (text-prompted variations)
    v
Response with product data / try-on image / recommendations / content
```

## Sample Data

The agent ships with 5 sample products in `data/sample-products.csv`:

| Product | Price | Brand | Category |
|---------|-------|-------|----------|
| Wireless Headphones | $199.99 | Sony | Audio |
| Laptop Stand | $49.99 | Generic | Accessories |
| USB-C Cable | $19.99 | Anker | Cables |
| Mechanical Keyboard | $129.99 | Keychron | Peripherals |
| Monitor Light Bar | $59.99 | BenQ | Lighting |

## Evaluation

```bash
# Run eval suite
python -m pytest tests/ -v

# Or use the eval runner
python eval/run.py --skill retail-product-search --project-id $GOOGLE_CLOUD_PROJECT
```

## Cleanup

Delete GCP resources when done:

```bash
# BigQuery
bq rm -r -f $GOOGLE_CLOUD_PROJECT:products_dataset

# GCS buckets (if VTO was set up)
gcloud storage rm -r gs://$GOOGLE_CLOUD_PROJECT-tryon-output
gcloud storage rm -r gs://$GOOGLE_CLOUD_PROJECT-tryon-uploads
```

## License

Apache 2.0
