# Task 7 - RAG outputs (k = 5)

## Ticket 28763 - Supported request

### Retrieved chunks

Rank 1 - KB-SAM-TV-001-0 (distance 0.1211)
## Symptoms

Use this article when a Samsung QN90A owner reports intermittent screen
flicker, brightness pulsing, or rapid flashing that disrupts viewing. The goal
is to separate input-related behavior from a likely panel or control-board issue
without asking the customer to open the television or perform unsafe hardware
work.

Rank 2 - KB-SAM-TV-001-1 (distance 0.1263)
## Safe checks the customer can perform

Ask the customer to note whether the flicker appears on every source or only on
one device. A useful first check is opening the TV home menu or a built-in app;
if flicker is visible there as well, the problem is less likely to be caused by
an external cable or player. For external sources, the customer can reseat the
HDMI cable, try a known-good cable, and temporarily set the source output to a
standard refresh rate such as 60 Hz.

The customer may also power the TV off, unplug it for one minute, and reconnect
it directly to a wall outlet if it was previously attached to a power strip.
Picture settings that aggressively alter brightness can be turned off for
testing, including contrast enhancer and motion smoothing. These checks are safe
because they are reversible and do not require service access.

Rank 3 - KB-SAM-TV-001-2 (distance 0.1300)
## What support provides

Support interprets the results. If flicker persists on the built-in menu,
continues after a clean power cycle, and is unaffected by input changes, support
should treat the case as a likely hardware-path issue that needs warranty
routing or technician assessment. If the flicker happens only with one source,
support can narrow the next step to cabling or source configuration rather than
the display assembly.

Rank 4 - KB-SAM-TV-001-3 (distance 0.1627)
## Limits and escalation

Do not ask the customer to remove the back cover, press on the panel, reseat
internal boards, or repeatedly factory-reset the unit. Escalate to authorized
service when the symptom persists after the safe checks above, when the screen
shows flicker before any external source is selected, or when the problem has
become more frequent over time.

Rank 5 - KB-SAM-NEG-001-2 (distance 0.1929)
## What support provides

Support interprets the results and decides whether the next step is audio
configuration review, accessory isolation, or hardware service for the audio
path. Picture flicker, backlight pulsing, and display artifacts are outside the
scope of this article.

### Generated summary

- summary: The customer's Samsung QLED QN90A TV is experiencing persistent flickering issues, which they believe is a hardware-related problem.
- customer_request: I need help resolving the flickering issue on my Samsung QLED QN90A TV. I've tried adjusting brightness and refreshing the support software, but it hasn't resolved the problem. I'm looking for guidance on how to diagnose and fix this issue, and I'd appreciate information about your repair policies and warranty coverage.
- missing_information: ["The specific source of the flickering issue, whether it's intermittent or persistent, and whether it occurs on every source or only on one device."]

## Ticket 29206 - Supported multi-source request

### Retrieved chunks

Rank 1 - KB-JIRA-001-2 (distance 0.1324)
## What support provides

Support confirms that Jira 8.20 can host a revised priority scheme without a
plugin for the core priority field itself. Before implementation, support
advises taking a configuration snapshot and testing the new values in staging
when available. The normal sequence is to create or rename priority values,
confirm their display order, map any dependent boards or filters that reference
old names, and then verify that issue creation and search still behave as
expected.

If the customer asks for dynamic reprioritization tied to project state or
business goals, support should treat that as a second decision point. Basic
priority changes are straightforward; automatic priority changes require an
approved ruleset and separate review of whether native automation already in
place can support it.

Rank 2 - KB-JIRA-002-0 (distance 0.1426)
## Overview

This article supports Jira 8.20 requests to add statuses, modify transitions,
or align workflow conditions with a new ticket handling policy. It is commonly
retrieved alongside the custom priority article because teams often need both
sets of changes to reflect a revised issue process.

Rank 3 - KB-JIRA-001-0 (distance 0.1600)
## Overview

Use this article when a Jira Software 8.20 customer wants to change issue
priority options so they match a new internal prioritization policy. The base
platform supports custom priorities, but support should collect the approved
priority matrix before advising on implementation.

Rank 4 - KB-JIRA-001-3 (distance 0.1664)
## Planning estimate

After receiving the approved matrix, affected-project list, and test access,
support can normally configure and validate a basic priority scheme within
three business days. That estimate excludes workflow conditions and automatic
reprioritization. Support owns the final estimate after reviewing dependent
filters and automations; the customer supplies constraints and an acceptable
change window rather than calculating the schedule.

