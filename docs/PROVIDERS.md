# Providers

## Why this boundary exists

The graph should orchestrate a reasoning capability rather than a vendor SDK. `Provider.generate()` returns a normalized `LLMResponse` containing content, finish reason, usage, model, and raw response. `build_provider()` translates `RoleConfig` into a concrete provider outside graph routing.

## Current implementations

| Provider | Current status |
| --- | --- |
| `StubProvider` | Default for stub/local roles; returns an empty normalized response. |
| `OllamaProvider` | Calls local `/api/generate`, records response usage, and wraps request failures in `ProviderError`. Unit-tested and the only provider reported as run end-to-end. |
| `AnthropicProvider` | Calls the Messages API using `ANTHROPIC_API_KEY` and normalizes text/usage. The adapter exists but has never been exercised against a live API key. |

Do not describe Anthropic and Ollama as equally validated. The graph defaults every reasoning role to `stub`, so neither live provider is selected without configuration changes.

## Configuration and tradeoff

Roles have independent `provider` and optional `model` fields (`planner`, `coder`, `critic`, and reserved `verifier`). Settings currently read only operational environment overrides, not role configuration from a file. The explicit `GraphDependencies` path is the normal graph composition path; direct node calls can fall back to cached `get_settings()`. This is an open architectural decision described in [Architecture](ARCHITECTURE.md).

## Future work

Prompt rendering, provider calls in agents, provider retry policy, and additional adapters remain future work. Provider selection and model selection should remain separate role-level concerns.
