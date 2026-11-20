# Homework 9 - Integrate and Extend the Application

## Goal

Turn the work from Homeworks 2 through 8 into one browser-accessible local
application. Integrate the supplied UI with the existing deployment, then design
and implement one non-trivial feature of your choosing.

## Provided Materials

| Material | Purpose |
| --- | --- |
| `materials/ui/` | Supplied `index.html`, `app.js`, and `styles.css` for the cumulative application |
| `materials/ui_workflow_api.py` | UI-serving adapter with an import placeholder for your Homework 8 app |

Bring forward your Homework 8 four-service deployment code and runtime artifacts,
including record saving, routing-review behavior, monitoring trace-event logging,
unified trace retrieval, three operational metrics, and persistent storage. Start
with fresh record and trace storage; previous homework data and volumes do not
need to be transferred or migrated.
Saved workflow records intentionally retain the original submitted ticket body for review;
monitoring, tracing, logs, errors, and metric payloads remain content-free.
Use the existing Homework 2 ticket dataset for sample inputs and the demonstration;
no additional demo-ticket file is provided.

## Part 1 - Integrate the Cumulative Application

## Task 1 - Add the Supplied UI

You have been provided an HTML/CSS/JavaScript bundle that implements a simple UI.
At a high-level, you will copy this bundle into the workflow service image, and
update HW8 workflow FastAPI app to serve the UI and its static assets. The supplied UI already
uses the previously defined API contracts and relative paths, so as long as you used the 
endpoints and field names from Homeworks 2 through 8, the UI should work with minimal changes.

### Integration Steps

1. Add the supplied UI bundle + `ui_workflow_api.py` to the location you build your workflow image from.
2. In `ui_workflow_api.py`, populate the import-placeholder. This file extends your `workflow_api.py` from
   Homework 8, and adds a new endpoint + mount to it. 
3. In `ui/app.js`, populate the `METRICS` placeholders with the three metric-name
   suffixes you implemented in Homework 8 (for example, `"workflow-success-rate"`,
   not a full URL). The UI requests `/ops/metrics/<metric_name>` and prominently
   displays scalar responses, rounding numbers to at most three decimal places.
   It displays `null` as `N/A` and objects or arrays as complete, pretty-printed JSON.
4. Use `COPY` to place the 3 UI files into the image under `/app/ui`.
5. Use `COPY` to place the supplied `ui_workflow_api.py` into the image under `/app`.
6. Update your workflow service `Dockerfile` to start `ui_workflow_api.py` instead of `workflow_api.py`.
7. From `task1/`, run `docker compose up --build` to rebuild and start the four services.
8. Go to `http://localhost:8000/` in your browser, and confirm the page loads.

Task 1 is a self-contained fresh deployment. Include the carried-forward service
code and runtime artifacts in `task1/` so all three student-built images can be
rebuilt from that directory. Use fresh persistent record and unified trace storage;
the prepared `homework7_ollama` model volume is the allowed external prerequisite.

The supplied UI uses one `GET /ops/traces?trace_id=<ID>` request for both
service logging and Homework 8 monitoring trace-events. It displays every field
in recorded order, without sorting timestamps or filtering measurements.
There is no separate event store or event-lookup endpoint.

### Deliverables

- A `task1/` directory containing the complete four-service Compose deployment: application and UI code, 
  build files, dependencies, and required local data/configuration. It must run on my computer without 
  edits to files or paths. I already have the prepared `homework7_ollama` volume defined in Homework 7, 
  so make sure your deployment mounts the `homework7_ollama` volume.

## Task 2 - Test the UI

Use the browser to check that the supplied UI works with the Task 1 deployment
of your Homework 8 application before adding your new feature.

### Requirements

1. In the "Process Ticket" tab, submit a ticket from the ticket dataset.
2. Wait for the workflow to complete, and confirm the result is displayed alongside the submission.
3. In the "Workflow Records" tab, confirm the saved record is present under "Saved records".
4. Click on the ticket, and under record details, confirm the contents are present and accurate.
5. Test various routing/department filters to ensure the ticket is included/excluded as expected.
6. In the "Record Details", ensure the department assignment panel is present and works as expected.
   The color of the dropdown-box depends on your routing-review policy; red for required, white for optional.
7. Copy the trace ID from the record details, switch to the "Operations" tab, paste it into the
   "Trace lookup", and confirm both the Homework 6 service logging and
   Homework 8 monitoring trace-events are displayed together in recorded order
   and appear reasonable.
8. In the "Operations" tab, confirm the three operational metric tiles load and display values.

## Part 2 - Design and Implement One New Feature

