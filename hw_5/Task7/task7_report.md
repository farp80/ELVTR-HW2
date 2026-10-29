# Task 7 - RAG summaries on three tickets

k = 5 (see `Task6/Task6_Selection_Reasoning.md`). Rubric: `Task2/rubric_frozen.md`. No-RAG scores: `Task2/scoring.md`.

Where the values come from:
- Retrieved chunks and generated summaries: `task7_outputs.md` and `task7_results.json`, written by `task.py`.
- Scores: I read each output and the unaltered ticket body, then applied the frozen rubric by hand.
- No-RAG scores: copied from `Task2/scoring.md`.

Scores are on a 0, 0.5, 1 scale. The total is out of 4.

## Ticket 28763 - Supported request

### Retrieval results

Ranks 1 to 4 are the four chunks of `KB-SAM-TV-001` (Samsung QN90A flicker): symptoms, safe checks, what support provides, and limits. Distances run from 0.121 to 0.163. Rank 5 is `KB-SAM-NEG-001-2` (distance 0.193), an audio article that says picture flicker is outside its scope. Retrieval is good here. Only rank 5 is noise.

### Generated summary

The summary says the QN90A has persistent flickering that the customer thinks is hardware. The request keeps the tried steps and asks for diagnosis help, repair policies, and warranty coverage. `missing_information` has one item about the flicker source.

### Grading

- Grounded: 1. Every statement is in the body ("persistent", "hardware-related", "adjusting brightness", "refreshing the support software").
- Request coverage: 1. It has the diagnosis guidance, the repair policies, and the warranty coverage.
- Missing information: 0. The item says "whether it's intermittent or persistent". The body already says the flicker is intermittent. The rubric gives 0 when an item repeats a fact from the body. The real gaps (purchase date, order number) are not named.
- Summary job: 0.5. The summary leaves out the tried steps (cables, power, brightness, software).

Total: 2.5 of 4.

### Comparison with no-RAG

No-RAG scored 3.0. RAG scored 2.5. Missing information fell from 0.5 to 0. The other three scores did not change. The article chunk about "every source or only one device" pushed the model to ask a question the body had already answered.

## Ticket 29206 - Supported multi-source request

### Retrieval results

All five chunks are Jira articles. Ranks 1, 3, 4, and 5 are `KB-JIRA-001` (custom priority: what support provides, overview, planning estimate, what the customer provides). Rank 2 is `KB-JIRA-002-0` (workflow statuses and transitions). Distances run from 0.132 to 0.171. Retrieval is good, but four of the five chunks come from one article. The workflow article got one slot.

### Generated summary

The summary names Jira 8.20 workflow changes for the new prioritization policy. The request is short: adjust prioritization settings, add dynamic adjustment, and give guidance. `missing_information` has six items copied from the "What the customer provides" chunk.

### Grading

- Grounded: 1. The summary and the request say only what the body says. The six gap items are questions, not statements.
- Request coverage: 0. I count 9 asks in the body. The output has 4: priority settings, dynamic adjustment, workflow changes, and guidance. Feasibility, timelines, plugin help, documentation, and the meeting are gone. Four of nine is under half.
- Missing information: 0. The last item asks for "plugins required". The body already asks about plugins. The fifth item repeats the body's wish for dynamic adjustment.
- Summary job: 1. It names Jira 8.20 and the policy problem in its own words.

Total: 2.0 of 4.

### Comparison with no-RAG

No-RAG scored 3.0. RAG scored 2.0. Request coverage fell from 0.5 to 0, because the output now holds 4 of 9 asks and not 6. Missing information fell from 0.5 to 0. The articles gave the model a long list of gaps to copy, and it spent its words there.

## Ticket 28921 - Unsupported request

### Retrieval results

No article covers an HR system redesign. Distances run from 0.238 to 0.284, the weakest of the three tickets. Ranks 1, 2, and 4 are `KB-DASH-NEG-001` (dashboard and report enhancement intake). Ranks 3 and 5 are consulting intake chunks. The dashboard article is the closest match, but it is about a different subject.

### Generated summary

The summary and the request restate the redesign and the data analysis wish, using the body's words. `missing_information` has three items: "Desired grouping for the new metric", "Judgment criteria for the new view", and "Current layout screenshots". The first two use words from the dashboard article.

### Grading

- Grounded: 0.5. The summary and the request stay in the body, so the weak chunks did not leak into them. The gap items say "new metric" and "new view". The body never asks for either word.
- Request coverage: 0.5. It has 2 of 3 asks. The plan and timeline ask is missing.
- Missing information: 1. The list is not empty and repeats nothing from the body. "Current layout screenshots" is a real gap. The other two items are weak. The gaps named in Task 2 (which modules, which reports) are not listed.
- Summary job: 0.5. It states the wish and "improve efficiency", but not the problem: staff struggle to find information.

Total: 2.5 of 4.

### Comparison with no-RAG

No-RAG scored 2.0. RAG scored 2.5. Only Missing information moved, from 0.5 to 1. That gain is thin. The items came from an unrelated article, not from the body. Review this grade before you trust it.

## Overall

The average total is 2.33 with RAG and 2.67 without. RAG is lower on two tickets and higher on one.

Tickets with a good match (28763 and 29206) lost points on Missing information. The model copied the "customer provides" lists from the articles, and some items repeated the body. On 28921 the model kept article facts out of the summary and the request. That is the behavior the prompt asks for.

The weak model is the main limit. This matches the assignment note that RAG may not beat no-RAG.

Grades are my reading of the rubric. Read them and change any you disagree with.
