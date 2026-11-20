"use strict";

const DEPARTMENTS = [
  "Billing and Payments",
  "Customer Service",
  "General Inquiry",
  "Human Resources",
  "IT Support",
  "Product Support",
  "Returns and Exchanges",
  "Sales and Pre-Sales",
  "Service Outages and Maintenance",
  "Technical Support",
];

const METRICS = [
  "median_workflow_ms",
  "workflow_failure_rate",
  "routing_review_rate",
];

const state = {
  activeView: "process",
  latestResult: null,
  processRequest: 0,
  records: [],
  selectedRecordId: null,
  recordRequest: 0,
  recordLoading: false,
  metrics: new Map(),
  metricRequest: 0,
  metricLoading: false,
  lookupRequest: 0,
};

const byId = (id) => document.getElementById(id);

function element(tag, options = {}, children = []) {
  const node = document.createElement(tag);
  if (options.className) node.className = options.className;
  if (options.text !== undefined) node.textContent = String(options.text);
  if (options.type) node.type = options.type;
  if (options.value !== undefined) node.value = options.value;
  if (options.title) node.title = options.title;
  if (options.dataset) Object.assign(node.dataset, options.dataset);
  if (options.attrs) {
    for (const [name, value] of Object.entries(options.attrs)) {
      node.setAttribute(name, value);
    }
  }
  for (const child of children.flat()) {
    if (child !== null && child !== undefined) node.append(child);
  }
  return node;
}

function replaceContent(target, ...children) {
  target.replaceChildren(...children.flat().filter((child) => child !== null));
}

function setLoading(target, message) {
  replaceContent(target, element("div", { className: "loading-state", text: message }));
}

function setEmpty(target, message) {
  replaceContent(target, element("div", { className: "empty-state", text: message }));
}

function showNotice(message, isError = false) {
  const notice = byId("app-notice");
  notice.textContent = message;
  notice.className = `notice${isError ? " is-error" : ""}`;
  notice.hidden = false;
  window.clearTimeout(showNotice.timeoutId);
  showNotice.timeoutId = window.setTimeout(() => {
    notice.hidden = true;
  }, 7000);
}

async function requestJson(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new Error("The workflow service is unavailable.");
  }

  let payload = null;
  const contentType = response.headers.get("content-type") || "";
  try {
    if (contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      const text = await response.text();
      payload = text ? { detail: text } : null;
    }
  } catch (error) {
    if (response.ok) throw error;
  }

  if (!response.ok) {
    const message =
      (payload && (payload.detail || payload.error)) ||
      `Request failed with status ${response.status}.`;
    const error = new Error(typeof message === "string" ? message : JSON.stringify(message));
    error.status = response.status;
    if (url === "/tickets/process" && options.method === "POST" && isWorkflowResult(payload)) {
      error.workflowResult = payload;
    }
    throw error;
  }
  return payload;
}

function activateView(viewName) {
  state.activeView = viewName;
  for (const tab of document.querySelectorAll(".tab[data-view]")) {
    const active = tab.dataset.view === viewName;
    tab.classList.toggle("is-active", active);
    if (active) tab.setAttribute("aria-current", "page");
    else tab.removeAttribute("aria-current");
  }
  for (const panel of document.querySelectorAll("[data-view-panel]")) {
    const active = panel.dataset.viewPanel === viewName;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  }
  if (viewName === "records" && state.records.length === 0 && !state.recordLoading) loadRecords();
  if (viewName === "operations" && state.metrics.size === 0 && !state.metricLoading) loadMetrics();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function checkHealth() {
  const status = byId("health-status");
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Health check failed.");
    status.className = "health-status is-healthy";
    status.lastElementChild.textContent = "Workflow online";
  } catch (error) {
    status.className = "health-status is-unhealthy";
    status.lastElementChild.textContent = "Workflow unavailable";
  }
}

function clearTicketErrors() {
  byId("ticket-id-error").textContent = "";
  byId("ticket-body-error").textContent = "";
}

function validateTicket(ticketIdValue, bodyValue) {
  clearTicketErrors();
  const ticketId = Number(ticketIdValue);
  let valid = true;
  if (!Number.isInteger(ticketId) || ticketId <= 0) {
    byId("ticket-id-error").textContent = "Enter a positive whole number.";
    valid = false;
  }
  if (!bodyValue.trim()) {
    byId("ticket-body-error").textContent = "Enter a non-empty ticket body.";
    valid = false;
  }
  return valid ? { ticket_id: ticketId, Body: bodyValue } : null;
}

