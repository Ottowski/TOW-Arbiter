# TOW Arbiter Development Guide

Use this file as the starting point before changing the project. It defines the
project's boundaries and the checks expected from AI-assisted development.

## Project scope

TOW Arbiter is a local-first rules assistant for **Warhammer: The Old World**.
It combines a FastAPI backend, a React/Vite frontend, and a RAG pipeline that
searches the Markdown and text files under `rules/`.

Keep work within that scope unless the user explicitly requests otherwise:

- Do support rules lookup, source retrieval, and explanation of content that is
  present in the project's knowledge base.
- Do not turn the project into a general-purpose chatbot or support unrelated
  games and rulesets as an incidental feature.
- Do not invent rules, citations, army data, or source metadata. When retrieved
  material does not support an answer, say that it cannot be determined from the
  available rules.
- Do not replace or overwrite the supplied rules corpus with generated content.
- Treat `rules/` as authoritative project input, not as a place to silently
  "correct" content while working on application behavior.
- Preserve local-first operation. Do not require a hosted service, account,
  database, or telemetry for core desktop functionality.
- Optional LLM integrations must remain optional and must not break the local
  retrieval-only path.

## Architecture boundaries

- `rules/`: source material used by retrieval. Changes here can invalidate the
  vector index and must be intentional.
- `src/document_loader/`: loading and chunking source files.
- `src/rag/`: knowledge-base, retrieval, rule matching, and answer generation.
- `src/rag_pipeline.py`: public coordination layer used by the CLI, API, and
  future application entry points.
- `api.py`: FastAPI models and HTTP behavior.
- `app_launcher.py`: desktop-specific startup, local port selection, and
  pywebview behavior.
- `frontend/src/`: the React user interface.
- `build_desktop.ps1` and `TOW Arbiter.spec`: Windows packaging.

When a behavior spans multiple surfaces, keep their contracts consistent. For
example, an API field or status change must be reflected in both the backend
and frontend consumers.

## Protected behavior

Do not regress these requirements:

- The app must still run without an API key or external LLM.
- Source metadata must remain available with answers.
- The API must remain bound to loopback for the desktop app.
- Desktop data must remain writable outside the packaged executable, under
  `%LOCALAPPDATA%\TOW-Arbiter` when frozen.
- The knowledge base initialization status must be exposed to clients.
- Existing Markdown rules and frontend Markdown rendering must continue to work.
- The packaged application must include both `rules/` and `frontend/dist/`.
- Avoid exposing secrets in source, logs, browser requests, examples, or tests.

## Change discipline

- Make the smallest complete change that addresses the request.
- Reuse the existing RAG pipeline instead of duplicating retrieval logic in a
  client or entry point.
- Keep backend source paths compatible with both source execution and
  PyInstaller's frozen application layout.
- Preserve Python 3.11+ support and the frontend's supported Node.js versions.
- Add focused tests when changing retrieval, answer formatting, API contracts,
  startup behavior, or other non-trivial logic.
- Do not commit generated or local-only files such as `frontend/dist/`,
  `data/vector_store/`, virtual environments, caches, build output, packaged
  executables, or user configuration.
- Update the root `README.md` when setup, runtime behavior, commands, or
  packaging requirements change.

## Frontend expectations

- Keep React components functional and avoid unnecessary new dependencies.
- Preserve keyboard and mobile/basic responsive usability when changing the UI.
- Show loading, empty, and error states explicitly; do not silently hide
  failed requests or initialization errors.
- Preserve the rule-link interaction unless a requested feature deliberately
  replaces it and all callers are updated.
- Use the existing JavaScript/JSX style and `frontend/eslint.config.js` rules.

## Backend and RAG expectations

- Validate external request data with Pydantic models.
- Return useful HTTP error statuses rather than success-shaped error responses.
- Keep retrieval and answer-generation code independent enough to test without
  requiring network access.
- Preserve deterministic, source-backed behavior in the non-LLM path.
- Treat an absent, stale, or failed knowledge-base initialization as an explicit
  operational state.
- Keep file and filesystem access safe for packaged and un-packaged execution.

## Validation

Run the narrowest checks that cover the change, then build more broadly when the
change affects startup or packaging.

From the repository root:

```powershell
# Frontend lint
npm --prefix frontend run lint

# Frontend production build
npm --prefix frontend run build

# Python syntax checks for the main application surfaces
.\.venv\Scripts\python.exe -m py_compile api.py app_launcher.py main.py src\rag_pipeline.py

# Current focused retrieval smoke test
.\.venv\Scripts\python.exe .\test_shooting.py

# Full desktop packaging check when entry points, bundled data, or paths change
.\build_desktop.ps1
```

If a command is unavailable because dependencies have not been installed, follow
the setup in `README.md`; do not weaken or skip validation merely to avoid that
setup.

## Definition of done

A change is complete when:

1. The requested behavior works on its actual entry point.
2. Existing CLI, API, frontend, and desktop behavior remains compatible where it
   should.
3. Errors are visible and actionable.
4. Relevant lint, tests, syntax checks, and builds pass.
5. Documentation is updated when the user-facing contract or workflow changed.
