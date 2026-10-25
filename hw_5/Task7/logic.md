# Task 7 — Three RAG summaries

## Logic

Run the Task 6 prompt on the unaltered Body of tickets 28763, 29206, and 28921. For each ticket, save the retrieved chunks, the summary JSON, the four rubric scores, and the Task 2 scores beside them. Under the pair of scores, write what changed in each field.

Score with the frozen Task 2 rubric.

28763 is one supported subject. The knowledge base has QN90A flicker checks and warranty routing. 29206 is a supported subject that spans articles. Jira 8.20 workflows, custom priorities, and notification or role rules can all apply. 28921 is unsupported. An HR screen redesign has no article. On 28921, Grounded scores 1 when the summary leaves out chunks about a different subject.

Record the scores the rubric gives, including a tie or a lower score.

## Reasoning

One prompt faces three retrieval situations. 28763 should receive articles about that television. 29206 should receive more than one Jira article, which is why k has to reach a second source. 28921 should receive weak matches. The prompt rule that skips an unrelated article is what keeps those matches out of the summary.

Homework 4 already showed this model skips missing details when the prompt tells it to list them. A flat or lower RAG score is a valid result. The required work is the side-by-side comparison on the frozen rubric.
