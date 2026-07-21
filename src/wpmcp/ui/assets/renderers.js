const {
  content, loading, errorState, errorMessage, title, subtitle, sitePill, footerSite,
  text, block, badge, metric, panel, table, codeBlock,
} = window.__wpmcp;

function setSite(site) {
  if (!site) return;
  sitePill.textContent = site;
  footerSite.textContent = site;
}

function renderError(message) {
  loading.hidden = true;
  content.hidden = true;
  errorState.hidden = false;
  errorMessage.textContent = message || "The tool returned an unsupported response.";
}

function renderOperation(payload) {
  title.textContent = `${payload.action} result`;
  subtitle.textContent = payload.message || "Operation completed.";
  const hero = document.createElement("section");
  hero.className = "panel operation-hero";
  hero.append(
    text("div", payload.ok ? "✓" : "!", "operation-icon"),
    badge(payload.ok ? "successful" : "failed"),
    text("div", payload.message || "Done", "operation-message"),
  );
  content.append(hero);
  if (payload.data && typeof payload.data === "object") {
    const details = panel("Details", "Structured response from WordPress");
    const grid = document.createElement("div");
    grid.className = "detail-grid";
    Object.entries(payload.data).slice(0, 12).forEach(([k, v]) =>
      grid.append(block(k.replaceAll("_", " "), typeof v === "object" ? JSON.stringify(v) : v)),
    );
    details.append(grid);
    content.append(details);
  }
}

function renderTable(view, payload, columns, heading, description) {
  const rows = Array.isArray(payload.data) ? payload.data : (payload.data?.items || []);
  title.textContent = heading;
  subtitle.textContent = `${rows.length} records · ${payload.action}`;
  const p = panel(heading, description);
  p.append(table(rows, columns));
  content.append(p);
}

function renderDetails(payload, heading, description) {
  title.textContent = heading;
  subtitle.textContent = description || "Structured record from WordPress.";
  const p = panel(heading, description || "Complete structured record");
  const grid = document.createElement("div");
  grid.className = "detail-grid";
  const data = payload.data && typeof payload.data === "object" ? payload.data : { value: payload.data };
  Object.entries(data).slice(0, 16).forEach(([k, v]) =>
    grid.append(block(k.replaceAll("_", " "), typeof v === "object" ? JSON.stringify(v) : v)),
  );
  p.append(grid);
  content.append(p);
  if (payload.data?.content && typeof payload.data.content === "string") {
    content.append(codeBlock(payload.data.content));
  }
}

function renderCatalog(payload) {
  title.textContent = "WPMCP action catalog";
  subtitle.textContent = "Every gateway tool and the actions it accepts.";
  const domains = Array.isArray(payload.data) ? payload.data : [];
  domains.forEach((d) => {
    const p = panel(d.title || d.tool, d.description || "");
    const rows = (d.actions || []).map((a) => ({
      action: a.name,
      summary: a.summary,
      params: Object.keys(a.params || {}).join(", ") || "—",
      safety: a.destructive ? "destructive" : a.read_only ? "read" : "write",
    }));
    p.append(table(rows, [
      { key: "action", label: "Action" },
      { key: "summary", label: "Summary" },
      { key: "params", label: "Params", className: "hide-mobile" },
      { key: "safety", label: "Safety", badge: true },
    ]));
    content.append(p);
  });
}

function renderSites(payload) {
  const rows = Array.isArray(payload.data) ? payload.data : [];
  title.textContent = "Registered sites";
  subtitle.textContent = `${rows.length} WordPress connection${rows.length === 1 ? "" : "s"}.`;
  const p = panel("Multisite connections", "Sites this WPMCP server can manage");
  p.append(table(rows, [
    { key: "alias", label: "Alias" },
    { key: "url", label: "URL" },
    { key: "username", label: "User", className: "hide-mobile" },
    { key: "is_default", label: "Default", format: (v) => (v ? "✓" : "—") },
  ]));
  content.append(p);
}

function renderDashboard(payload) {
  title.textContent = "WordPress command center";
  subtitle.textContent = payload.message || "Overview of the current site.";
  const data = payload.data || {};
  const metrics = document.createElement("div");
  metrics.className = "metrics";
  const m = (l, v, n) => metrics.append(metric(l, v, n));
  m("Site", data.name || data.title || "—", data.url || "");
  m("WP version", data.version || "—", data.namespaces ? `${data.namespaces.length} REST namespaces` : "");
  m("Timezone", data.timezone_string || data.timezone || "—", data.language || "");
  content.append(metrics);
  if (data.description) {
    const p = panel("Site description", "From the WordPress REST root");
    p.append(text("p", data.description));
    content.append(p);
  }
}

