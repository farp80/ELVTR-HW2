# Task 6 - Add Retrieved Context to the Prompt - claude

## Logic

1. **Pick k** from the Task 5 averages. Take the smallest k where recall stops growing clearly and precision is still acceptable. If k = 3 and k = 5 are close, take 3.
2. **Retrieve.** Call `query()` with the unaltered ticket `Body` and that k.
3. **Build the prompt.** Keep the accepted Homework 4 prompt word for word. Add two labeled blocks:
   - `Ticket body`: the customer's words.
   - `Support articles`: the retrieved chunks.
4. **Add one instruction.** The ticket is the customer's input. The articles are outside help. Use an article only if it applies to the ticket. If none applies, summarize the ticket alone.
5. **Keep settings.** Model `qwen2.5:1.5b-instruct-q4_K_M`, temperature 0, seed 42, stream false, `num_predict` 512.

## Reasoning

Only the context changes, so any score change comes from retrieval.

Two labeled blocks stop the model from treating article text as something the customer said.

A small k keeps the prompt short. A 1.5B model loses instructions as the prompt grows.

Searching with the raw `Body` is required, and it keeps the search text identical to what gets summarized.
