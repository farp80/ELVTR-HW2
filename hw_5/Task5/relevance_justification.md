# Task 5 — Why each retrieved chunk is relevant or not

The labels are in `retrieval_results.json`. A row is `true` when the chunk text helps answer that query, including a partial answer. A row is `false` when the text is only about a nearby subject. Rank and distance are not part of the decision.

## Q001

Query: is there a current regional incident in the eu-west managed environment, and when was its status last updated?

The two facts that count are an open or current incident (or current health) and the time of the last status update. A scheduled maintenance notice does not supply either fact.

| Rank | Chunk | Label | Reason |
| --- | --- | --- | --- |
| 1 | KB-AWS-MAINT-001-0 | false | Scheduled window for `AMS-2023-Q4-NET-17` on 18 November 2023. It is a planned change, not a current incident, and it gives no last-update time. |
| 2 | KB-AWS-MAINT-001-1 | false | Expected impact during that same maintenance window. Delayed dashboards are a side effect of the planned event. |
| 3 | KB-AWS-MAINT-001-2 | false | Says maintenance updates are posted at start, every 30 minutes, and at completion. That schedule belongs to the named event, not to a current regional incident. |
| 4 | KB-AWS-NEG-003-2 | false | Tells the agent which details to collect from the customer. It does not say whether an incident is open or when status was published. |
| 5 | KB-AWS-NEG-003-0 | true | States that this article is for current platform status and for whether the service is presently healthy, degraded, or recovering. That is the first question. |
| 6 | KB-AWS-NEG-003-1 | true | States that support can say whether an unscheduled incident is open and can give the time of the last published update. That is both questions. |
| 7 | KB-AWS-MAINT-002-1 | false | Preparation steps before the same scheduled maintenance window. |
| 8 | KB-CONSULT-003-3 | false | Routes a long server outage to operations. It is not an AWS regional incident status. |
| 9 | KB-AWS-NEG-002-2 | false | Cost-alert thresholds and a six-hour spend check. Not service health. |
| 10 | KB-CONSULT-003-1 | false | Evidence to collect for a latency consultation. |

## Q002

Query: which workflow settings and which mail-routing settings must be handled separately when adding a Jira review state that emails a project role?

A chunk is `true` if it covers the workflow change, the mail routing, or the fact that those two are different objects.

| Rank | Chunk | Label | Reason |
| --- | --- | --- | --- |
| 1 | KB-JIRA-NEG-001-2 | true | Limits the change to mail routing and says to separate the mail event from the workflow step. |
| 2 | KB-JIRA-002-2 | true | Covers the workflow half: new statuses, transitions, and conditions in Jira 8.20. |
| 3 | KB-JIRA-002-3 | true | Says this workflow article does not cover notification changes, so mail is a separate configuration. |
| 4 | KB-JIRA-002-1 | true | Names the workflow pieces required to add a state: workflow name, statuses, and allowed transitions. |
| 5 | KB-JIRA-NEG-001-1 | true | Says the notification scheme and the workflow are different objects, and asks which role should receive the mail. |
| 6 | KB-JIRA-002-0 | true | Overview of adding statuses and changing transitions for a new handling policy. |
| 7 | KB-JIRA-NEG-002-3 | false | Separates permissions from workflow redesign. The query asks about mail versus workflow, not permissions. |
| 8 | KB-JIRA-NEG-002-2 | false | Permission scheme and role membership. It does not add a review state or route mail. |
| 9 | KB-JIRA-NEG-002-0 | false | Who can browse or transition issues. Same neighbor topic as ranks 7 and 8. |
| 10 | KB-JIRA-001-2 | false | Custom priority values. Not a workflow state and not mail routing. |

## Q003

Query: the router order is still editable. Change the destination, and say whether expedited service is still available after that change.

A chunk is `true` if it covers the address change, the expedited shipping choice, or both.