## Task 3 - Select and Define the Feature

Choose exactly one option below or propose an instructor-approved alternative.
The options describe expected capabilities, not prescribed implementations.
Choose a modest, non-trivial enhancement to the existing project; a large new
subsystem is not expected. Your work may improve model behavior, processing,
evaluation, or the user experience. UI changes are required only for options
that explicitly call for them.

### Option 1 - Use a More Capable LLM

Replace the small local LLM used for ticket summarization with calls to a more
capable hosted model through your personal account/subscription with API access.

- Use the new model in the project's summarization flow, preserving the structured
  summary fields expected by the rest of the application.
- Complete three rounds of prompt iteration. Evaluate the rounds on a consistent
  set of tickets so differences can be compared. Record each round's prompt,
  outputs, assessment, and reasoning behind changes.
- Demonstrate the outputs and explain what improved, what did not, and how the
  final version compares with the original local-model baseline.

### Option 2 - Find Similar Tickets

Given a new ticket, find relevant previous tickets that could help an agent
recognize a recurring issue or choose a department.

- Search a collection of existing ticket records and return ranked matches with
  their IDs, ticket text, and available routing information. Do not return the
  query record itself as a match.
- Evaluate whether the matches are useful on varied examples, including a query
  with no closely related ticket.
- Explain the basis for the ranking and its limitations. The provided dataset
  does not establish that tickets were resolved or contain verified resolutions;
  do not present retrieved tickets as proven solutions.

### Option 3 - Add Iterative Knowledge Retrieval

Extend the single-search RAG workflow with a bounded LLM-driven retrieval loop.
The model can refine its search after inspecting evidence; an agent framework
is not required.

- Have the LLM propose a search query based on the ticket. Application code
  executes the query through the existing retrieval service and returns the
  evidence to the LLM.
- After inspecting the evidence, let the LLM request another search with a
  revised query or indicate that it is done.
- Choose and enforce a small maximum of `N` retrieval rounds. Stop searching
  when the LLM indicates it is done or the limit is reached.
- After the loop, make a separate final summarization call that produces the
  existing structured summary using the available evidence. This call does not
  count toward `N` and cannot request another search. It must give a best-effort
  answer, identifying missing information rather than inventing unsupported facts.
- Demonstrate a case involving re-querying and show that the round limit is
  enforced. Compare retrieval relevance and summary quality with the original
  single-search workflow on the same tickets.

### Option 4 - Visualize Workflow Execution

Extend the supplied UI to show a visual execution graph for a selected workflow
invocation, rather than only a list of raw trace events.

- Show workflow steps and their dependencies, including the parallel routing
  and summarization branches.
- Populate each step's execution state from the selected invocation's traces.
  Distinguish successful, failed, and unexecuted steps; do not treat missing
  trace information alone as proof that a step did not run.
- Let the user select a component to inspect its recorded metadata, such as
  duration, routing scores, retrieved chunk IDs, or error information.
  Preserve access to the underlying events and do not invent missing metadata.
- Demonstrate successful and failed invocations, showing how the graph helps
  identify a slow or failing step. A static workflow diagram or restyled JSON
  alone is not sufficient. Choose your own graph layout and interaction design.

### Option 5 - Visualize Metrics Over Time

Extend the supplied UI with an interactive time-series graph for one existing
operational metric, such as workflow duration, success rate, or routing-review rate.

- Add a separate endpoint that returns the metric aggregated into defined time
  buckets. Preserve the existing scalar endpoint so the metric cards keep working.
- Compute the series from the underlying traces or saved results, preserving the
  metric's definition and filtering semantics. Define the bucket size and boundaries
  so each eligible observation belongs to exactly one bucket.
- Display the series in an interactive graph with a selectable time range and
  inspectable point values. Handle empty buckets and no-data ranges explicitly;
  do not represent undefined values as measured zeros.
- Demonstrate a pattern visible in the graph and verify plotted values against
  the underlying data. Choose your own metric, bucket size, and graphing library;
  a full monitoring dashboard is not expected.

### Option 6 - Route Tickets with an LLM

Build a standalone ticket router using a more capable hosted LLM through your
personal account with API access. Focus on engineering and improving the routing
prompt, rather than integrating a replacement classifier into the application.

- Accept ticket text as the input and produce a validated department from the
  existing label set.
- Complete three rounds of prompt iteration using a consistent set of labeled
  development tickets. Record each round's prompt, predictions, assessment, and
  reasoning behind changes. Do not provide the target ticket's correct label
  as part of its routing input.
