# WPMCP — Remote WordPress MCP Server

Give any AI agent **complete, multisite control of WordPress** through one fast, secure remote MCP server. Built with Python + [FastMCP](https://gofastmcp.com), served over Streamable HTTP, with a premium **generative UI** that renders every result as an interactive console — not raw text.

Connect Cursor, Claude Desktop, Cline, or any MCP-compatible client to a single URL and manage content, themes, plugins, files, database, WooCommerce, SEO, security, backups, and an entire multisite network in plain language.

---

## Highlights

- **Remote & multi-client** — one Streamable HTTP endpoint serves many AI clients at once.
- **Multisite native** — manage one site or a fleet from the same server; switch sites per call.
- **Generative UI** — every tool result renders in a polished, interactive console (MCP Apps) with action dialogs that call back into the server.
- **Compact tool surface** — 160+ WordPress actions exposed through **17 dispatch tools**, so the model's context window stays small instead of filling with hundreds of schemas.
- **Secure by default** — bearer-token auth for the server, WordPress Application Passwords per site, filesystem allow-listing, SELECT-only SQL, destructive-action flags.
- **Fast** — async `httpx` with connection pooling, cached settings, concurrent UI loading.

---

## How it works (the dispatch pattern)

Most MCP servers register one tool per capability. For a surface as large as WordPress that means hundreds of tools — and every tool's schema is shipped to the LLM on each session, bloating context and slowing it down.

WPMCP does the opposite. It exposes **17 namespaced gateway tools**:

```
wp_discover        wp_content       wp_users         wp_appearance
wp_plugins         wp_menus         wp_taxonomy      wp_files
wp_database        wp_woocommerce   wp_blocks        wp_seo
wp_security        wp_performance   wp_backup        wp_maintenance
wp_sites
```

Each gateway takes three arguments — `action`, optional `site`, and `params` — and dispatches to the right WordPress operation. The model calls `wp_discover` once to learn every available action, then dispatches. **Full WordPress power, a fraction of the context cost.**

Every result comes back as a structured `WpResult` envelope that the generative UI renders automatically:

```json
{ "ok": true, "action": "create_post", "domain": "content", "site": "primary",
  "view": "post", "data": { "...": "..." }, "message": "Post created.", "meta": {} }
```

---

## Quick start

### 1. Install (with `uv`)

```bash
git clone <your-repo-url> wpmcp
cd wpmcp
uv sync
```

### 2. Configure a single site

Copy the example env file and fill in your WordPress credentials:

```bash
cp .env.example .env
```

```dotenv
# Server
WPMCP_HOST=127.0.0.1
WPMCP_PORT=8787
WPMCP_TRANSPORT=http
# Optional: require clients to present this bearer token
WPMCP_BEARER_TOKEN=

# Default site used when a tool omits the `site` argument
WPMCP_DEFAULT_SITE=primary

# Single site connection
WPMCP_SITE_PRIMARY_URL=https://your-site.com
WPMCP_SITE_PRIMARY_USERNAME=admin
WPMCP_SITE_PRIMARY_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

`WPMCP_SITE_PRIMARY_PASSWORD` is a **WordPress Application Password** — generate one in WordPress at **Users → Profile → Application Passwords**. The WordPress user needs capabilities appropriate to the actions you want to run (e.g. `edit_posts`, `manage_options`, `edit_themes`, `edit_plugins`).

### 3. Run the remote server

```bash
uv run wpmcp
```

The MCP endpoint is now live at:

```
http://127.0.0.1:8787/mcp
```

---

## Multisite usage

WPMCP can manage **many WordPress installs** from one server. Register each site with a `WPMCP_SITE_<ALIAS>_*` block — the alias is the name you pass to tools.

```dotenv
WPMCP_DEFAULT_SITE=primary

# Production site
WPMCP_SITE_PRIMARY_URL=https://your-site.com
WPMCP_SITE_PRIMARY_USERNAME=admin
WPMCP_SITE_PRIMARY_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Staging site
WPMCP_SITE_STAGING_URL=https://staging.your-site.com
WPMCP_SITE_STAGING_USERNAME=admin
WPMCP_SITE_STAGING_PASSWORD=yyyy yyyy yyyy yyyy yyyy yyyy

# A completely different install
WPMCP_SITE_SHOP_URL=https://shop.example.com
WPMCP_SITE_SHOP_USERNAME=admin
WPMCP_SITE_SHOP_PASSWORD=zzzz zzzz zzzz zzzz zzzz zzzz
```

Now any tool can target a specific site by passing its alias:

```jsonc
// Create a post on staging
{ "action": "create_post", "site": "staging", "params": { "title": "Hello", "status": "draft" } }

// List plugins on the shop site
{ "action": "get_plugins", "site": "shop" }

// Omit `site` to use the default (primary)
{ "action": "get_posts", "params": { "per_page": 10 } }
```

Discover every registered connection:

```jsonc
{ "action": "list_sites" }   // via wp_sites
```

> **Note:** "multisite" here means *many independent WordPress installs* managed by one WPMCP server. If your WordPress itself is a multisite network, `wp_sites` also exposes `list_network_sites`, `create_network_site`, and `delete_network_site` to manage sites within that network.

---

## Connecting an MCP client

WPMCP is a **remote** server, so clients connect by URL rather than launching a local process.

### Cursor

`Settings → MCP → Add MCP server`:

```json
{
  "mcpServers": {
    "wordpress": {
      "url": "http://127.0.0.1:8787/mcp"
    }
  }
}
```

If you set `WPMCP_BEARER_TOKEN`, add headers:

```json
{
  "mcpServers": {
    "wordpress": {
      "url": "http://127.0.0.1:8787/mcp",
      "headers": { "Authorization": "Bearer YOUR_TOKEN" }
    }
  }
}
```

### Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "wordpress": {
      "transport": {
        "type": "http",
        "url": "http://127.0.0.1:8787/mcp",
        "headers": { "Authorization": "Bearer YOUR_TOKEN" }
      }
    }
  }
}
```

### Any MCP client

Point the client at `http://<host>:8787/mcp` using the Streamable HTTP transport.

---

## Using the tools

Start a conversation with: *"Call wp_discover to see what you can do."* The model will read the full action catalog, then dispatch.

A few examples of what you can say:

- *"Create a draft post titled 'Hello World' on the staging site."*
- *"List all installed plugins and tell me which are inactive."*
- *"Create a child theme of twentytwentyfive called Studio."*
- *"Read the style.css file from my active theme."*
- *"Show me the database tables and the structure of wp_posts."*
- *"Get my latest 10 WooCommerce orders and total revenue."*
- *"Run a site audit — health, updates, and performance."*
- *"Back up the database, then list all backups."*

### Direct tool contract

```jsonc
{
  "action": "create_post",        // required: an action from wp_discover
  "site": "primary",              // optional: multisite alias (defaults to WPMCP_DEFAULT_SITE)
  "params": {                     // optional: action-specific parameters
    "title": "Hello World",
    "content": "<p>Body</p>",
    "status": "publish"
  }
}
```

---

## The generative UI

Every tool result renders inside an interactive console (served as the `ui://wpmcp/console-v1.html` MCP resource). The UI switches renderers based on the result's `view` field — dashboards, post tables, media galleries, plugin grids, theme inspectors, database tables, WooCommerce orders, cron jobs, backups, and more — with quick-action buttons that open forms and call back into the server. Supported clients render this automatically; text-only clients still get the full structured JSON.

---

## Security

- **Server auth** — set `WPMCP_BEARER_TOKEN` to require a bearer token from every client.
- **WordPress auth** — each site uses a scoped Application Password over HTTPS Basic.
- **Filesystem** — paths are restricted to `wp-content/themes`, `wp-content/plugins`, `wp-content/uploads`, `wp-content/mu-plugins`; traversal is blocked.
- **Database** — only `SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN` statements are permitted.
- **Destructive actions** — flagged in the `wp_discover` catalog so the model can confirm with you before running them.

---

## Project structure

```
src/wpmcp/
  server.py            composition + entrypoint (bearer auth, streamable-http)
  core/                config, exceptions, logging
  wordpress/           async httpx client (pooling), endpoint map, multisite registry
  domain/              WpResult envelope, View enum, action catalog models
  services/            one service per WordPress domain (real REST calls)
  tools/               17 gateway tools, dispatch, annotations, app config
  resources/           wp://capabilities, wp://action-catalog, wp://sites
  prompts/             reusable workflow prompts
  ui/                  console.html + CSS/JS renderers, registered as an MCP resource
scripts/verify_surface.py   lists tools, resources, prompts, and the action catalog
```

---

## Scripts

Verify the server surface without a live WordPress connection:

```bash
uv run python scripts/verify_surface.py
```

This prints every tool, resource, prompt, the full action catalog, and confirms the UI resource renders.

---

## Deployment

A `Dockerfile` is included. Build and run:

```bash
docker build -t wpmcp .
docker run --env-file .env -p 8787:8787 wpmcp
```

Behind a reverse proxy (recommended for remote exposure), set `proxy_buffering off` and a long `proxy_read_timeout` — Streamable HTTP streams responses and will break if the proxy buffers them.

---

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `WPMCP_HOST` | `127.0.0.1` | Bind address |
| `WPMCP_PORT` | `8787` | Bind port |
| `WPMCP_TRANSPORT` | `http` | Streamable HTTP transport |
| `WPMCP_BEARER_TOKEN` | _none_ | Optional bearer token clients must present |
| `WPMCP_DEFAULT_SITE` | `primary` | Site alias used when `site` is omitted |
| `WPMCP_SITE_<ALIAS>_URL` | — | WordPress URL for alias `<ALIAS>` |
| `WPMCP_SITE_<ALIAS>_USERNAME` | — | WordPress admin username |
| `WPMCP_SITE_<ALIAS>_PASSWORD` | — | WordPress Application Password |

---

MIT License — built for AI-powered WordPress development.
