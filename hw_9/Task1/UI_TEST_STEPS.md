# Test the UI

Start the stack from this directory, then walk through the three tabs at `http://localhost:8000/`. The local model can take a minute on the first ticket.

```powershell
cd hw_9\Task1
docker compose up --build
```

Leave that window running. The header should say **Workflow online**.

## 1. Process a ticket

Open **Process Ticket**. Use ticket 1 from the Homework 2 dataset.

- Ticket ID: `1`
- Ticket body:

```text
Dear Customer Support Team,I am writing to report a significant problem with the centralized account management portal, which currently appears to be offline. This outage is blocking access to account settings, leading to substantial inconvenience. I have attempted to log in multiple times using different browsers and devices, but the issue persists.Could you please provide an update on the outage status and an estimated time for resolution? Also, are there any alternative ways to access and manage my account during this downtime?
```

Click **Process ticket** and wait until **Latest result** fills in beside the form. A successful run shows **Summary ready**, a department, class scores, a three-part summary, and one to five evidence chunks. Copy the trace ID from that panel.

## 2. Check the saved record

Open **Workflow Records**. Ticket 1 should be under **Saved records**. Select it and confirm the details match the result you just got: the same ticket body, department, summary, and evidence.

## 3. Check the filters

With the department set to the one shown on the record, **Apply filters**. Ticket 1 stays in the list. Switch the department to a different one and apply again. Ticket 1 disappears. **Clear** brings it back.

Do the same with **Routing review**. If the record says route review is required, **Requires review** keeps it and **Does not require review** hides it. If review is not required, those two filters swap.

## 4. Assign a department

On the open record, the assignment box is red when review is required and white when it is optional. Pick a department and click **Assign department**. The assigned department changes. The model recommendation and the class scores stay the same.

## 5. Inspect the trace

Open **Operations**. Paste the trace ID into **Trace lookup** and click **Inspect trace**. You should see one timeline, in the order the events were recorded, containing both kinds of events:

- Service log lines for `workflow`, `routing`, `retrieval`, and `llm`, each with a start and a completion.
- Monitoring fields on the closing workflow event, including `elapsed_ms` and `terminal_status`.

The events should not contain the ticket text, the summary, or the article text.

## 6. Check the metrics

Still on **Operations**, the three tiles should load:

- `median_workflow_ms`
- `workflow_failure_rate`
- `routing_review_rate`

Each tile shows the JSON from that endpoint, with a `value` field. After one successful ticket, the median is a positive number of milliseconds, the failure rate is `0`, and the review rate is `0` or `1` depending on whether that ticket required review. Set a start time after the ticket was processed and refresh. The tiles should show `null` inside the JSON, which means no records fell in that window.