Rank 5 - KB-JIRA-001-1 (distance 0.1711)
## What the customer provides

The customer should provide the approved list of priority names, definitions,
and intended order from highest to lowest urgency. Support also needs to know
which projects are affected, whether the customer uses a staging environment,
and who has Jira administrator access to make the change safely. If the
customer wants issue priority to influence automation or workflow behavior,
those downstream rules should be described separately.

The customer is not expected to know the exact configuration screens or whether
plugins are required for the basic priority list change.

### Generated summary

- summary: The customer requests modifications to Jira Software 8.20 workflows to align with new company policies regarding ticket prioritization and dynamic adjustments based on project status and goals.
- customer_request: We need to adjust the prioritization settings within Jira to reflect our new company policies and implement a feature that allows for dynamic adjustments based on the real-time status of issues and overarching project goals. We are looking for guidance on the best approach for implementing these workflow modifications.
- missing_information: ['The approved list of priority names, definitions, and intended order from highest to lowest urgency.', 'Which projects are affected?', 'Whether the customer uses a staging environment.', 'Who has Jira administrator access to make the change safely.', 'Whether issue priority should influence automation or workflow behavior.', 'Exact configuration screens or plugins required for the basic priority list change.']

## Ticket 28921 - Unsupported request

### Retrieved chunks

Rank 1 - KB-DASH-NEG-001-1 (distance 0.2384)
## What the customer provides

The customer should describe which report or dashboard needs improvement, who
uses it, and what decision the new view is supposed to support. If they want a
new metric, support needs the business definition, desired grouping, and how the
result would be judged successful. Screenshots of the current layout help, but a
finished design mockup is not required.

Rank 2 - KB-DASH-NEG-001-2 (distance 0.2545)
## What support provides

Support logs the enhancement request, checks whether the desired change fits the
current product area, and identifies whether the request is a small field-level
adjustment or a broader product change. Support may clarify intake questions and
route the request to product review. Product review, rather than intake support,
decides whether the request enters the roadmap and whether further discovery is
needed.

If the customer asks for a more intuitive layout, support can capture which
screens are confusing and which reporting outcomes are currently hard to reach.
That information helps product review understand the request, but it is still an
intake artifact rather than a design decision. Support-owned actions here are
logging, categorizing, and routing the request, not promising scope or schedule.

Rank 3 - KB-CONSULT-001-1 (distance 0.2631)
## What the customer provides

The customer should provide a short description of the problem they want the
consultation to address, the systems or teams involved, any target date that is
driving urgency, and the names of the people who should attend. Helpful intake
details include whether the request is exploratory or tied to an active pain
point, the current size of the environment, and any known change restrictions.
For architecture or workflow requests, the customer should also share the
current-state summary they already have, even if it is incomplete.

The customer is not expected to arrive with a finished solution, a final
priority matrix, or a vendor selection. Missing discovery details can delay a
recommendation, but they do not prevent support from opening the consultation
track and reserving time with the right specialist.

Rank 4 - KB-DASH-NEG-001-0 (distance 0.2654)
## Overview

Use this article when a customer requests additional dashboard views, revised
report layouts, or new summary metrics in an existing business application. The
article is an intake guide for scoping one reporting surface before product
review.

Rank 5 - KB-CONSULT-002-1 (distance 0.2835)
## What the customer provides

The customer should provide the channels where requests currently arrive, the
main categories of work they want tracked, and how they want urgent versus
routine issues distinguished. If they already use approval steps, escalation
paths, or service targets, those should be shared as part of intake. For teams
that mention upgrade handling, support also needs to know whether upgrades are
approved in one queue, in a separate change flow, or outside the ticketing
system today.

The customer does not need to propose a final workflow diagram. The point of
discovery is to uncover it.

### Generated summary

- summary: The customer requests a redesign of the internal human resources management system's user interface and enhanced data analysis capabilities to improve user experience and efficiency.
- customer_request: I am requesting a significant enhancement to our internal human resources management system, focusing on the user interface design and data analysis capabilities. We believe these improvements can help our team navigate through various modules more easily and access crucial information more quickly. Additionally, implementing advanced data analysis tools would allow our HR team to perform more detailed assessments and generate reports with greater ease.
- missing_information: ['Desired grouping for the new metric', 'Judgment criteria for the new view', 'Current layout screenshots']
