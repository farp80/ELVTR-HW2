# Task 5 — Write an Initial Prompt

## Requirements

- Write an initial prompt that accepts the ticket's `Body` and returns a JSON object matching the output contract below.
- Create a reusable function to call the LLM with the prompt and ticket body, including output validation.
- Successfully run the prompt on one non-trivial ticket.
- Ground every output field only in the supplied ticket body.

### JSON output contract

The output must be an object containing exactly these required fields:

| Field | Type | Contract |
| --- | --- | --- |
| `summary` | string | One or two concise sentences describing the reported issue. |
| `customer_request` | string | The action or outcome the customer appears to want. |
| `missing_information` | array of strings | Details needed to understand or act on the request; empty when none are clearly missing. |

## Deliverables

- Initial prompt.
- Code to call the LLM and validate its result.
- Ticket ID used as the test ticket.
- Generated output for that single test ticket.