async function processTicket(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const ticket = validateTicket(form.ticket_id.value, form.Body.value);
  if (!ticket) return;

  const requestId = ++state.processRequest;
  const button = byId("process-button");
  const resultTarget = byId("process-result");
  state.latestResult = null;
  byId("app-notice").hidden = true;
  button.disabled = true;
  button.textContent = "Processing...";
  setLoading(resultTarget, "Processing ticket. Local model generation may take a moment...");
  try {
    const result = await requestJson("/tickets/process", {
      method: "POST",
      body: JSON.stringify(ticket),
    });
    if (requestId !== state.processRequest) return;
    if (!isWorkflowResult(result)) {
      throw new Error("The workflow returned an invalid result.");
    }
    state.latestResult = result;
    renderWorkflowResult(resultTarget, result, { showRecordLink: true });
    invalidateRecords();
    showNotice(
      workflowSucceeded(result)
        ? "Ticket processing completed."
        : `Ticket processing ended with ${result.terminal_status}.`,
      !workflowSucceeded(result),
    );
  } catch (error) {
    if (requestId !== state.processRequest) return;
    if (error.workflowResult) {
      state.latestResult = error.workflowResult;
      renderWorkflowResult(resultTarget, error.workflowResult);
      invalidateRecords();
      showNotice(
        `Ticket processing returned ${error.workflowResult.terminal_status} (HTTP ${error.status}).`,
        true,
      );
    } else {
      setErrorState(resultTarget, error.message);
      showNotice(error.message, true);
    }
  } finally {
    if (requestId === state.processRequest) {
      button.disabled = false;
      button.textContent = "Process ticket";
    }
  }
}

function setErrorState(target, message) {
  replaceContent(
    target,
    element("div", { className: "empty-state" }, [
      element("span", { className: "badge error", text: "Request failed" }),
      element("p", { text: message }),
    ]),
  );
}

function statusBadge(record) {
  const status = record.terminal_status;
  const labels = {
    summary_ready_for_review: "Summary ready",
    input_rejected: "Input rejected",
    workflow_failed: "Workflow failed",
  };
  return element("span", {
    className: `badge ${status === "summary_ready_for_review" ? "success" : "error"}`,
    text: labels[status] || status || "Unknown",
  });
}

function reviewBadge(record) {
  if (record.terminal_status !== "summary_ready_for_review") return null;
  if (record.requires_routing_review) {
    return element("span", { className: "badge warning", text: "Route review required" });
  }
  if (record.human_reviewed_route) {
    return element("span", { className: "badge reviewed", text: "Route reviewed" });
  }
  return element("span", { className: "badge", text: "No route review required" });
}

function effectiveRoute(record) {
  return record.human_reviewed_route || record.recommended_department;
}

function dataBlock(label, value, options = {}) {
  const classes = ["data-value"];
  if (options.preserveLineBreaks) classes.push("preserve-whitespace");
  if (options.fallback) classes.push("muted");
  return element("div", { className: "data-block" }, [
    element("span", { className: "data-label", text: label }),
    element(options.preserveLineBreaks ? "div" : "span", {
      className: classes.join(" "),
      text: value === null || value === undefined ? "Not available" : value,
    }),
  ]);
}

function workflowSucceeded(record) {
  return record.terminal_status === "summary_ready_for_review";
}

