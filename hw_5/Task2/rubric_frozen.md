# Task 2 - Rubric (version 2, FROZEN)

**Status: frozen.** This is the final rubric. Do not edit it. Task 7 scores the RAG summaries with exactly this text, so RAG and no-RAG results are judged by the same rules. The edits from version 1 are listed in `scoring.md`.

## How to use it

Read the unaltered ticket `Body` first, then the output. Score each dimension 0, 0.5, or 1. Write one sentence of reason for each score and quote the body or the output.

**Gate:** if the output is not valid JSON with exactly `summary`, `customer_request`, and `missing_information`, score 0 on all four.

**Placeholders:** words like `name`, `acc_num`, `tel_num`, and `company_name` are privacy placeholders. They are never a missing detail and never an added fact.

## Grounded

**Measures:** Does the output say only what the body says? This dimension judges what is *written*. Leaving something out is scored in Request coverage, Missing information, and Summary job, not here.

### Score 1

Every statement is in the body.

### Score 0.5

One word or detail is changed, but the meaning stays the same.

### Score 0

A fact, a fix, or a department was added that the body does not contain.

## Request coverage

**Measures:** Does `customer_request` hold every ask and question?

**Method (new in version 2):** First list every ask in the body. Count them. Then count how many appear in `customer_request`. Name the main ask (the first thing the customer says they want).

### Score 1

Every ask is present.

### Score 0.5

The main ask is present and at least half of all asks are present.

### Score 0

The main ask is missing, or fewer than half of all asks are present.

## Missing information

**Measures:** Does `missing_information` name facts the customer left out and an agent needs?

**Clear gap (new in version 2):** a fact the agent must have to act (for example an order number, a date, an amount, a quantity, a warranty status) that the body does not give. The scorer must name at least one such fact when claiming a gap.

### Score 1

Real gaps are listed, or the list is empty because no clear gap exists.

### Score 0.5

The list is empty, but a clear gap exists.

### Score 0

An item repeats a question or a fact already in the body.

## Summary job

**Measures:** Does `summary` state the problem in one or two sentences, in its own words, without copying `customer_request`?

**Tried step (new in version 2):** something the customer already did to fix or check the problem, such as changing cables or refreshing software. Findings that make up the problem itself (for example an audit that found a billing difference) are part of the issue, not a tried step.

### Score 1

Product, problem, and tried steps are clear.

### Score 0.5

It copies the request, or it only restates the request without the problem behind it, or it leaves out a tried step.

### Score 0

The problem is missing.
