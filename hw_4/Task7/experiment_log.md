# Task 7 - Experiment Log

Base for Iteration 1: the original Task 5 prompt. The 10 tickets, the schema, the model and the settings (`temperature 0`, `seed 42`) did not change. Only the prompt changed.

## Iteration 1

### Plan (written before the run)

- Targeted failure pattern: the `customer_request` is too narrow. It drops part of what the customer asks.
- Why this one: it affects 8 of 10 tickets in Task 6. A prompt can fix it, because the old prompt did not ask for every request.
- Exact prompt change, one line:
  - Before: `- customer_request: what the customer wants done.`
  - After: `- customer_request: everything the customer asks for, in one or two sentences. Include every request and every question.`
- Keep rule: keep only if the request improves in at least 2 tickets and no ticket gets worse. Worse means a schema failure, an unsupported statement, or lost important information.

### Improvements

The request is fuller in 7 of 10 tickets:

- 28907: now includes the review of the charges.
- 28399: now includes the consultation session and the server details.
- 28736: now covers all four questions, including the case studies.
- 28763: now includes the request for next steps, repair policy and warranty.
- 28563: now includes the steps for the exchange and the terms.
- 28642: now includes contingency plans and preparation tasks.
- 29206: now includes feasibility, timelines and plugins.

Same in 3 tickets: 28381, 28921, 28571.

Side effect, not planned: `missing_information` in 28571 and 28642 was wrong before (it repeated the customer's questions). Now it is an empty list. That is better than before, but the list is now empty in all 10 tickets.

### Regressions

- Schema: 10 of 10 outputs are valid. No new failures.
- Unsupported statements: none. I checked every new request against the body.
- The prompt says "one or two sentences". Three requests break it: 28399 (3 sentences), 28763 (3 sentences) and 28736 (four numbered items). The rule did not count this as a regression, so it does not change the decision. I note it here.
- Small losses: 29206 no longer has the version "8.20". 28763 lost "persistent". 28399 lost "integration with customer support". I do not count these as important information.
- 29206 now uses the customer's voice ("We need to modify..."). It is still supported by the body.

### Decision

KEEP. The request improved in 7 of 10 tickets (rule: at least 2). No schema failure, no unsupported statement, and no important information lost. Iteration 2 starts from this prompt.

## Iteration 2

### Plan (written before the run)

- Targeted failure pattern: `missing_information` never names a missing detail.
- Why this one: after Iteration 1 it is an empty list in 10 of 10 tickets. Details are clearly absent in at least 5 of them, for example the amounts in 28907, the warranty status in 28763, and the quantity and address in 28571. The prompt does not say the details are ones the customer did not give.
- Exact prompt change, one line:
  - Before: `- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing.`
  - After: `- missing_information: a list of details the customer did not give but the support agent needs to act on the request. Do not list what the customer is asking for. Use an empty list if nothing is clearly missing.`
- Keep rule: keep only if at least 2 tickets get a missing detail that is truly absent from the body and no ticket gets worse. Worse means a schema failure, a listed detail that is in the body, a list item that repeats the customer's request, an unsupported statement, or a worse summary or request.

### Improvements

None. The goal was a real missing detail in at least 2 tickets. The list is still empty in 9 of 10 tickets. No ticket got a detail that is truly absent from the body (for example amounts in 28907, warranty status in 28763, quantity and address in 28571).

### Regressions

- 28571: missing_information changed from an empty list to ['Technical specifications', 'Delivery timeline', 'Return policy']. These are the customer's questions, not missing details. This is exactly what the prompt said not to do.
- 28381: the request got worse. It is now a list of topics ("architectural planning, performance optimization, server setup, ...") and no longer says the customer wants advice or a consultation.
- The prompt change touched only one field, but the summary changed in 6 tickets and the request changed in 8. This shows that a small prompt change moves other fields too. I did not count most of those changes as regressions, because they are small wording changes and are supported by the body.
- Schema: 10 of 10 outputs are valid. No unsupported statements.

### Decision

REVERT. The rule needs at least 2 improved tickets and no worse ticket. There are 0 improved tickets and 2 worse tickets (28571 and 28381). The accepted prompt stays the Iteration 1 prompt.

## Final prompt

Iteration 1: kept. Iteration 2: reverted. The final accepted prompt is the Iteration 1 prompt (file prompt_iteration_1.txt):

~~~text
You write an internal summary of a customer support ticket for a human support agent.

Use only the information in the ticket text. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: everything the customer asks for, in one or two sentences. Include every request and every question.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing.
~~~

## What I learned

- A one-line change in the prompt can fix the request field (7 of 10 tickets) but changes other fields too.
- The 1.5B model does not report missing information, even when told how. The prompt cannot fix this. A bigger model or a different design would be needed.
