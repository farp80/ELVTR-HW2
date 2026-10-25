# Task 7 - Check Three RAG-Informed Summaries - claude

## Logic

Run the Task 6 prompt on the unaltered `Body` of three tickets.

| Ticket | Case | What to expect |
| --- | --- | --- |
| 28763 | Supported | Chunks on the same product and warranty |
| 29206 | Supported, many sources | Chunks from several Jira articles |
| 28921 | Unsupported | Only weak matches |

For each ticket, record:
1. The retrieved chunks.
2. The RAG summary.
3. The four scores from the frozen Task 2 rubric, with a reason for each.
4. The no-RAG scores from Task 2, side by side.
5. A short note on what changed in each field and why.

Report the scores as they are, even if RAG ties or loses.

## Reasoning

The three tickets test three situations with one prompt.

When articles help, the summary must stay true to the ticket. When they do not (28921), the model must ignore them.

The frozen rubric makes RAG and no-RAG scores comparable.

RAG may not win with a weak model. The goal is an honest comparison, not a gain.
