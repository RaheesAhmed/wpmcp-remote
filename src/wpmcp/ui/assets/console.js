import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

const content = document.querySelector("#content");
const loading = document.querySelector("#loading-state");
const errorState = document.querySelector("#error-state");
const errorMessage = document.querySelector("#error-message");
const title = document.querySelector("#view-title");
const subtitle = document.querySelector("#view-subtitle");
const sitePill = document.querySelector("#site-pill");
const footerSite = document.querySelector("#footer-site");

const statusClass = (value) =>
  String(value || "").toLowerCase().replaceAll("_", "-").replaceAll(" ", "-");
const statusLabel = (value) => String(value ?? "—").replaceAll("_", " ");

const text = (tag, value, className) => {
  const node = document.createElement(tag);
  node.textContent = String(value ?? "—");
  if (className) node.className = className;
  return node;
};
const block = (label, value) => {
  const node = document.createElement("div");
  node.className = "detail";
  node.append(text("div", label, "detail-label"), text("div", value, "detail-value"));
  return node;
};
const badge = (value) => text("span", statusLabel(value), `badge ${statusClass(value)}`);

function metric(label, value, note) {
  const node = document.createElement("article");
  node.className = "metric";
  node.append(
    text("div", label, "metric-label"),
    text("div", value, "metric-value"),
    text("div", note, "metric-note"),
  );
  return node;
}
function panel(heading, description) {
  const node = document.createElement("section");
  node.className = "panel";
  const head = document.createElement("div");
  head.className = "panel-head";
  const copy = document.createElement("div");
  copy.append(text("h2", heading), text("p", description));
  head.append(copy);
  node.append(head);
  return node;
}
function table(rows, columns) {
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const tableNode = document.createElement("table");
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((c) => headRow.append(text("th", c.label, c.className)));
  head.append(headRow);
  const body = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((c) => {
      const td = document.createElement("td");
      if (c.badge) td.append(badge(row[c.key]));
      else td.textContent = c.format ? c.format(row[c.key]) : String(row[c.key] ?? "—");
      if (c.className) td.className = c.className;
      tr.append(td);
    });
    body.append(tr);
  });
  tableNode.append(head, body);
  wrap.append(tableNode);
  return wrap;
}
function codeBlock(value) {
  const pre = document.createElement("pre");
  pre.className = "code-block";
  pre.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return pre;
}

window.__wpmcp = {
  content, loading, errorState, errorMessage, title, subtitle, sitePill, footerSite,
  statusClass, statusLabel, text, block, badge, metric, panel, table, codeBlock,
};