const RENDERERS = {
  dashboard: renderDashboard,
  catalog: renderCatalog,
  sites: renderSites,
  operation: renderOperation,
  error: (p) => renderError(p.message),
  posts: (p) => renderTable("posts", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" },
    { key: "status", label: "Status", badge: true }, { key: "date", label: "Date", className: "hide-mobile" },
  ], "Posts", "Content returned by WordPress"),
  pages: (p) => renderTable("pages", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" },
    { key: "status", label: "Status", badge: true }, { key: "parent", label: "Parent", className: "hide-mobile" },
  ], "Pages", "Site structure"),
  media: (p) => renderTable("media", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" },
    { key: "mime_type", label: "Type", className: "hide-mobile" }, { key: "source_url", label: "URL", className: "hide-mobile" },
  ], "Media", "Media library"),
  "media-gallery": (p) => renderTable("media-gallery", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" }, { key: "mime_type", label: "Type" },
  ], "Media library", "Recent media items"),
  users: (p) => renderTable("users", p, [
    { key: "id", label: "ID" }, { key: "name", label: "Name" }, { key: "slug", label: "Slug", className: "hide-mobile" },
  ], "Users", "Registered users"),
  roles: (p) => renderDetails(p, "Roles & capabilities", "Role definitions"),
  comments: (p) => renderTable("comments", p, [
    { key: "id", label: "ID" }, { key: "author_name", label: "Author" },
    { key: "status", label: "Status", badge: true }, { key: "date", label: "Date", className: "hide-mobile" },
  ], "Comments", "Discussion"),
  terms: (p) => renderTable("terms", p, [
    { key: "id", label: "ID" }, { key: "name", label: "Name" }, { key: "slug", label: "Slug", className: "hide-mobile" }, { key: "count", label: "Count" },
  ], "Terms", "Taxonomy terms"),
  taxonomy: (p) => renderDetails(p, "Taxonomy", "Post types and taxonomies"),
  themes: (p) => renderTable("themes", p, [
    { key: "stylesheet", label: "Stylesheet" }, { key: "name", label: "Name" },
    { key: "active", label: "Active", format: (v) => (v ? "✓" : "—") }, { key: "version", label: "Version", className: "hide-mobile" },
  ], "Themes", "Installed themes"),
  "theme-json": (p) => renderDetails(p, "theme.json", "Block theme configuration"),
  templates: (p) => renderTable("templates", p, [
    { key: "name", label: "Name" }, { key: "type", label: "Type", className: "hide-mobile" },
  ], "Templates", "Theme templates and parts"),
  plugins: (p) => renderTable("plugins", p, [
    { key: "plugin", label: "Plugin" }, { key: "name", label: "Name" },
    { key: "active", label: "Active", format: (v) => (v ? "✓" : "—") }, { key: "version", label: "Version", className: "hide-mobile" },
  ], "Plugins", "Installed plugins"),
  "plugin-files": (p) => renderTable("plugin-files", p, [
    { key: "path", label: "Path" }, { key: "size", label: "Size", className: "hide-mobile" },
  ], "Plugin files", "Files in this plugin"),
  menus: (p) => renderTable("menus", p, [
    { key: "id", label: "ID" }, { key: "name", label: "Name" }, { key: "locations", label: "Locations", className: "hide-mobile" },
  ], "Menus", "Navigation menus"),
  "menu-items": (p) => renderTable("menu-items", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" }, { key: "url", label: "URL", className: "hide-mobile" },
  ], "Menu items", "Items in this menu"),
  "menu-locations": (p) => renderDetails(p, "Menu locations", "Registered menu locations"),
  files: (p) => renderTable("files", p, [
    { key: "path", label: "Path" }, { key: "type", label: "Type" }, { key: "size", label: "Size", className: "hide-mobile" },
  ], "Files", "Directory listing"),
  file: (p) => renderDetails(p, "File", "File contents and metadata"),
  tables: (p) => renderTable("tables", p, [
    { key: "name", label: "Table" }, { key: "rows", label: "Rows" }, { key: "is_wp_table", label: "WP", format: (v) => (v ? "✓" : "—") },
  ], "Database tables", "Tables in this database"),
  "table-structure": (p) => renderTable("table-structure", p, [
    { key: "Field", label: "Field" }, { key: "Type", label: "Type", className: "hide-mobile" }, { key: "Key", label: "Key", className: "hide-mobile" },
  ], "Table structure", "Column definitions"),
  "table-preview": (p) => renderDetails(p, "Table preview", "Sample rows from the table"),
  query: (p) => renderDetails(p, "Query result", "Rows returned by the SELECT query"),
  options: (p) => renderDetails(p, "Option", "WordPress option value"),
  "wc-products": (p) => renderTable("wc-products", p, [
    { key: "id", label: "ID" }, { key: "name", label: "Name" }, { key: "status", label: "Status", badge: true }, { key: "regular_price", label: "Price", className: "amount" },
  ], "Products", "WooCommerce products"),
  "wc-orders": (p) => renderTable("wc-orders", p, [
    { key: "id", label: "Order" }, { key: "status", label: "Status", badge: true }, { key: "total", label: "Total", className: "amount" }, { key: "date_created", label: "Date", className: "hide-mobile" },
  ], "Orders", "WooCommerce orders"),
  "wc-customers": (p) => renderTable("wc-customers", p, [
    { key: "id", label: "ID" }, { key: "name", label: "Name" }, { key: "email", label: "Email", className: "hide-mobile" },
  ], "Customers", "WooCommerce customers"),
  "wc-coupons": (p) => renderTable("wc-coupons", p, [
    { key: "id", label: "ID" }, { key: "code", label: "Code" }, { key: "amount", label: "Amount", className: "amount" },
  ], "Coupons", "WooCommerce coupons"),
  "wc-report": (p) => renderDetails(p, "WooCommerce report", "Store performance"),
  blocks: (p) => renderTable("blocks", p, [
    { key: "name", label: "Block" }, { key: "title", label: "Title", className: "hide-mobile" },
  ], "Block types", "Registered Gutenberg blocks"),
  "block-patterns": (p) => renderTable("block-patterns", p, [
    { key: "name", label: "Pattern" }, { key: "title", label: "Title" },
  ], "Block patterns", "Reusable block patterns"),
  "reusable-blocks": (p) => renderTable("reusable-blocks", p, [
    { key: "id", label: "ID" }, { key: "title", label: "Title" },
  ], "Reusable blocks", "Synced block patterns"),
  seo: (p) => renderDetails(p, "SEO", "Search optimization data"),
  security: (p) => renderDetails(p, "Security", "Security status"),
  updates: (p) => renderDetails(p, "Updates", "Available updates"),
  "debug-log": (p) => renderDetails(p, "Debug log", "Recent log entries"),
  performance: (p) => renderDetails(p, "Performance", "Performance metrics"),
  backups: (p) => renderTable("backups", p, [
    { key: "id", label: "ID" }, { key: "type", label: "Type" }, { key: "size", label: "Size", className: "hide-mobile" }, { key: "date", label: "Date", className: "hide-mobile" },
  ], "Backups", "Available backups"),
  backup: (p) => renderDetails(p, "Backup", "Backup job status"),
  cron: (p) => renderTable("cron", p, [
    { key: "hook", label: "Hook" }, { key: "schedule", label: "Schedule", className: "hide-mobile" }, { key: "next_run", label: "Next run" },
  ], "Cron jobs", "Scheduled events"),
  shortcodes: (p) => renderTable("shortcodes", p, [
    { key: "tag", label: "Shortcode" }, { key: "callback", label: "Callback", className: "hide-mobile" },
  ], "Shortcodes", "Registered shortcodes"),
  widgets: (p) => renderDetails(p, "Widgets", "Widget areas and widgets"),
  settings: (p) => renderDetails(p, "Settings", "Site settings"),
  "site-info": (p) => renderDashboard(p),
  post: (p) => renderDetails(p, "Record", "Single record from WordPress"),
};

function render(payload) {
  content.replaceChildren();
  loading.hidden = true;
  errorState.hidden = true;
  content.hidden = false;
  setSite(payload.site);
  const view = payload.view;
  const renderer = RENDERERS[view] || renderDetails;
  if (view === "error") return renderError(payload.message);
  renderer(payload, view);
}

window.__wpmcp.render = render;
window.__wpmcp.renderError = renderError;
