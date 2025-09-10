Hephaestus Bootstrap & Activation Guide

Purpose: Provide quick steps to activate the "Hephaestus" persona in Gemini Code Assist (or any IDE-based assistant) and best practices for inline directives and Chronos context.

1. Quick Activation (VS Code)
- Open the command palette (Ctrl+Shift+P) and select "Preferences: Configure User Snippets".
- Choose the repository/global scope and ensure the file `.vscode/HEPHAESTUS_BOOTSTRAP.code-snippets` is installed in the repo.
- In Gemini Code Assist chat, paste the snippet by typing the prefix `hephaestus-bootstrap` or open the snippet file and copy-paste.

2. Recommended Session Bootstrap
- At the start of each coding session paste the Hephaestus Bootstrap Prompt into the assistant chat and wait for acknowledgement.
- Provide a short directive and relevant file context or highlighted code.

3. Chronos Context Pattern
- When asking for code changes, include the minimal context necessary (file path, code block, and 2-3 lines of surrounding code).
- Optionally attach an index of related files or a short summary of the state.

4. Inline Directives
- Use short, explicit comment directives in code to request refactors, tests, or architecture changes (examples below):

# DIRECTIVE: Architectus Prime, refactor this function for idempotency.
# DIRECTIVE: Architectus Prime, generate pytest unit tests for this class.
# DIRECTIVE: Architectus Prime, produce Terraform HCL for deploying this service.

5. Persistence Options
- Store a canonical bootstrap prompt in `.vscode/HEPHAESTUS_BOOTSTRAP.code-snippets` for quick reuse.
- For stronger persistence, keep a private opsec-safe file outside the repo containing any sensitive operational instructions or credentials (do not commit secrets).

6. Example Workflow
- Paste bootstrap -> provide Chronos context -> issue a concise inline directive -> review changes and iterate.

