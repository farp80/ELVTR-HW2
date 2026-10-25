# Task 1 — Rubric

## Logic

The rubric has four dimensions. Score each 0, 0.5, or 1.
**Higher is better**

### Grounded ###
**What it measures:** Does the output say only what the ticket body says?
**Scores and criteria:** 
- `1`: all of it is in the body.
- `0.5`: one word shifts and the case stays the same. 
- `0`: a fact, a fix, or a department was added.

### Request coverage. ###
**what it mesures:** `customer_request` holds every ask and every question. 
**Scores and criteria:**
- `1`: every ask is there. 
- `0.5`: the main ask is there and one ask is missing. 
- `0`: the main ask is missing.

### Missing information.###
**What it measures:** The list names facts the customer left out and an agent needs. 
**Scores and criteria:**
- `1`: those gaps are listed, or the list is empty because no gap is clear. 
- `0.5`: the list is empty and a gap is clear.
- `0`: an item repeats a question or a fact already in the body.

 ### Summary job. ###
 **What it measures:** `summary` states the issue in one or two sentences and differs from `customer_request`. 
 **Scores and criteria:**
- `1`: the product or system, the issue, and any tried step that belongs to the issue are clear. 
- `0.5`: the two fields match, or a tried step is left out.
- `0`: the issue is missing.

A missing JSON field scores 0 on every dimension.