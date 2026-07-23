# Execution Trace

## Purpose

`ExecutionTrace` is HIALT's immutable execution journal: the workflow flight recorder. `TraceEntry` is a frozen Pydantic model with timestamp, node, event type, message, and metadata. `AgentState.execution_trace` uses a list-concatenation reducer, so graph-node updates append rather than overwrite prior entries.

Immutable history matters because final state alone cannot explain how an autonomous workflow arrived at approval or failure. Trace entries preserve routing and evidence across revisions for debugging, evaluation, and future controlled use by hialt-recall.

## Current events

The graph records lifecycle, planning, coding, verification, tool request/completion, critique, revision, approval, and failure events. Timestamps are timezone-aware UTC values. Trace metadata currently contains small operational facts such as tool name, exit code, pass/fail, issue count, and code length.

## What it is not

| Concept | Difference |
| --- | --- |
| Logging | Operational diagnostics; may be filtered, reformatted, or discarded. |
| Conversation memory | Context intentionally supplied to later reasoning. |
| RAG / hialt-recall | Retrieval systems may index selected trace data later, but are not the journal. |
| Prompt history | Raw model inputs/outputs; not automatically trace data and may be sensitive. |

## Future work

Before trace data is used by hialt-recall, define retention, serialization, access controls, and which metadata is safe to index. Do not store secrets or complete prompts merely because a trace exists.
