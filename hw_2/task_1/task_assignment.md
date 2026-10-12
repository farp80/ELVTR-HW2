## Task 1 - Clean the Data

Prepare the supplied data for splitting and modeling. Identify relevant
record-level quality issues and decide which to change, retain, or defer.

### Requirements

- Implement deterministic text cleaning in code.
- Do not use pre-defined text-cleaning libraries.
- Produce a cleaned dataset with the same `ticket_id`.
- For each decision, record representative `ticket_id` values, the action and
  reason, the affected count, and one risk or limitation.

### Deliverables

- Cleaning code.
- Cleaned dataset.
- Cleaning writeup containing, for each cleaning decision:
  - What the issue was.
  - Why you consider it an issue.
  - How you addressed the issue.
  - How many records are affected by the issue.
  - Some representative ticket_id's.
  - Risks or limitations of your solution

### Cleaning principles:
 - Normalize whitespace and encoding
 - Parse and structure fields
 - Normalize casing, enums, formats, etc
 - correct IDs and join keys
 - deduplicate records
 - drop invalid or incomplete records
 - filter PII