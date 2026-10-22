# Task 5 - Initial Prompt

## Initial prompt

```text
You write an internal summary of a customer support ticket for a human support agent.

Use only the information in the ticket text. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: what the customer wants done.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing.
```

The ticket body goes in the user message. The prompt stays in the system message. The JSON schema is sent in the `format` field.

## Code

- `hw_4/Task5/llm_summary.py` has the prompt, the schema, the call to the model and the validation.
- `summarize_ticket(body, system_prompt)` returns the messages, the raw text, the parsed output and an error (or `None`).
- The validation checks the exact three fields, the types, and that `missing_information` is a list of strings.
- Model `qwen2.5:1.5b-instruct-q4_K_M`, `temperature 0`, `seed 42`.

## Test ticket

- Ticket ID: 87 (training split).
- Why it is not trivial: the body is about 800 characters. It has a problem (EMR/PACS disruption, possible security breach), what was done (assessment by the SOC teams) and a request for help. The text also contains a support reply, so the model must sort out who says what.

## Generated output

```json
{
  "summary": "Severe disruption affecting EMR/PACS connections due to network failure and potential security breach.",
  "customer_request": "Diagnose and resolve the issue to restore normal operations as quickly as possible.",
  "missing_information": [
    "system logs",
    "details of affected endpoints"
  ]
}
```

## Review

- Valid against the contract: yes. No error and no quality warnings.
- Supported by the body: yes. Every statement is in the text.
- One point to watch: the two missing items come from the support reply inside the body ("provide recent system logs and details of affected endpoints"). They are in the text, so this is acceptable. It still shows the model does not separate the customer from the agent.
