# Task 7 - RAG summaries on three tickets

k = 5 (see `Task6/Task6_Selection_Reasoning.md`). Rubric: `Task2/rubric_frozen.md`. No-RAG scores: `Task2/scoring.md`.

Scores are on a 0, 0.5, 1 scale. The total is out of 4.

## How these scores were made

**Retrieved chunks and generated summaries.** `task7_outputs.md` and `task7_results.json`, written by `task.py`.

**RAG scores.** I read each output and the unaltered ticket body, then applied the frozen rubric by hand.

**No-RAG scores.** Copied from `Task2/scoring.md`.

## Ticket 28763 - Supported request

### Retrieval results

**Rank 1.** `KB-SAM-TV-001-0`, distance 0.121. QN90A flicker: symptoms.

**Rank 2.** `KB-SAM-TV-001-1`, distance 0.126. QN90A flicker: safe checks.

**Rank 3.** `KB-SAM-TV-001-2`, distance 0.130. QN90A flicker: what support provides.

**Rank 4.** `KB-SAM-TV-001-3`, distance 0.163. QN90A flicker: limits.

**Rank 5.** `KB-SAM-NEG-001-2`, distance 0.193. Audio article. Picture flicker is outside its scope.

Ranks 1 to 4 are the matching article. Only rank 5 is noise.

### Generated summary

**summary.** The QN90A has persistent flickering that the customer thinks is hardware.

**customer_request.** Keeps the tried steps and asks for diagnosis help, repair policies, and warranty coverage.

**missing_information.** One item about the flicker source.

### Grading

**Grounded: 1.** Every statement is in the body ("persistent", "hardware-related", "adjusting brightness", "refreshing the support software").

**Request coverage: 1.** It has the diagnosis guidance, the repair policies, and the warranty coverage.

**Missing information: 0.** The item says "whether it's intermittent or persistent". The body already says the flicker is intermittent. The rubric gives 0 when an item repeats a fact from the body. The real gaps (purchase date, order number) are not named.

**Summary job: 0.5.** The summary leaves out the tried steps (cables, power, brightness, software).

**Total: 2.5 of 4.**

### Comparison with no-RAG

**Grounded.** No-RAG 1. RAG 1. Same.

**Request coverage.** No-RAG 1. RAG 1. Same.

**Missing information.** No-RAG 0.5. RAG 0. Fell. The article chunk about "every source or only one device" pushed the model to ask a question the body had already answered.

**Summary job.** No-RAG 0.5. RAG 0.5. Same.

**Total.** No-RAG 3.0. RAG 2.5. RAG is lower.

## Ticket 29206 - Supported multi-source request

### Retrieval results

**Rank 1.** `KB-JIRA-001-2`, distance 0.132. Custom priority: what support provides.

**Rank 2.** `KB-JIRA-002-0`, distance 0.143. Workflow statuses and transitions.

**Rank 3.** `KB-JIRA-001-0`, distance 0.160. Custom priority: overview.

**Rank 4.** `KB-JIRA-001-3`, distance 0.166. Custom priority: planning estimate.

**Rank 5.** `KB-JIRA-001-1`, distance 0.171. Custom priority: what the customer provides.

All five chunks are Jira articles. Four come from `KB-JIRA-001`. The workflow article got one slot.

### Generated summary

**summary.** Names Jira 8.20 workflow changes for the new prioritization policy.

**customer_request.** Adjust prioritization settings, add dynamic adjustment, and give guidance.

**missing_information.** Six items copied from the "What the customer provides" chunk.

### Grading

**Grounded: 1.** The summary and the request say only what the body says. The six gap items are questions, not statements.

**Request coverage: 0.** The body has 9 asks. The output has 4: priority settings, dynamic adjustment, workflow changes, and guidance. Feasibility, timelines, plugin help, documentation, and the meeting are gone. Four of nine is under half.

**Missing information: 0.** The last item asks for "plugins required". The body already asks about plugins. The fifth item repeats the body's wish for dynamic adjustment.

**Summary job: 1.** It names Jira 8.20 and the policy problem in its own words.

**Total: 2.0 of 4.**

### Comparison with no-RAG

**Grounded.** No-RAG 1. RAG 1. Same.

**Request coverage.** No-RAG 0.5. RAG 0. Fell. The output now holds 4 of 9 asks, not 6.

**Missing information.** No-RAG 0.5. RAG 0. Fell. The articles gave the model a long list of gaps to copy, and it spent its words there.

**Summary job.** No-RAG 1. RAG 1. Same.

**Total.** No-RAG 3.0. RAG 2.0. RAG is lower.

## Ticket 28921 - Unsupported request

### Retrieval results

**Rank 1.** `KB-DASH-NEG-001-1`, distance 0.238. Dashboard and report enhancement intake.

**Rank 2.** `KB-DASH-NEG-001-2`, distance 0.255. Dashboard and report enhancement intake.

**Rank 3.** `KB-CONSULT-001-1`, distance 0.263. IT consulting scheduling and intake.

**Rank 4.** `KB-DASH-NEG-001-0`, distance 0.265. Dashboard and report enhancement intake.

**Rank 5.** `KB-CONSULT-002-1`, distance 0.284. Ticketing workflow discovery intake.

No article covers an HR system redesign. These are the weakest distances of the three tickets. The dashboard article is the closest match, and it is about a different subject.

### Generated summary

**summary.** Restates the redesign and the data analysis wish, using the body's words.

**customer_request.** Same wish, in the body's words.

**missing_information.** "Desired grouping for the new metric", "Judgment criteria for the new view", and "Current layout screenshots". The first two use words from the dashboard article.

### Grading

**Grounded: 0.5.** The summary and the request stay in the body, so the weak chunks did not leak into them. The gap items say "new metric" and "new view". The body never uses either phrase.

**Request coverage: 0.5.** It has 2 of 3 asks. The plan and timeline ask is missing.

**Missing information: 1.** The list is not empty and repeats nothing from the body. "Current layout screenshots" is a real gap. The other two items are weak. The gaps named in Task 2 (which modules, which reports) are not listed.

**Summary job: 0.5.** It states the wish and "improve efficiency", but not the problem: staff struggle to find information.

**Total: 2.5 of 4.**

### Comparison with no-RAG

**Grounded.** No-RAG 0.5. RAG 0.5. Same.

**Request coverage.** No-RAG 0.5. RAG 0.5. Same.

**Missing information.** No-RAG 0.5. RAG 1. Rose. The gain is thin. The items came from an unrelated article, not from the body.

**Summary job.** No-RAG 0.5. RAG 0.5. Same.

**Total.** No-RAG 2.0. RAG 2.5. RAG is higher on this ticket only.

## Overall

### 28763 Supported request

No-RAG 3.0. RAG 2.5.

### 29206 Supported multi-source request

No-RAG 3.0. RAG 2.0.

### 28921 Unsupported request

No-RAG 2.0. RAG 2.5.

### Mean

No-RAG 2.67. RAG 2.33.

RAG is lower on two tickets and higher on one.

Tickets with a good match (28763 and 29206) lost points on Missing information. The model copied the "customer provides" lists from the articles, and some items repeated the body. On 28921 the model kept article facts out of the summary and the request. That is the behavior the prompt asks for.

The weak model is the main limit. This matches the assignment note that RAG may not beat no-RAG.
