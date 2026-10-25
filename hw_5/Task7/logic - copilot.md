# Task 7 - Check Three RAG-Informed Summaries - copilot

## Logic

Run the Task 6 prompt on the unaltered `Body` of three tickets:

| Ticket | Case | What to expect |
| --- | --- | --- |
| 28763 | Supported | Articles on the same product and warranty |
| 29206 | Supported, many sources | Chunks from more than one Jira article |
| 28921 | Unsupported | Weak matches only |

For each ticket, record:
1. The retrieved chunks.
2. The RAG summary.
3. The four rubric scores, using the frozen Task 2 rubric.
4. The no-RAG scores from Task 2, next to them.
5. A short note on what changed in each field, and why.

Report the scores as they are, even if RAG ties or scores lower.

## Reasoning

The three tickets test three situations with one prompt. When the knowledge base helps, the summary should stay faithful. When it is unrelated (28921), the prompt must make the model ignore it. Using the frozen rubric makes the RAG and no-RAG scores comparable. The assignment says RAG may not win with a weak model. The goal is the process and an honest comparison, not a better number.
