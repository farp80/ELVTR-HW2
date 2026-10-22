# Task 6 — Apply the Initial Prompt

Run the initial prompt on all 10 listed canonical dataset records without altering them:

| Department | `ticket_id` |
| --- | ---: |
| Billing and Payments | `28907` |
| Customer Service | `28399` |
| General Inquiry | `28381` |
| Human Resources | `28921` |
| IT Support | `28736` |
| Product Support | `28763` |
| Returns and Exchanges | `28563` |
| Sales and Pre-Sales | `28571` |
| Service Outages and Maintenance | `28642` |
| Technical Support | `29206` |

These are the longest `Body` values in each department by character count; ties use the lowest numeric `ticket_id`.

## Requirements

- Use all 10 listed tickets without alteration.
- Review each output for general quality.

## Deliverables

For each ticket, report:

- The full input sent to the LLM.
- The output returned by the LLM.
- Whether the output followed the JSON schema.
- Whether the output was factually supported by the ticket body.
- Whether it contained the most important information from the ticket body.
- Whether you agree with the identified missing information, and why.
- High-level issues observed.
