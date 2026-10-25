# Task 6 - Selected k and Updated Prompt - claude

## 1. Selected k

**Status: the rule is fixed now. The value comes from your Task 5 numbers.** I could not run Task 5 on my machine, so I cannot name the number honestly. The code in `program - claude.md` applies the rule below to `../Task5/metrics.json` and prints the result. Write that number here: **k = ___**.

### The rule

Only k = 1, 3, and 5 were tested, so choose among them.

1. Start with k = 1.
2. Move from 1 to 3 only if mean **recall@3 is at least 0.10 higher** than recall@1 **and** mean **precision@3 is at least 0.5**.
3. Move from 3 to 5 only if you reached 3 and mean **recall@5 is at least 0.10 higher** than recall@3 **and** mean **precision@5 is at least 0.5**.
4. Never go above 5.

### Why this rule

- **A small k is the default.** The model is 1.5B parameters. A longer prompt makes it forget instructions, and every extra chunk can distract it.
- **A bigger k must earn its place.** It has to find clearly more useful material (recall up by 0.10) without filling the prompt with junk (precision at least 0.5, meaning at least half of the chunks help).
- **Close results keep the smaller k.** A rise below 0.10 is noise with only 5 queries.
- **Hit@k is a floor.** If mean hit@k is low at the chosen k, say so. It means the model often gets no useful chunk, and the RAG summary will likely match the no-RAG one.

## 2. Updated prompt

### What changed, and only this

| Part | Homework 4 accepted prompt | Task 6 prompt |
| --- | --- | --- |
| Sources | One source: the ticket text | Two labeled sources: TICKET BODY and SUPPORT ARTICLES |
| Rule 1 | "Use only the information in the ticket text." | Replaced by the source paragraph below |
| Output fields | `summary`, `customer_request`, `missing_information` | **Unchanged** |
| Field descriptions | As in Homework 4 (Iteration 1) | **Unchanged, word for word** |
| Model and settings | `qwen2.5:1.5b-instruct-q4_K_M`, temperature 0, seed 42, stream false | Same, plus `num_predict: 512` |

### System prompt (full text)

~~~text
You write an internal summary of a customer support ticket for a human support agent.

You receive two sources, in two labeled blocks:
- TICKET BODY: what the customer wrote. This is the only text you summarize.
- SUPPORT ARTICLES: approved company articles found for this ticket. The customer did not write them. They are background help only.

Describe only what the customer wrote in the TICKET BODY. Use the SUPPORT ARTICLES only to decide which details the customer did not give but support needs. Never copy article facts into summary or customer_request. If no article applies to this ticket, ignore the articles. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: everything the customer asks for, in one or two sentences. Include every request and every question.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing.
~~~

### User message (format)

~~~text
TICKET BODY (written by the customer):
<the unaltered Body>

SUPPORT ARTICLES (company knowledge, not written by the customer):
[chunk_id] article title
<chunk content>

[chunk_id] article title
<chunk content>
~~~

## 3. Why the prompt is built this way

- **Two labeled blocks.** The model must not mistake article text for something the customer said. The labels say who wrote each block.
- **Articles help only `missing_information`.** In Task 2 that was the weakest dimension (0.5 on all five tickets). Many articles list what the customer must provide, which is the kind of fact the list should name.
- **"Never copy article facts into summary or customer_request."** This protects the Grounded dimension. A summary must stay true to the ticket.
- **"If no article applies, ignore the articles."** A 1.5B model tends to use whatever it is given. This line is the safety valve for unsupported tickets such as 28921.
- **Search with the raw `Body`.** The search text and the summarized text are the same, so nothing is lost in a rewrite.
