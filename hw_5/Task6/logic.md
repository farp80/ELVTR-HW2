# Task 6 — Put retrieval in the prompt

The program is in `program-cursor.md`.

## Logic

Pick k from the Task 5 averages. Use the smallest of 1, 3, and 5 whose mean recall is clearly higher than the next smaller k, while mean precision stays at or above 0.5. When 3 and 5 are close, keep 3.

Call `query()` with the unaltered ticket Body and that k. In the prompt, put the returned chunks under the heading "Support articles" and the ticket under the heading "Ticket body".

Keep the accepted Homework 4 field rules. Keep the model settings: `qwen2.5:1.5b-instruct-q4_K_M`, temperature 0, seed 42, stream false, and `num_predict` 512.

Add four rules to the system text. The ticket body is what the customer wrote. The support articles are outside context. Use an article only when it applies to this ticket. When no article applies, summarize the body on its own. Article facts stay article facts.

## Reasoning

The summary task stays the same. The allowed change is to place the retrieved text in the prompt and to say what that text is. The old line "use only the ticket text" now has two sources, so it names the body as the customer's words and the articles as outside context.

Homework 4 showed this 1.5B model drops asks as the instruction gets longer. The smaller k leaves room for the ticket. Search receives the Body as stored, so the search question and the summarized ticket are the same text.
