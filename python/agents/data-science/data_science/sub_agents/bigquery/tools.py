# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file contains the tools used by the database agent."""

import datetime
from typing import Any

import numpy as np
import pandas as pd
from google.adk.tools import ToolContext
from google.cloud import bigquery
from google.genai import Client

from ...config import get_config
from .chase_sql import chase_constants

config = get_config()

# Use configuration from config module with sensible defaults
dataset_id = config.bq_dataset_id
data_project = config.bq_data_project_id
compute_project = config.bq_compute_project_id
vertex_project = config.project_id
location = config.location
llm_client = Client(vertexai=True, project=vertex_project, location=location)

MAX_NUM_ROWS = 80


def _serialize_value_for_sql(value: Any) -> str:
    """Serializes a Python value from a pandas DataFrame into a BigQuery SQL literal."""
    if pd.isna(value):
        return "NULL"
    if isinstance(value, str):
        # Escape single quotes and backslashes for SQL strings.
        return f"'{value.replace(chr(92), chr(92) * 2).replace(chr(39), chr(39) * 2)}'"
    if isinstance(value, bytes):
        return f"b'{value.decode('utf-8', 'replace').replace(chr(92), chr(92) * 2).replace(chr(39), chr(39) * 2)}'"
    if isinstance(value, datetime.datetime | datetime.date | pd.Timestamp):
        # Timestamps and datetimes need to be quoted.
        return f"'{value}'"
    if isinstance(value, list | np.ndarray):  # type: ignore[unreachable]
        # Format arrays.
        return f"[{', '.join(_serialize_value_for_sql(v) for v in value)}]"
    if isinstance(value, dict):
        # For STRUCT, BQ expects ('val1', 'val2', ...).
        # The values() order from the dataframe should match the column order.
        return f"({', '.join(_serialize_value_for_sql(v) for v in value.values())})"
    return str(value)


database_settings: dict[str, Any] | None = None
bq_client = None


def get_bq_client() -> bigquery.Client:
    """Get BigQuery client."""
    global bq_client
    if bq_client is None:
        bq_client = bigquery.Client(project=config.bq_compute_project_id)
    return bq_client


def get_database_settings() -> dict[str, Any]:
    """Get database settings."""
    global database_settings
    if database_settings is None:
        database_settings = update_database_settings()
    return database_settings


def update_database_settings() -> dict[str, Any]:
    """Update database settings."""
    global database_settings
    ddl_schema = get_bigquery_schema_and_samples(
        dataset_id=config.bq_dataset_id,
        data_project_id=config.bq_data_project_id,
        client=get_bq_client(),
        compute_project_id=config.bq_compute_project_id,
    )
    database_settings = {
        "bq_project_id": config.bq_data_project_id,
        "bq_dataset_id": config.bq_dataset_id,
        "bq_ddl_schema": ddl_schema,
        "bq_schema_and_samples": ddl_schema,
        # Include ChaseSQL-specific constants.
        **chase_constants.chase_sql_constants_dict,
    }
    return database_settings


def get_bigquery_schema_and_samples(
    dataset_id: str,
    data_project_id: str,
    client: bigquery.Client,
    compute_project_id: str,
) -> dict:
    """Retrieves schema and sample values for the BigQuery dataset tables."""
    dataset_ref = bigquery.DatasetReference(data_project_id, dataset_id)
    tables_context = {}
    for table in client.list_tables(dataset_ref):
        table_info = client.get_table(
            bigquery.TableReference(dataset_ref, table.table_id)
        )
        table_schema = [
            (schema_field.name, schema_field.field_type)
            for schema_field in table_info.schema
        ]
        table_ref = dataset_ref.table(table.table_id)
        sample_query = f"SELECT * FROM `{table_ref}` LIMIT 5"
        sample_values = client.query(sample_query).to_dataframe().to_dict(orient="list")
        for key in sample_values:
            sample_values[key] = [
                _serialize_value_for_sql(v) for v in sample_values[key]
            ]
        tables_context[str(table_ref)] = {
            "table_schema": table_schema,
            "example_values": sample_values,
        }

    return tables_context


def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates an initial SQL query from a natural language question.

    Args:
        question (str): Natural language question.
        tool_context (ToolContext): The tool context to use for generating the SQL
          query.

    Returns:
        str: An SQL statement to answer this question.
    """

    prompt_template = """
You are a BigQuery SQL expert tasked with answering user's questions about BigQuery tables by generating SQL queries in the GoogleSql dialect.  Your task is to write a Bigquery SQL query that answers the following question while using the provided context.

**Guidelines:**

- **Table Referencing:** Always use the full table name with the database prefix in the SQL statement.  Tables should be referred to using a fully qualified name with enclosed in backticks (`) e.g. `project_name.dataset_name.table_name`.  Table names are case sensitive.
- **Joins:** Join as few tables as possible. When joining tables, ensure all join columns are the same data type. Analyze the database and the table schema provided to understand the relationships between columns and tables.
- **Aggregations:**  Use all non-aggregated columns from the `SELECT` statement in the `GROUP BY` clause.
- **SQL Syntax:** Return syntactically and semantically correct SQL for BigQuery with proper relation mapping (i.e., project_id, owner, table, and column relation). Use SQL `AS` statement to assign a new name temporarily to a table column or even a table wherever needed. Always enclose subqueries and union queries in parentheses.
- **Column Usage:** Use *ONLY* the column names (column_name) mentioned in the Table Schema. Do *NOT* use any other column names. Associate `column_name` mentioned in the Table Schema only to the `table_name` specified under Table Schema.
- **FILTERS:** You should write query effectively  to reduce and minimize the total rows to be returned. For example, you can use filters (like `WHERE`, `HAVING`, etc. (like 'COUNT', 'SUM', etc.) in the SQL query.
- **LIMIT ROWS:**  The maximum number of rows returned should be less than {MAX_NUM_ROWS}.

**Schema:**

The database structure is defined by the following table schemas (possibly with sample rows):

```
{SCHEMA}
```

**Natural language question:**

```
{QUESTION}
```

**Think Step-by-Step:** Carefully consider the schema, question, guidelines, and best practices outlined above to generate the correct BigQuery SQL.

   """

    bq_schema_and_samples = tool_context.state["database_settings"][
        "bq_schema_and_samples"
    ]

    prompt = prompt_template.format(
        MAX_NUM_ROWS=MAX_NUM_ROWS, SCHEMA=bq_schema_and_samples, QUESTION=question
    )

    response = llm_client.models.generate_content(
        model=config.baseline_nl2sql_model,
        contents=prompt,
        config={"temperature": 0.1},
    )

    sql = response.text or ""
    if sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    print("\n sql:", sql)

    tool_context.state["sql_query"] = sql

    return sql
