# Task 6 - Add Retrieved Context to the Prompt - copilot

## Logic

1. **Pick k.** Use the Task 5 averages. Choose the smallest k where recall stops growing clearly and precision stays acceptable. If k = 3 and k = 5 are close, choose 3.
2. **Retrieve.** Call `query()` with the unaltered ticket `Body` and that k.
3. **Build the prompt.** Keep the Homework 4 prompt as is. Add two labeled blocks:
   - `Ticket body`: the customer's words.
   - `Support articles`: the retrieved chunks.
4. **Add instructions.** The ticket is the customer's input. The articles are outside context. Use an article only if it applies. If none applies, summarize the ticket alone.
5. **Keep settings.** Model `qwen2.5:1.5b-instruct-q4_K_M`, temperature 0, seed 42, stream false, `num_predict` 512.

## Reasoning

Only the context changes, so any score change comes from retrieval. Two labeled blocks stop the model from treating article text as something the customer said. A small k keeps the prompt short, which matters because this small model forgets instructions when the prompt grows. Searching with the raw `Body` means the search text and the summarized text are identical.
