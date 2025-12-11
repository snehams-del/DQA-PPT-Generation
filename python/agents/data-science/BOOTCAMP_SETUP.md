# AI Data Bootcamp - Data Science Agent Setup Guide

## Overview

This simplified version of Google's ADK Data Science Agent demonstrates how AI can help non-technical users analyze data using natural language. Perfect for teaching freelancers and SME staff data analysis without requiring SQL or Python knowledge.

## What This Agent Does

The bootcamp agent includes three powerful capabilities:

### 1. **NL2SQL (Natural Language to SQL)**
Ask questions in plain English and get answers from your BigQuery database:
- "What countries are in the dataset?"
- "Show me total sales by country"
- "Which store had the highest sales in Canada?"

### 2. **BQML (BigQuery Machine Learning)**
Train and use ML models with natural language:
- "Train a forecasting model to predict sticker sales"
- "What model types can I use for time series forecasting?"
- "Evaluate my model's performance"

### 3. **Code Interpreter (Data Visualization)**
Generate Python visualizations and statistical analysis:
- "Create a bar chart of total sales per country"
- "Show me a time series plot of sales trends"
- "Generate summary statistics for the dataset"

## Simplified Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ROOT AGENT                           │
│         (Orchestrates all sub-agents)                   │
└────────────┬────────────────────────────────────────────┘
             │
             ├──────────────────┬──────────────────┬
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │ BigQuery Agent │ │  BQML Agent    │ │Analytics Agent │
    │   (NL2SQL)     │ │  (ML Models)   │ │ (Visualizations│
    └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
             │                  │                  │
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │   BigQuery     │ │  BigQuery ML   │ │ Vertex AI Code │
    │   Database     │ │   (BQML)       │ │  Interpreter   │
    └────────────────┘ └────────────────┘ └────────────────┘
```

### Key Components:

- **Root Agent**: Receives user questions and delegates to appropriate sub-agents
- **BigQuery Agent**: Converts natural language to SQL queries
- **BQML Agent**: Handles machine learning tasks (forecasting, classification, clustering)
- **Analytics Agent**: Generates Python code for visualizations and statistical analysis

### What We Removed:
- ❌ AlloyDB support (simplified to BigQuery-only)
- ❌ MCP Toolbox for Databases (not needed for BigQuery)
- ❌ Cross-dataset joins (single dataset is simpler for learning)

## Prerequisites

### Required:
- Google Cloud account with billing enabled
- Python 3.12+ installed
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- Git installed

### Google Cloud APIs to Enable:
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com
```

## Setup Instructions

### Step 1: Configure Your Environment

1. **Edit the `.env` file** that was just created in `python/agents/data-science/.env`

2. **Replace the following values** with your Google Cloud information:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1  # or your preferred region

   BQ_COMPUTE_PROJECT_ID=your-actual-project-id
   BQ_DATA_PROJECT_ID=your-actual-project-id
   ```

3. **Leave these empty** for now (will be auto-populated):
   ```bash
   BQML_RAG_CORPUS_NAME=
   CODE_INTERPRETER_EXTENSION_NAME=
   ```

### Step 2: Install Dependencies

From the `python/agents/data-science` directory:

```bash
# Install all dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

### Step 3: Set Up BigQuery Dataset

Load the sample "forecasting_sticker_sales" dataset:

```bash
# This creates the dataset and loads sample data
python3 data_science/utils/create_bq_table.py
```

This dataset includes:
- **train table**: Historical sticker sales data by country, store, and product
- **test table**: Data for testing forecasting models

### Step 4: Set Up BQML RAG Corpus

The BQML agent needs access to BigQuery ML documentation:

```bash
# Create RAG corpus and ingest BQML reference documentation
python3 data_science/utils/reference_guide_RAG.py
```

**Important**: After this runs successfully, it will output a corpus name like:
```
projects/YOUR_PROJECT/locations/us-central1/ragCorpora/123456789
```

Copy this value and add it to your `.env` file:
```bash
BQML_RAG_CORPUS_NAME='projects/YOUR_PROJECT/locations/us-central1/ragCorpora/123456789'
```

### Step 5: Code Interpreter Setup

The Code Interpreter extension will be created automatically on first run, but you can check the logs for the extension ID and add it to `.env` to avoid creating duplicates:

```
CODE_INTERPRETER_EXTENSION_NAME='projects/YOUR_PROJECT/locations/YOUR_LOCATION/extensions/YOUR_EXTENSION_ID'
```

## Running the Agent

### Option 1: ADK Web UI (Recommended for Bootcamp)

```bash
uv run adk web
```

Then:
1. Open your browser to the URL shown (usually http://localhost:8000)
2. Select "data_science" from the dropdown
3. Start asking questions!

### Option 2: Command Line Interface

```bash
uv run adk run data_science
```

## Bootcamp Demonstration Queries

### Level 1: Basic Data Exploration (NL2SQL)

```
1. "Hi! What data do you have access to?"
2. "What countries are in the dataset?"
3. "How many stores are in each country?"
4. "Show me total sales per country"
5. "Which store had the highest sales?"
```

### Level 2: Data Visualization (Code Interpreter)

```
1. "Create a bar chart showing total sales by country"
2. "Generate a time series plot of daily sales"
3. "Show me a breakdown of sales by product type"
4. "Create summary statistics for the train table"
```

### Level 3: Machine Learning (BQML)

```
1. "What types of forecasting models can I train in BQML?"
2. "Train an ARIMA model to forecast sticker sales by country"
3. "Evaluate my forecasting model's performance"
4. "Use the model to predict next month's sales"
```

### Level 4: Combined Workflows

```
1. "Analyze sales trends by country and create a visualization"
2. "Train a forecasting model and show me the predictions as a chart"
3. "Compare actual vs predicted sales visually"
```

## Bootcamp Learning Objectives

By using this agent, learners will understand:

1. **Natural Language Interfaces**: How AI can translate human language to database queries
2. **Automated Data Analysis**: How AI generates Python code for visualizations
3. **Accessible Machine Learning**: How to train ML models without coding
4. **Multi-Agent Systems**: How specialized agents work together to solve complex tasks

## Configuration Options

### NL2SQL Methods

You can switch between two methods for generating SQL queries:

```bash
# In .env file:
BQ_NL2SQL_METHOD="BASELINE"  # Uses Gemini directly (simpler, faster)
# or
BQ_NL2SQL_METHOD="CHASE"     # Uses CHASE-SQL method (more accurate for complex queries)
```

For bootcamp demonstrations, `BASELINE` is recommended.

### Model Selection

All agents use `gemini-2.5-pro` by default. You can change individual agent models in the `.env` file if needed.

## Troubleshooting

### Common Issues:

**"500 Internal Server Error"**
- Simply re-run your last command. This is usually a temporary issue.

**"Permission denied" errors**
- Ensure you've enabled the required Google Cloud APIs
- Check that your Google Cloud credentials are configured: `gcloud auth application-default login`

**"Dataset not found"**
- Make sure you ran `python3 data_science/utils/create_bq_table.py` successfully
- Verify the dataset exists in BigQuery console

**BQML queries failing**
- Ensure you've set up the RAG corpus with `python3 data_science/utils/reference_guide_RAG.py`
- Check that `BQML_RAG_CORPUS_NAME` is set in your `.env` file

**Code Interpreter not working**
- Check the logs for the extension ID on first run
- Add it to `.env` to prevent creating multiple extensions

## Next Steps

### For Bootcamp Delivery:
1. Test all demonstration queries before your session
2. Prepare backup examples in case of API issues
3. Consider recording successful interactions for offline playback
4. Have the BigQuery console open to show the underlying data

### For Further Customization:
1. Add your own datasets (see `forecasting_sticker_sales_dataset_config.json` for format)
2. Customize prompts in `data_science/prompts.py` for your audience
3. Create custom example queries specific to your industry
4. Deploy to Cloud Run for live, always-available demonstrations

## Deployment (Optional)

Once you're comfortable with the agent locally, you can deploy it to Cloud Run for live demonstrations:

```bash
gcloud run deploy data-science-agent \
  --source . \
  --port 8080 \
  --memory 2G \
  --project $GOOGLE_CLOUD_PROJECT \
  --allow-unauthenticated \
  --region us-central1
```

See the main README.md for full deployment instructions.

## Key Files Reference

- **`.env`**: Your configuration (NEVER commit this to Git!)
- **`forecasting_sticker_sales_dataset_config.json`**: Dataset configuration
- **`data_science/agent.py`**: Root agent definition
- **`data_science/sub_agents/`**: Individual agent implementations
- **`data_science/prompts.py`**: Agent instructions (customize for your audience)

## Resources

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Video Walkthrough**: https://youtu.be/efcUXoMX818
- **Original Sample**: https://github.com/google/adk-samples/tree/main/python/agents/data-science
- **BigQuery ML Guide**: https://cloud.google.com/bigquery/docs/bqml-introduction

## Support

For bootcamp-specific questions or customization help, refer back to this guide and the main README.md.

---

**Ready to start?** Follow the setup steps above and try your first query! 🚀
