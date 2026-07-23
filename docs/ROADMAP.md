# Roadmap

## Completed

- LangGraph planner → coder → verifier → critic workflow with bounded revision routing.
- Typed workflow state, deterministic verification, centralized Rich logging, and immutable execution trace.
- Provider protocol, normalized responses, Ollama adapter, Anthropic adapter, and defensive critic response parsing.
- Documentation and architecture baseline.

## Current

- Keep workflow boundaries provider-independent and deterministic tools isolated behind `ToolRunner`.
- Document and resolve the explicit dependency-injection versus singleton-fallback provider-resolution tradeoff.

## Next

- Prompt Objects and a Prompt Renderer.
- Provider integration for planner and coder.
- Planner and coder implementations.
- Critic implementation: response parsing is complete, but `review()` does not call a provider yet.
- Live Anthropic validation; the provider class exists but has not been exercised with a live key.
- Role-level multi-provider orchestration and configuration.

## Future

- Git tooling and additional filesystem/testing/quality adapters.
- Observability improvements, including careful file-log design.
- hialt-recall integration using appropriately governed execution-trace data.
- Continued documentation improvements as implementation changes.