| Rank | Chunk | Label | Reason |
| --- | --- | --- | --- |
| 1 | KB-SHIP-NEG-001-2 | true | Address can be updated before carrier handoff, and support must say whether the order is still editable. |
| 2 | KB-SHIP-NEG-001-1 | true | The address change needs the order number, the new address, and whether the order has shipped. |
| 3 | KB-SHIP-NEG-001-3 | false | Only says this article does not estimate future delivery or create tracking numbers. |
| 4 | KB-SHIP-001-4 | false | Refuses address changes after handoff and points to a different process. It does not say how to change an editable order or whether expedited remains. |
| 5 | KB-SHIP-NEG-001-0 | true | This article is the address change, and it says shipping speed is a separate question. |
| 6 | KB-SHIP-001-3 | true | Support confirms which shipping methods are available for the destination. That is the expedited half. |
| 7 | KB-SHIP-001-1 | true | Defines expedited delivery as two to three business days, distinct from ground and overnight. |
| 8 | KB-CISCO-NEG-001-2 | false | Firmware upgrade path for an ISR4331. The query is about the order, not the router software. |
| 9 | KB-CONSULT-002-1 | false | Intake for a ticketing-workflow consultation. |
| 10 | KB-SHIP-001-2 | true | To quote delivery, support needs the destination and whether the customer wants standard, expedited, or priority. |

## Q004

Query: a QN90A flickers on internal menus. Give safe diagnostic steps, and compare the still-open store return with manufacturer technician service.

A chunk is `true` if it gives safe flicker checks, the store-return route, or the technician route.

| Rank | Chunk | Label | Reason |
| --- | --- | --- | --- |
| 1 | KB-SAM-TV-001-2 | true | Flicker on the built-in menu, after a power cycle, points to warranty routing or a technician. |
| 2 | KB-SAM-TV-001-3 | true | Lists the unsafe steps to avoid and when to escalate to authorized service. |
| 3 | KB-SAM-TV-001-1 | true | The safe checks: built-in menu, HDMI, refresh rate, power cycle, and reversible picture settings. |
| 4 | KB-SAM-TV-001-0 | true | Matches QN90A flicker and says to separate input problems from a panel fault without opening the set. |
| 5 | KB-SAM-NEG-001-2 | false | Audio article. It says picture flicker is out of scope and gives no flicker steps. |
| 6 | KB-SAM-NEG-001-3 | false | Tells the agent to leave the audio flow when the symptom is menu flicker. It does not provide the checks or the return comparison. |
| 7 | KB-SAM-TV-002-1 | true | Technician and warranty intake, including proof of purchase and whether the built-in menu flickers. |
| 8 | KB-SAM-NEG-002-3 | true | Store-return article: it does not authorize a technician, and after the return window the case moves to warranty. That is the comparison of the two routes. |
| 9 | KB-SAM-NEG-001-1 | false | Safe checks for audio dropouts and eARC, not for menu flicker. |
| 10 | KB-SAM-NEG-001-0 | false | Sound cuts out while the picture stays stable. The opposite symptom. |

## Q005

Query: enroll a new hardware security key for multifactor authentication, and revoke the employee's lost authenticator.

No retrieved chunk describes a hardware security key or revoking an authenticator. Password reset, hardware returns, subscription cancellation, and router specs are neighbors. Every row is `false`.

| Rank | Chunk | Label | Reason |
| --- | --- | --- | --- |
| 1 | KB-SHIP-002-1 | false | 30-day hardware return eligibility. Not an authenticator. |
| 2 | KB-DIST-001-2 | false | Password reset. "Update multifactor settings at the next sign-in" is not enrolling a hardware key or revoking a lost authenticator. |
| 3 | KB-SHIP-002-3 | false | Issuing an RMA and inspecting returned hardware. |
| 4 | KB-DIST-001-0 | false | Overview of a password reset and identity check. |
| 5 | KB-DIST-001-1 | false | Account identifier, email, and an identity-check detail for a password reset. |
| 6 | KB-SHIP-002-0 | false | Returns of networking hardware after delivery. |
| 7 | KB-SHIP-002-2 | false | Order number and serial number for a hardware return. |
| 8 | KB-DIST-002-3 | false | Subscription cancellation limits. |
| 9 | KB-CISCO-001-2 | false | ISR4331 modules and compatibility. |
| 10 | KB-DIST-001-3 | false | Password-reset article does not unlock contracts or override identity controls. |

## Counts

| Query | Relevant in the top 10 |
| --- | --- |
| Q001 | 2 (ranks 5 and 6) |
| Q002 | 6 (ranks 1 through 6) |
| Q003 | 6 (ranks 1, 2, 5, 6, 7, and 10) |
| Q004 | 6 (ranks 1, 2, 3, 4, 7, and 8) |
| Q005 | 0 |
