## Task 2 - Split the Data

Create reproducible train, validation, and test partitions from the cleaned
dataset.

### Requirements

- Choose and justify the proportions, assignment strategy, and reproducibility
  parameters of your split policy.
- Implement the assignment algorithm directly without a pre-built splitting
  function.
- Algorithm should output a CSV with 2 columns: `ticket_id` and `split`. 
  `split` is one of `train`, `validation`, or `test`.
- Include automated integrity checks (e.g. make sure your splitting worked as expected).

### Deliverables

- Split-generation code.
- Split verification code.
- Manifest CSV.
- Split writeup containing:
  - Chosen proportions and rationale.
  - Assignment strategy and reproducibility parameters.