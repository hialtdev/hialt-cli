# Logging

## Current implementation

`hialt.logging_config.configure_logging(level="INFO")` configures the root logger. CLI startup calls it with `get_settings().log_level`; `Settings.from_environment()` sources that value from `HIALT_LOG_LEVEL`, defaulting to `INFO`.

The initializer resolves the level name with an `INFO` fallback, sets the root logger level, and adds a Rich `RichHandler` when one named `hialt-rich-console` is not already present. On repeated calls it finds that handler by name and updates its level instead of adding a duplicate. The handler writes to stderr, hides paths, enables Rich tracebacks and markup, and formats messages without a prefix.

Modules use named loggers. Current usage includes graph lifecycle messages, verifier and tool completion, provider failures, parser warnings, and trace-entry debug messages. Complete prompts are not logged by the current modules.

## Relationship to ExecutionTrace

Logging records application operation for humans and operators: failures, state transitions, and command timing. `ExecutionTrace` records immutable agent-workflow facts such as planning, tool request/completion, routing, approval, and failure. Logging is mutable/filterable operational output; trace is the agent flight recorder. Neither is conversation memory, RAG, or prompt history.

## Future work

Rotating file logging is not implemented. If added, it should remain configured only by this module, avoid secrets, and not replace execution tracing.
