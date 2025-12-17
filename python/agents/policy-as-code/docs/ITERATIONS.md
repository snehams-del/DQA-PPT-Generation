# Policy-as-Code Agent: Iterations

This document outlines the iterative development process of the Policy-as-Code Agent, detailing the different approaches explored, their advantages and disadvantages, and the rationale behind each transition.

## Iteration 1: Hardcoded Regex-Based Parsing

### Description
The initial version of the agent relied on hardcoded regular expressions within the `parse_policy_query` function to extract policy information from natural language queries. The `run_simulation` function contained specific `if/elif` blocks to evaluate these predefined policy types.

### Pros
-   **Simplicity:** Easy to implement for a very limited set of known policy patterns.
-   **Predictable:** Behavior was entirely deterministic for supported queries.

### Cons
-   **Rigidity:** Could only understand and process a fixed, small set of policy queries. Any new policy type required code changes to both the parser and the simulation logic.
-   **Limited Expressiveness:** Natural language queries had to strictly adhere to predefined patterns, making the agent difficult to use for varied or nuanced policy definitions.
-   **Maintenance Burden:** Adding new policy types quickly led to a large, unmanageable `if/elif` structure in `run_simulation`.
-   **Not Scalable:** Could not scale to a wide range of real-world data governance policies.

### Rationale for Transition
The inherent inflexibility and maintenance burden of the regex-based approach became apparent as the need for more diverse policy validation emerged. It was clear that a more dynamic and extensible solution was required to truly leverage natural language for policy definition.

## Iteration 2: LLM-Based JSON Parsing

### Description
In this iteration, the `parse_policy_query` function was replaced with an LLM-based approach (`llm_parse_policy_query`). The LLM was tasked with converting natural language queries into a structured JSON format, adhering to a predefined `policy_schema.md`. The `run_simulation` function was refactored to be more generic, interpreting the JSON structure and applying rules based on `attribute`, `operator`, and `value` fields.

### Pros
-   **Increased Flexibility:** The LLM could interpret a wider range of natural language queries, translating them into a consistent JSON representation.
-   **Improved Expressiveness:** Users had more freedom in how they phrased their policy queries.
-   **More Generic Simulation:** The `run_simulation` became more generalized, reducing the need for extensive code changes when new policy types were introduced (as long as they fit the JSON schema).

### Cons
-   **LLM Inconsistency:** The LLM did not always consistently return the same attribute names or structures for similar queries, leading to parsing failures or unexpected behavior in `run_simulation`.
-   **Schema Limitations:** While more flexible than regex, the predefined JSON schema still imposed limitations on the complexity and types of policies that could be expressed. Policies requiring complex logic or computations (e.g., counting PII columns based on specific criteria, checking for the existence of related entities) were difficult to represent accurately in the generic `attribute-operator-value` format.
-   **Attribute Mapping Challenges:** Mapping diverse natural language concepts to a fixed set of JSON attributes and operators proved challenging and often led to `Actual value: None` errors when the `run_simulation` couldn't find the expected data.
-   **Debugging Complexity:** Debugging issues related to LLM parsing and attribute mapping was time-consuming.

### Rationale for Transition
Despite the increased flexibility, the limitations imposed by the predefined JSON schema and the inconsistencies in LLM output for complex policy logic became significant roadblocks. The need for a truly dynamic and unconstrained policy evaluation mechanism led to the exploration of generating executable code.

## Iteration 3: LLM-Generated Python Code (Current Approach)

### Description
The current and most advanced iteration leverages the LLM to directly generate executable Python code for policy evaluation. The `llm_generate_policy_code` function prompts the LLM to create a Python function (`check_policy(metadata: list)`) that takes the entire list of metadata entries and returns a list of violations. The `run_simulation` function then executes this single generated function to evaluate the policy across all data.

### Pros
-   **Maximum Flexibility and Expressiveness:** The LLM can generate arbitrary Python logic, allowing for the validation of virtually any policy, no matter how complex or nuanced. This completely removes the limitations of predefined schemas or attribute mappings.
-   **Highly Powerful:** Enables the agent to handle policies involving complex computations, conditional logic, and data traversal that were impossible with previous approaches.
-   **Direct Mapping:** The LLM directly translates natural language into executable logic, reducing the "translation layer" issues encountered in JSON parsing.
-   **Improved Debuggability:** The generated Python code is human-readable, making it easier to understand and debug policy evaluation logic.
-   **Future-Proof:** New policy types can be supported simply by improving the LLM's ability to generate the corresponding Python code, without requiring changes to the core agent framework.

### Cons
-   **Security Concerns:** Executing dynamically generated code is inherently risky and requires a robust sandboxing mechanism to prevent malicious code injection or unintended system access. The current implementation uses Python's built-in `exec()` function for simplicity during development, which is not secure. For production environments, this should be replaced with a secure, sandboxed code execution environment.
-   **LLM Reliability:** The quality and correctness of the generated Python code depend heavily on the LLM's capabilities and the clarity of the prompt. Errors in generated code can lead to runtime exceptions.
-   **Increased Complexity in `run_simulation`:** While the policy definition is simplified, the `run_simulation` function now needs to manage code execution, error handling during execution, and potentially more sophisticated reporting.

### Iteration 4: GCS-Native Workflow and Remediation

### Description
This iteration focused on making the agent more robust, user-friendly, and production-ready by removing local file dependencies and adding a remediation feature.

