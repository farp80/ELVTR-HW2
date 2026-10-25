## Reasoning

The 33 articles run from 179 to 412 words, and each one is already split into three to six headed sections. The embedding model keeps about 512 tokens. A 412-word article can lose its ending. That ending is often Limits, the part that says when the article does not apply. A section is short enough to embed whole.

The headings are already in the file, so the split stays the same if a sentence is edited. A character-count cut would move.

The Jira review-state query and the QN90A flicker query each need facts from more than one article. A section can rank on its own, so the top of the list can hold a workflow section and a mail section together.

`content` stays the source text because the store returns `content` into the prompt. `embedding_text` adds the title and product because many sections share the headings "Limits" and "What the customer provides".