function isWorkflowResult(record) {
  const fields = [
    "ticket_id", "terminal_status", "recommended_department", "class_scores",
    "ticket_body", "requires_routing_review", "human_reviewed_route",
    "ticket_summary", "retrieved_evidence", "trace_id", "error", "workflow_record_id",
  ];
  if (!hasExactFields(record, fields)) return false;
  const nonemptyString = (value) => typeof value === "string" && value.trim().length > 0;
  if (!nonemptyString(record.workflow_record_id) ||
      !(record.trace_id === null || nonemptyString(record.trace_id))) return false;
  if (!(Number.isInteger(record.ticket_id) && record.ticket_id > 0) &&
      !(record.terminal_status === "input_rejected" && record.ticket_id === null)) return false;

  if (["input_rejected", "workflow_failed"].includes(record.terminal_status)) {
    return nonemptyString(record.error) &&
      record.requires_routing_review === false &&
      Array.isArray(record.retrieved_evidence) && record.retrieved_evidence.length === 0 &&
      ["recommended_department", "class_scores", "ticket_body", "ticket_summary",
        "human_reviewed_route"].every((key) => record[key] === null);
  }
  if (!workflowSucceeded(record) || record.error !== null ||
      typeof record.requires_routing_review !== "boolean" ||
      !nonemptyString(record.ticket_body) ||
      !DEPARTMENTS.includes(record.recommended_department) ||
      !(record.human_reviewed_route === null || DEPARTMENTS.includes(record.human_reviewed_route)) ||
      !hasExactFields(record.class_scores, DEPARTMENTS) ||
      !Object.values(record.class_scores).every(Number.isFinite) ||
      record.class_scores[record.recommended_department] !== Math.max(...Object.values(record.class_scores))) {
    return false;
  }
  const summary = record.ticket_summary;
  return hasExactFields(summary, ["summary", "customer_request", "missing_information"]) &&
    typeof summary.summary === "string" &&
    typeof summary.customer_request === "string" &&
    Array.isArray(summary.missing_information) &&
    summary.missing_information.every((item) => typeof item === "string") &&
    Array.isArray(record.retrieved_evidence) &&
    record.retrieved_evidence.length >= 1 && record.retrieved_evidence.length <= 5 &&
    record.retrieved_evidence.every((item, index) =>
      hasExactFields(item, ["rank", "chunk_id", "distance", "content", "metadata"]) &&
      item.rank === index + 1 && nonemptyString(item.chunk_id) &&
      Number.isFinite(item.distance) && typeof item.content === "string" &&
      isObject(item.metadata));
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function hasExactFields(value, fields) {
  return isObject(value) && Object.keys(value).length === fields.length &&
    fields.every((field) => Object.prototype.hasOwnProperty.call(value, field));
}

function renderOriginalTicketBody(record) {
  const hasTicketBody =
    record &&
    typeof record === "object" &&
    Object.prototype.hasOwnProperty.call(record, "ticket_body");
  if (!hasTicketBody) {
    return dataBlock("Original ticket body", "Not available for legacy record", {
      fallback: true,
    });
  }
  if (record.ticket_body === null) {
    return dataBlock(
      "Original ticket body",
      workflowSucceeded(record)
        ? "Not available"
        : "Unavailable for this rejected or failed result.",
      { fallback: true },
    );
  }
  return dataBlock("Original ticket body", record.ticket_body, {
    preserveLineBreaks: true,
  });
}

function renderWorkflowResult(target, record, options = {}) {
  if (!record || typeof record !== "object") {
    setErrorState(target, "The workflow returned an invalid result.");
    return;
  }

  const badges = element("div", { className: "record-meta" }, [
    statusBadge(record),
    reviewBadge(record),
  ]);
  const identity = element("div", { className: "identity-grid" }, [
    dataBlock("Ticket ID", record.ticket_id),
    dataBlock("Terminal status", record.terminal_status),
    dataBlock("Workflow record ID", record.workflow_record_id),
    dataBlock("Trace ID", record.trace_id),
  ]);
  const content = [badges, identity];

  if (!workflowSucceeded(record)) {
    content.push(
      dataBlock("Error", record.error || "The workflow did not produce a review package."),
      renderOriginalTicketBody(record),
    );
    replaceContent(target, ...content);
    return;
  }

  if (options.enableReview) {
    content.push(renderReviewForm(record));
  }

  content.push(
    element("h4", { className: "section-title", text: "Raw ticket info" }),
    element("div", { className: "identity-grid" }, [
      dataBlock("Model recommended department", record.recommended_department),
      dataBlock("Assigned department", effectiveRoute(record)),
    ]),
    renderOriginalTicketBody(record),
  );

  const summary = record.ticket_summary || {};
  content.push(
    element("h4", { className: "section-title", text: "Prepared ticket summary" }),
    element("div", { className: "summary-grid" }, [
      dataBlock("Summary", summary.summary),
      dataBlock("Customer request", summary.customer_request),
      dataBlock(
        "Missing information",
        Array.isArray(summary.missing_information) && summary.missing_information.length
          ? summary.missing_information.join("\n• ")
          : "No missing information identified",
      ),
    ]),
  );

  if (record.class_scores && typeof record.class_scores === "object") {
    content.push(
      element("h4", { className: "section-title", text: "Class scores" }),
      renderClassScores(record.class_scores),
    );
  }

  content.push(
    element("h4", { className: "section-title", text: "Retrieved evidence" }),
    renderEvidence(record.retrieved_evidence),
  );

  if (options.showRecordLink) {
    const actions = element("div", { className: "filter-bar" });
    const recordButton = element("button", {
      className: "button button-secondary",
      text: "Open saved record",
      type: "button",
    });
    recordButton.addEventListener("click", async () => {
      byId("review-filter").value = "";
      byId("department-filter").value = "";
      state.selectedRecordId = record.workflow_record_id;
      const loading = loadRecords();
      activateView("records");
      await loading;
    });
    const eventButton = element("button", {
      className: "button button-secondary",
      text: "Inspect trace",
      type: "button",
    });
    eventButton.addEventListener("click", () => {
      byId("trace-id").value = record.trace_id || "";
      activateView("operations");
      lookupMonitoring();
    });
    actions.append(recordButton, eventButton);
    content.push(actions);
  }

  replaceContent(target, ...content);
}

function renderClassScores(scores) {
  const rows = Object.entries(scores).sort((left, right) => right[1] - left[1]);
  return element("div", { className: "score-list" }, [
    ...rows.map(([department, score]) =>
      element("div", { className: "score-row" }, [
        element("span", { text: department }),
        element("div", { className: "score-track", attrs: { "aria-hidden": "true" } }, [
          element("div", {
            className: "score-fill",
            attrs: {
              style: `width: ${score * 100}%`,
            },
          }),
        ]),
        element("span", { className: "score-value", text: String(score) }),
      ]),
    ),
  ]);
}

function renderEvidence(evidence) {
  if (!Array.isArray(evidence) || evidence.length === 0) {
    return element("div", { className: "empty-state", text: "No evidence returned." });
  }
  return element(
    "div",
    { className: "evidence-list" },
    evidence.map((item) =>
      element("article", { className: "evidence-item" }, [
        element("div", { className: "evidence-header" }, [
          element("strong", { text: `Rank ${item.rank}` }),
          element("span", { className: "muted", text: `Distance ${formatNumber(item.distance, 4)}` }),
        ]),
        element("div", { className: "evidence-meta" }, [
          element("span", { text: `Chunk: ${item.chunk_id}` }),
          element("span", { text: formatMetadata(item.metadata) }),
        ]),
        element("p", { className: "evidence-content", text: item.content }),
      ]),
    ),
  );
}

function formatMetadata(metadata) {
  if (!metadata || typeof metadata !== "object") return "No metadata";
  return Object.entries(metadata)
    .map(([key, value]) => `${key}: ${typeof value === "string" ? value : JSON.stringify(value)}`)
    .join(" · ");
}

function populateDepartments() {
  for (const department of DEPARTMENTS) {
    byId("department-filter").append(element("option", { value: department, text: department }));
  }
}

function recordQuery() {
  const params = new URLSearchParams();
  const review = byId("review-filter").value;
  const department = byId("department-filter").value;
  if (review) params.set("requires_routing_review", review);
  if (department) params.set("department", department);
  const query = params.toString();
  return `/tickets${query ? `?${query}` : ""}`;
}

async function loadRecords(event) {
  if (event) event.preventDefault();
  const requestId = ++state.recordRequest;
  state.recordLoading = true;
  const list = byId("records-list");
  setLoading(list, "Loading saved records...");
  try {
    const records = await requestJson(recordQuery());
    if (requestId !== state.recordRequest) return;
    state.records = Array.isArray(records) ? records : [];
    renderRecordList();
    if (state.selectedRecordId) {
      const selected = state.records.find(
        (record) => record.workflow_record_id === state.selectedRecordId,
      );
      if (selected) renderSelectedRecord(selected);
      else {
        state.selectedRecordId = null;
        setEmpty(byId("record-detail"), "The selected record is not in these results.");
      }
    }
  } catch (error) {
    if (requestId !== state.recordRequest) return;
    setErrorState(list, error.message);
    byId("record-count").textContent = "Refresh failed";
  } finally {
    if (requestId === state.recordRequest) state.recordLoading = false;
  }
}

function invalidateRecords() {
  state.records = [];
  ++state.recordRequest;
  state.recordLoading = false;
  if (state.activeView === "records") {
    loadRecords();
  } else {
    setEmpty(byId("records-list"), "Refresh records to see the latest workflow results.");
    byId("record-count").textContent = "";
    setEmpty(byId("record-detail"), "Select a workflow record after refreshing records.");
  }
}

function renderRecordList() {
  const list = byId("records-list");
  byId("record-count").textContent =
    `${state.records.length} record${plural(state.records.length)}`;
  if (state.records.length === 0) {
    setEmpty(list, "No workflow records match the active filters.");
    return;
  }

  const items = state.records.map((record) => {
    const button = element("button", {
      className: `record-item${
        state.selectedRecordId === record.workflow_record_id ? " is-selected" : ""
      }`,
      type: "button",
    }, [
      element("div", { className: "record-item-header" }, [
        element("strong", {
          text: `Ticket ${
            record.ticket_id === null || record.ticket_id === undefined
              ? "unavailable"
              : record.ticket_id
          }`,
        }),
        statusBadge(record),
      ]),
      element("div", { className: "record-meta" }, [
        element("span", { text: effectiveRoute(record) || "No route" }),
        reviewBadge(record),
      ]),
      element("div", {
        className: "muted",
        text: `Record ${record.workflow_record_id}`,
      }),
    ]);
    button.addEventListener("click", () => renderSelectedRecord(record));
    return button;
  });
  replaceContent(list, element("div", { className: "record-list" }, items));
}

function renderSelectedRecord(record) {
  state.selectedRecordId = record.workflow_record_id;
  renderRecordList();
  renderWorkflowResult(byId("record-detail"), record, { enableReview: true });
}

function renderReviewForm(record) {
  const selectId = `manual-department-${record.workflow_record_id}`;
  const select = element("select", {
    attrs: { id: selectId },
  }, [
    element("option", { value: "", text: "Select a department" }),
    ...DEPARTMENTS.map((department) =>
      element("option", { value: department, text: department }),
    ),
  ]);
  select.value = record.human_reviewed_route || "";
  const error = element("p", { className: "field-error", attrs: { role: "alert" } });
  const submit = element("button", {
    className: "button button-primary",
    text: "Assign department",
    type: "button",
  });
  submit.addEventListener("click", async () => {
    error.textContent = "";
    if (!select.value) {
      error.textContent = "Select an allowed department.";
      return;
    }
    submit.disabled = true;
    submit.textContent = "Assigning...";
    try {
      await requestJson(
        `/tickets/${encodeURIComponent(record.workflow_record_id)}/routing-review`,
        {
          method: "POST",
          body: JSON.stringify({ human_reviewed_route: select.value }),
        },
      );
      showNotice("Department assigned. The model recommendation remains unchanged.");
      await loadRecords();
    } catch (requestError) {
      error.textContent = requestError.message;
    } finally {
      submit.disabled = false;
      submit.textContent = "Assign department";
    }
  });

  return element("section", {
    className: `assignment-box${record.requires_routing_review ? " requires-review" : ""}`,
  }, [
    record.requires_routing_review
      ? element("strong", { text: "Route review required" })
      : element("strong", { text: "Manual department assignment" }),
    element("p", {
      className: "helper-text",
      text: "A manual assignment changes the assigned department, not the model recommendation or scores.",
    }),
    element("div", { className: "filter-bar" }, [
      element("div", { className: "field field-grow" }, [
        element("label", {
          text: "Manually assign department",
          attrs: { for: selectId },
        }),
        select,
        error,
      ]),
      submit,
    ]),
  ]);
}

function clearRecordFilters() {
  byId("review-filter").value = "";
  byId("department-filter").value = "";
  loadRecords();
}

function metricParams() {
  const start = byId("metric-start").value;
  const end = byId("metric-end").value;
  const params = new URLSearchParams();
  let startDate = null;
  let endDate = null;
  if (start) {
    startDate = new Date(start);
    if (Number.isNaN(startDate.getTime())) throw new Error("Start time is invalid.");
    params.set("start", startDate.toISOString());
  }
  if (end) {
    endDate = new Date(end);
    if (Number.isNaN(endDate.getTime())) throw new Error("End time is invalid.");
    params.set("end", endDate.toISOString());
  }
  if (startDate && endDate && startDate > endDate) {
    throw new Error("Start time must not be later than end time.");
  }
  return params;
}

function metricLabel(key) {
  const words = key.replace(/[-_]+/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function renderMetricTile(key, response) {
  const isScalar = response === null || ["number", "string", "boolean"].includes(typeof response);
  return element("article", { className: "metric-card" }, [
    element("span", { className: "data-label", text: key }),
    isScalar
      ? element("div", {
          className: "metric-value",
          text: response === null ? "N/A" : typeof response === "number" ? String(Number(response.toFixed(3))) : String(response),
        })
      : literalJson(response),
  ]);
}

async function loadMetrics(event) {
  if (event) event.preventDefault();
  const requestId = ++state.metricRequest;
  const target = byId("metric-cards");
  const errorTarget = byId("metric-error");
  errorTarget.textContent = "";

  let params;
  try {
    params = metricParams();
  } catch (error) {
    errorTarget.textContent = error.message;
    state.metricLoading = false;
    state.metrics.clear();
    setEmpty(target, "Correct the time bounds and refresh metrics.");
    return;
  }

  state.metricLoading = true;
  replaceContent(
    target,
    ...METRICS.map((key) =>
      element("article", { className: "metric-card loading-state", text: `Loading ${metricLabel(key)}...` }),
    ),
  );

  const suffix = params.toString() ? `?${params}` : "";
  const results = await Promise.allSettled(
    METRICS.map((key) =>
      requestJson(`/ops/metrics/${encodeURIComponent(key)}${suffix}`),
    ),
  );
  if (requestId !== state.metricRequest) return;
  state.metricLoading = false;
  state.metrics.clear();
  replaceContent(
    target,
    ...results.map((result, index) => {
      const key = METRICS[index];
      if (result.status === "rejected") {
        return element("article", { className: "metric-card" }, [
          element("span", { className: "badge error", text: "Request failed" }),
          element("h4", { className: "section-title", text: metricLabel(key) }),
          element("p", { className: "muted", text: result.reason.message }),
        ]);
      }
      state.metrics.set(key, result.value);
      return renderMetricTile(key, result.value);
    }),
  );
}

function clearMetricBounds() {
  byId("metric-start").value = "";
  byId("metric-end").value = "";
  loadMetrics();
}

async function lookupMonitoring(event) {
  if (event) event.preventDefault();
  const requestId = ++state.lookupRequest;
  const traceId = byId("trace-id").value.trim();
  const tracesTarget = byId("trace-results");
  if (!traceId) {
    setErrorState(tracesTarget, "Enter a trace ID.");
    return;
  }
  setLoading(tracesTarget, "Finding trace records...");
  const query = new URLSearchParams({ trace_id: traceId });
  try {
    const traces = await requestJson(`/ops/traces?${query}`);
    if (requestId !== state.lookupRequest) return;
    renderTraces(tracesTarget, traces);
  } catch (error) {
    if (requestId !== state.lookupRequest) return;
    setErrorState(tracesTarget, error.status
      ? `Trace lookup failed (HTTP ${error.status}): ${error.message}`
      : error.message);
  }
}

function renderTraces(target, traces) {
  if (!Array.isArray(traces)) {
    setErrorState(target, "The trace lookup returned an invalid result.");
    return;
  }
  if (!traces.length) {
    setEmpty(target, "No trace records match this trace ID.");
    return;
  }
  replaceContent(target, element("div", { className: "trace-list" },
    traces.map((entry) => element("article", { className: "trace-item" }, [
      literalJson(entry),
    ])),
  ));
}

function literalJson(value) {
  return element("pre", {
    className: "data-value preserve-whitespace",
    text: JSON.stringify(value, null, 2),
  });
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) return "Not available";
  const number = Number(value);
  return Number.isFinite(number)
    ? number.toLocaleString(undefined, { maximumFractionDigits: digits })
    : "Not available";
}

function plural(count) {
  return count === 1 ? "" : "s";
}

function initialize() {
  populateDepartments();
  document.querySelectorAll(".tab[data-view]").forEach((tab) => {
    tab.addEventListener("click", () => activateView(tab.dataset.view));
  });
  byId("ticket-form").addEventListener("submit", processTicket);
  byId("record-filters").addEventListener("submit", loadRecords);
  byId("refresh-records").addEventListener("click", loadRecords);
  byId("clear-record-filters").addEventListener("click", clearRecordFilters);
  byId("metric-filters").addEventListener("submit", loadMetrics);
  byId("clear-metric-bounds").addEventListener("click", clearMetricBounds);
  byId("trace-form").addEventListener("submit", lookupMonitoring);
  checkHealth();
}

initialize();