### Pros
-   **GCS-Native:** The agent now operates exclusively on GCS URIs, removing the need for local metadata files and making it easier to deploy and use in a cloud environment.
-   **Actionable Remediation:** The new `suggest_remediation` tool provides users with actionable steps to fix policy violations, making the agent a more complete governance solution.
-   **Improved Performance and Resilience:** The remediation tool processes violations concurrently, and includes a retry mechanism with exponential backoff, making it faster and more resilient to transient errors.
-   **User-Controlled Workflow:** Remediation suggestions are now optional and are only provided when the user explicitly asks for them, giving the user more control over the interaction.

### Cons
-   **Increased Complexity:** The addition of the remediation feature and the concurrent processing logic adds complexity to the agent's codebase.

### Rationale for Current Approach
The move to a GCS-native workflow was a critical step in making the agent more practical for real-world use cases. The addition of the remediation feature was a direct response to user feedback and significantly increases the agent's value by not just identifying problems, but also helping to solve them.

## Iteration 5: Live Dataplex Search Integration

### Description
This iteration introduced a major new capability: the ability to run policies directly against the live Dataplex Universal Catalog, removing the dependency on static metadata exports. A new, all-in-one tool, `run_policy_on_dataplex_search`, was created to handle this workflow, while the existing GCS-based tools were retained to provide maximum flexibility.

### Pros
-   **Real-Time Validation:** Policies can be checked against the most up-to-date metadata without the need for manual exports, providing immediate and accurate results.
-   **Simplified User Experience:** For live checks, the user only needs to provide a policy and a search query. The agent handles the entire multi-step process of searching, fetching details, generating code, and running the simulation within a single tool.
-   **Increased Flexibility:** The agent now supports two distinct workflows—offline analysis via GCS and online validation via Dataplex search—allowing users to choose the best approach for their needs.

### Cons
-   **API Complexity:** Interacting with the Dataplex API introduced significant complexity, particularly in handling the nested and non-standard protobuf objects returned for entry aspects. This required the development of a custom, recursive converter to transform the data into a usable format.
-   **Increased Latency:** Live API calls, especially fetching full details for many entries, can be slower than reading from a pre-exported GCS file.
-   **Potential for API Errors:** The new workflow is subject to potential network issues or API-specific errors that are not present in the GCS-based approach.

## Iteration 6: Dynamic Prompting and Usability Enhancements

### Description
This iteration focused on improving the intelligence and user experience of the agent. The key changes were making the prompt context-aware by dynamically injecting sample data, and removing the need for the user to manually configure the GCP Project ID.

### Pros
-   **Context-Aware Prompts:** Instead of using a static, hardcoded example in the prompt, the agent now dynamically generates sample values from the user's provided data source (either GCS or Dataplex). This provides the LLM with a much more relevant and accurate example of the data structure, leading to higher-quality generated code.
-   **Improved User Experience:** The agent can now automatically detect the GCP Project ID from the user's `gcloud` authentication context, removing the requirement to have the `GCP_PROJECT` environment variable set.
-   **More Robust Sample Generation:** The logic for generating sample data was iteratively improved to be more intelligent. It now finds the most "representative" entry in a metadata file (i.e., the one with the most fields) to use as the example, ensuring that a rich, detailed entry is chosen over a sparse one.

### Cons
-   **Increased Startup Complexity:** The agent's internal logic is now slightly more complex, as it needs to perform the sample data generation and project ID detection steps before it can generate the policy code.

## Iteration 7: Persistent Memory with Firestore and Vector Search

### Description
This iteration introduced a sophisticated, long-term memory system using Google Cloud Firestore. Instead of generating policy code from scratch every time, the agent can now store, retrieve, and reuse policies. This iteration also added "Core Policies" for compliance scorecards and detailed execution logging for analytics.

### Pros
-   **Efficiency & Cost:** By reusing cached policy code, the agent significantly reduces the number of calls to the LLM for code generation, saving both time and token costs.
-   **Consistency:** Ensures that the exact same policy query results in the exact same code being executed, preventing "drift" where the LLM might generate slightly different logic on different runs.
-   **Scalability:** Firestore allows multiple agent instances to share the same knowledge base, scaling to thousands of policies and concurrent users.
-   **Analytics:** The execution logging enables powerful insights, such as identifying "hotspot" resources that frequently fail compliance checks or tracking the organization's compliance score over time.

### Cons

-   **Infrastructure Dependency:** The agent now requires a Google Cloud Firestore database and a Vector Search index to function fully, adding a slight overhead to the initial setup compared to a purely stateless or local-file-based agent.



## Iteration 8: Reporting, Scorecards, and MCP Integration



### Description

This iteration rounded out the agent's capabilities by adding comprehensive reporting features and integrating with the Model Context Protocol (MCP).



### Pros

-   **Compliance Scorecards:** The `generate_compliance_scorecard` tool allows users to run a standard set of "Core Policies" to get a high-level health check of their data.

-   **Rich Exporting:** The `export_report` tool enables users to save violation reports as CSV or HTML files, and optionally upload them directly to GCS for sharing.

-   **Execution Analysis:** New tools `get_execution_history` and `analyze_execution_history` provide insights into past runs, helping identify trends and "hotspot" resources.

-   **MCP Extensibility:** The agent now connects to a Dataplex MCP server, allowing it to leverage external tools for deeper Dataplex integration if available.



### Cons

-   **Increased Toolset Size:** The number of tools available to the agent has grown, requiring careful prompt engineering (instructions) to ensure the LLM chooses the right tool for the job.
