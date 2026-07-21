const { text } = window.__wpmcp;

const actionDialog = document.querySelector("#action-dialog");
const dialogContent = document.querySelector("#dialog-content");
const dialogTitle = document.querySelector("#dialog-title");
const actionButtons = document.querySelectorAll("[data-action]");

const ACTION_DEFINITIONS = {
  new_post: {
    title: "Create a post",
    description: "Draft a new blog post. Leave status as draft for review.",
    tool: "wp_content",
    action: "create_post",
    submitLabel: "Create post",
    fields: [
      { name: "title", label: "Title", required: true },
      { name: "content", label: "Content (HTML)", tag: "textarea", required: true },
      { name: "status", label: "Status", type: "select", options: [["draft", "Draft"], ["publish", "Publish"], ["pending", "Pending"]] },
    ],
  },
  new_page: {
    title: "Create a page",
    description: "Add a new page to the site structure.",
    tool: "wp_content",
    action: "create_page",
    submitLabel: "Create page",
    fields: [
      { name: "title", label: "Title", required: true },
      { name: "content", label: "Content (HTML)", tag: "textarea" },
      { name: "status", label: "Status", type: "select", options: [["draft", "Draft"], ["publish", "Publish"]] },
    ],
  },
  activate_plugin: {
    title: "Activate a plugin",
    description: "Switch a plugin on by its slug/path.",
    tool: "wp_plugins",
    action: "activate_plugin",
    submitLabel: "Activate plugin",
    fields: [{ name: "plugin", label: "Plugin slug", placeholder: "akismet/akismet", required: true }],
  },
  activate_theme: {
    title: "Activate a theme",
    description: "Switch the active theme by its stylesheet.",
    tool: "wp_appearance",
    action: "activate_theme",
    submitLabel: "Activate theme",
    fields: [{ name: "stylesheet", label: "Stylesheet", placeholder: "twentytwentyfive", required: true }],
  },
  clear_cache: {
    title: "Clear the cache",
    description: "Flush object cache and transients.",
    tool: "wp_performance",
    action: "clear_cache",
    submitLabel: "Clear cache",
    fields: [],
  },
  audit: {
    title: "Run a site audit",
    description: "Gather site info, health, and updates (read-only).",
    tool: "wp_sites",
    action: "get_site_info",
    submitLabel: "Run audit",
    fields: [],
  },
};

function buildField(def) {
  const wrapper = document.createElement("label");
  wrapper.className = "form-field";
  wrapper.append(text("span", def.label, "field-label"));
  let control;
  if (def.type === "select") {
    control = document.createElement("select");
    (def.options || []).forEach(([v, l]) => {
      const o = document.createElement("option");
      o.value = v;
      o.textContent = l;
      control.append(o);
    });
  } else if (def.tag === "textarea") {
    control = document.createElement("textarea");
    control.rows = 5;
  } else {
    control = document.createElement("input");
    if (def.type) control.type = def.type;
    if (def.placeholder) control.placeholder = def.placeholder;
  }
  control.name = def.name;
  if (def.required) control.required = true;
  wrapper.append(control);
  return wrapper;
}

function showDialogError(message) {
  dialogContent.querySelector(".dialog-error")?.remove();
  const err = text("p", message, "dialog-error");
  err.setAttribute("role", "alert");
  dialogContent.prepend(err);
}

async function callTool(toolName, args, submitButton) {
  const original = submitButton.textContent;
  submitButton.disabled = true;
  submitButton.textContent = "Working…";
  try {
    const result = await app.callServerTool({ name: toolName, arguments: args });
    const payload = extractPayload(result);
    if (result?.isError) throw new Error(payload?.message || "The action could not be completed.");
    return payload;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = original;
  }
}

function extractPayload(result) {
  if (result?.structuredContent) return result.structuredContent;
  const entry = result?.content?.find((i) => i.type === "text");
  if (!entry) return null;
  try { return JSON.parse(entry.text); } catch { return { message: entry.text }; }
}

function openActionDialog(actionName) {
  const def = ACTION_DEFINITIONS[actionName];
  if (!def) return;
  dialogTitle.textContent = def.title;
  const form = document.createElement("form");
  form.className = "action-form";
  form.append(text("p", def.description, "dialog-description"));
  def.fields.forEach((f) => form.append(buildField(f)));
  const submit = text("button", def.submitLabel, "button primary-button");
  submit.type = "submit";
  const actions = document.createElement("div");
  actions.className = "form-actions";
  actions.append(submit);
  form.append(actions);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const params = Object.fromEntries(new FormData(form).entries());
    try {
      const payload = await callTool(def.tool, { action: def.action, params }, submit);
      actionDialog.close();
      window.__wpmcp.render(payload);
    } catch (error) {
      showDialogError(error instanceof Error ? error.message : "The action could not be completed.");
    }
  });
  dialogContent.replaceChildren(form);
  if (!actionDialog.open) actionDialog.showModal();
  form.querySelector("input, select, textarea")?.focus();
}

actionButtons.forEach((b) =>
  b.addEventListener("click", () => openActionDialog(b.dataset.action)),
);
document.querySelector("[data-close-dialog]").addEventListener("click", () => actionDialog.close());
actionDialog.addEventListener("click", (e) => { if (e.target === actionDialog) actionDialog.close(); });

const app = new App({ name: "WPMCP Console", version: "1.0.0" });
app.ontoolresult = (result) => {
  const payload = extractPayload(result);
  if (payload) window.__wpmcp.render(payload);
  else window.__wpmcp.renderError();
};
await app.connect();
