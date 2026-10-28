# Task 6 — Selection Reasoning

**Selected approach:** Cursor’s reuse-oriented structure, combined with Claude’s sequential `k` selection.

Cursor reuses the accepted Homework 4 prompt, model settings, schema, validator, and ticket loader. This reduces duplicated logic and keeps behavior consistent across tasks. Claude’s `choose_k` stops at the first failed threshold, matching the stated policy: increase `k` only when recall improves by at least 0.10 and precision remains at least 0.50.

The ticket body is retrieved unchanged and kept separate from support articles. The model summarizes customer-provided facts; articles only help identify missing information. The output records retrieved chunks, messages, raw response, validated result, and validation errors for analysis.

**Important:** verify repository paths and the exact prompt rule before running. Runtime correctness is not confirmed until tested with the local vector database, model, metrics, and a known ticket.