- Evaluate the final prompt on a separate labeled sample not used for prompt
  development. Compare its routing accuracy with the existing classifier on
  those same tickets, and discuss correct predictions and misclassifications.
- Demonstrate the standalone implementation and the results across all three
  rounds. Integration with the workflow, class scores, routing-review policy,
  and UI is not required.

### Option 7 - Rerank Retrieved Evidence

Improve evidence selection by applying a second relevance-ranking step to a
larger set of candidates from the existing knowledge-base retrieval.

- Retrieve a larger candidate pool, rerank it using a distinct relevance
  assessment, and select the passages to pass to summarization. Choose your own
  reranking method; a dedicated reranking model is one option.
- Compare against the original retrieval on the same queries and with the same
  final passage count, so supplying more context does not explain the difference.
  Changing only the retrieval count does not qualify.
- Evaluate passage relevance and the effect on resulting summaries. Demonstrate
  examples where reranking changes the selected evidence, and discuss its
  limitations and additional processing cost.

### Option 8 - Combine Keyword and Semantic Retrieval

Add keyword-based knowledge retrieval alongside the existing semantic search,
then combine their scores to select evidence. This can help with exact product
names, error codes, or technical terms that semantic retrieval may miss.

- Implement both retrieval paths and a combined ranking. Explain how you make
  their scores comparable and weight their relative contributions.
- Try several weightings on a consistent set of development queries and use
  relevance evidence to select a weighting, rather than choosing it arbitrarily.
- Evaluate the selected weighting on separate queries not used for tuning,
  comparing against the original semantic-only retrieval with the same final
  passage count.
- Demonstrate queries where keyword and semantic retrieval disagree, and explain
  what the combined ranking gains or loses. Improvement is not guaranteed;
  conclusions should follow the evaluation results.

### Feature Definition Requirements

- State what you will add or improve, why it is useful, and how it relates to
  the existing project.
- Define a bounded scope and explain your chosen approach, including the
  components, data, models, or external services involved.
- Define how you will test or evaluate the enhancement and demonstrate its
  results. Choose examples and comparison criteria appropriate to your feature.
- Identify any additional dependencies or access needed to run it.

### Task 3 Deliverables

- A short feature definition document containing the information above.
- Instructor approval, if implementing an alternative feature.

## Task 4 - Implement the Feature

Implement the enhancement defined in Task 3.

### Requirements

- Implement the enhancement according to your Task 3 definition and approach.
- Check that the enhancement works and preserve the existing application's core
  functionality. Limit changes to the behavior intentionally addressed by your
  feature.
- Keep credentials out of submitted code and artifacts.

### Deliverables

- Implementation code and any prompts, dependencies, data, or configuration
  needed for the enhancement, excluding credentials.
- Instructions for running the enhancement with its stated dependencies and
  any required external access.

## Task 5 - Evaluate and Demonstrate the Feature

Evaluate and demonstrate the enhancement using the examples and criteria
defined in Task 3.

### Requirements

- For UI changes, show what changed and demonstrate how it works.
- For model, prompt, retrieval, or similar changes, present evaluation results
  comparing the original and changed behavior on consistent examples. Include
  results from the iterations or tuning required by your selected option.
- Use a demonstration format appropriate to the feature, such as the UI, API
  calls, a script, a notebook, or a comparison of model outputs. Features that
  combine UI and model or processing changes should demonstrate both.
- Explain the impact of the changes, whether they achieved the intended
  improvement, and one important limitation or tradeoff.

### Deliverables

- A concise demonstration and supporting evaluation results, as appropriate to
  the feature, showing the changes and their impact. Include artifacts that can
  be reviewed from the submission, such as screenshots, a recording, or saved
  outputs with an explanation.

## Submission Guidelines

- Submit the complete homework as one `.zip` file. Do not submit individual
  files or multiple `.zip` files.
- Name the archive `Firstname_Lastname_HW9.zip`, using the same first and last
  name shown in Google Classroom. For example: `Tanner_Gilligan_HW9.zip`.
- Organize the archive with one folder per task that has submitted deliverables
  at its root. Each task folder should contain that task's deliverables:

  ```text
  Tanner_Gilligan_HW9.zip
  |-- task1/
  |-- task3/
  |-- task4/
  `-- task5/
  ```

- Task 2 is a browser check with no submitted deliverables; omit its folder.
- Upload the `.zip` file itself. Do not submit a Google Drive, GitHub, or other
  external link in place of the file.
- Submit data tables as static CSV files, not Excel files or links to Google
  Sheets.
- Submit writeups as `.txt` or `.md` files.
- Do not include duplicate or extraneous files unless they are relevant to
  running or interpreting your submission.
