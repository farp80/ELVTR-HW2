# Homework 6 - Score and Checklist

Based on `WEEK_6_ASSIGNMENT.md` and `WORKFLOW_CONTRACT.md`. Checked against the files in `hw_6/` on Nov 5, 2026.
"Done" means the file exists and I checked it. "Open" means something is left to do.
The assignment has no official rubric, so the points are my estimate: 10 per task.

## Score

| Task | Points | Main reason |
| --- | --- | --- |
| Task 1 - Service contracts | 10 / 10 | One contract file per service, each with a request table, a response table, and errors. |
| Task 2 - Routing service | 10 / 10 | All requirements met. |
| Task 3 - Retrieval service | 10 / 10 | All requirements met. |
| Task 4 - LLM service | 10 / 10 | All requirements met. |
| Task 5 - Workflow | 10 / 10 | All requirements met. |
| Task 6 - Logging and tracing | 10 / 10 | All requirements met. Logging goes only through `TraceLogger`. |
| **Total** | **60 / 60** | The submission zip is not built yet. See the last section. |

## Checks that were run

| Check | Result |
| --- | --- |
| `python workflow.py` in `Task6` | `summary_ready_for_review`, `error` is `null`. |
| Workflow with Ollama unreachable | `workflow_failed`, with the failure in the trace log. |
| Workflow with an empty `Body` | `input_rejected`. |
| `Task5/workflow.py` on one ticket | `summary_ready_for_review`. |
| `show_timeline.py` | `PARALLEL`. Routing finished while the LLM was still running. |
| `test_trace_logger.py` with `TraceLogger` | 4 tests pass. |
| `test_trace_logger.py` with `IndexedTraceLogger` | 4 tests pass. |
| Ruff and pyright on Tasks 2 to 6 | No warnings. |

## Task 1 - Define the service contracts

| Item | Status |
| --- | --- |
| Routing: request fields, types, optionality | Done. `Task1/routing_contract.md`. |
| Routing: response keeps `recommended_department` and `class_scores` | Done. |
| Retrieval: request and response | Done. `Task1/retrieval_contract.md`. |
| LLM: request and response | Done. `Task1/llm_contract.md`. Prompt, model, options and an optional schema on every call. |
| Errors for each service | Done. `ValueError` for bad requests, `RuntimeError` for internal failures. |
| A separate contract doc for each service | Done. Three files with the same sections: Request, Response, Errors. |
| One request schema and one response schema per service | Done. A field table with type, required, and rules for each. |

## Task 2 - Routing service

| Item | Status |
| --- | --- |
| `routing_service.py` with `RoutingService.route_ticket` | Done. |
| Uses the Homework 4 classifier | Done. `TicketRoutingClassifier` with `hw4_candidate.pkl`, the model chosen in Homework 4. |
| Classifier loaded once in `__init__` | Done. |
| Input checked against the contract | Done. `__body` raises `ValueError`. |
| Response keeps `recommended_department` and `class_scores` | Done. `__check` confirms all ten departments, finite scores, and that the top score is the department. |
| Failures surfaced, no default value | Done. Classifier errors become `RuntimeError`. |

## Task 3 - Retrieval service

| Item | Status |
| --- | --- |
| `retrieval_service.py` with `RetrievalService.retrieve_evidence` | Done. |
| Uses the Homework 5 `VectorStore`, saved index and k = 5 | Done. `hw_5/Task4/lancedb`, `top_k=5`. |
| Store opened once in `__init__`, never rebuilt | Done. |
| Input checked against the contract | Done. |
| Each row checked for `rank`, `chunk_id`, `distance`, `content`, `metadata` | Done. |
| Failures surfaced, no empty fallback | Done. Query errors become `RuntimeError`. |

## Task 4 - LLM service

| Item | Status |
| --- | --- |
| `llm_service.py` with `LLMClient.call_llm` | Done. |
| Ollama URL stored in `__init__`, no model loaded in Python | Done. |
| Prompt, model, settings and schema passed on every call | Done. Nothing is fixed in the service. |
| Input checked against the contract | Done. Two bugs were fixed today: `schema` was read before it was set, and `call_llm` read `schema` after overwriting the payload. |
| Failures surfaced, no default value | Done. HTTP errors and empty replies become `RuntimeError`. |

## Task 5 - Workflow

| Item | Status |
| --- | --- |
| `workflow.py` with `TicketWorkflow.process_ticket` | Done. |
| Services created once in `__init__` | Done. |
| New `workflow_record_id` for every call, never taken from the request | Done. `uuid4()`. |
| Routing and summarization run in parallel | Done. `ThreadPoolExecutor`, as in `parallelism_example.py`. |
| Routing result does not control retrieval or the LLM | Done. Both paths are submitted before either is awaited. |
| Same unchanged `Body` sent to routing and retrieval, returned as `ticket_body` | Done. |
| Bad request returns `input_rejected` before any service runs | Done. Booleans are rejected as `ticket_id`. |
| Prompt uses the Homework 5 prompt with RAG | Done. Same system prompt and ticket/article layout as `hw_5/Task6`. |
| Homework 5 model, settings and summary schema sent to the LLM | Done. `qwen2.5:1.5b-instruct-q4_K_M`, `temperature 0`, `seed 42`, `num_predict 512`. |
| Summary checked: exactly three fields, right types | Done. `_summary`. |
| Department checked against the allowed list | Done. |
| Response has exactly the contract fields | Done. `_package`. Non-success results have no partial package. |
| `trace_id` is `null` in Task 5 | Done. |

## Task 6 - Logging and tracing

| Item | Status |
| --- | --- |
| One logger created in `__init__` and reused | Done. `IndexedTraceLogger`, a subclass of the supplied `TraceLogger`. |
| One `trace_id` per `process_ticket` call, used on every record | Done. |
| Workflow start, completion and terminal status recorded | Done. |
| `started` and `completed` or `failed` around each service | Done. Routing, retrieval and LLM. |
| Elapsed time for each service and the whole workflow | Done. `elapsed_ms`. |
| Recommended department recorded | Done. On the routing `completed` record. |
| Retrieved chunk IDs recorded | Done. On the retrieval `completed` record. |
| `trace_id` in every response | Done. Including `input_rejected` and `workflow_failed`. |
| No ticket text, prompts, content, summaries, credentials or reasoning logged | Done. The subclass refuses those field names. Failures log only `error_type`. |
| Logging only through `TraceLogger` | Done. Python `logging` was removed. The `error_type` field keeps the cause in the trace. |

## Submission

| Item | Status |
| --- | --- |
| One zip named `Firstname_Lastname_HW6.zip` | Open. Not built yet. Use your Google Classroom name. |
| Folders `Task1` to `Task6` at the root | Open. Build the zip from `hw_6/Task1` to `hw_6/Task6`. |
| Code runs from the zip | Open. The code imports `hw_6.TaskN...` and `shared.classes...`, and it loads files from `hw_4` and `hw_5`. It only runs inside this repo. Either add a short `README.md` in `Task6` with the folder layout it needs, or copy the needed files into the task folders. |
| Writeups are `.md` or `.txt` | Done. |
| No extra files | Open. Leave out `__pycache__`, `workflow_trace.jsonl`, and the `Fidel Alejandro Rosell Perez - ...` copies of the supplied materials. `show_timeline.py` is optional. Keep it if you want to show the parallel run. |
| `logic.md` files and `trace_logger_improvements.md` | Your writeups. Read them and edit them in your own words before you submit. |
