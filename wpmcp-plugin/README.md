# WordPress MCP Server Plugin

**Version:** 2.4.0  
**Requires WordPress:** 5.0+  
**Requires PHP:** 7.4+  
**License:** MIT

## Overview

The companion plugin for the WPMCP remote MCP server. It exposes the extended `wpmcp/v1` REST endpoints that the server calls for capabilities not covered by the core WordPress REST API:

- ✅ File System Operations (read, write, delete, copy, move, list, info)
- ✅ Shortcode Management (list, execute)
- ✅ Cron Job Scheduling (list, schedule, unschedule, run)
- ✅ Database Operations (tables, SELECT-only queries, options)
- ✅ Security Monitoring (site health, updates, debug log, core integrity, system info)
- ✅ Performance Optimization (cache, optimize, cleanup, flush rewrites)
- ✅ WP-CLI Execution (whitelisted commands only)

## Quick Setup (recommended — 3 steps, no code)

1. **Install & activate** the plugin (upload the zip via **Plugins → Add New → Upload Plugin**, or `wp plugin activate wpmcp-plugin`).
2. Open **WPMCP** in the admin sidebar → click **Generate connection**. Copy the token shown (shown once).
3. Paste the **Cursor config** block from the same page into **Settings → MCP → Add custom MCP**. Done.

No `wp-config.php` editing, no Python, no `.env`. The token is stored hashed in the database and validated in constant time over HTTPS. Self-hosters can change the **MCP server URL** on the same page and use the provided `.env` block.

## Quick Installation

### Method 1: Upload via WordPress Admin

1. Download the `wpmcp-plugin` folder as a zip
2. Go to **WordPress Admin → Plugins → Add New → Upload Plugin**
3. Upload the zip
4. Click **Activate**

### Method 2: Manual Upload

```bash
# SSH into your WordPress server
cd /path/to/wordpress/wp-content/plugins

# Create plugin directory
mkdir wpmcp-plugin
cd wpmcp-plugin

# Copy the plugin file
# Upload wpmcp-plugin.php to this directory

# Set permissions
chmod 644 wpmcp-plugin.php

# Activate via WordPress Admin → Plugins
```

### Method 3: WP-CLI

```bash
wp plugin install /path/to/wpmcp-plugin.php
wp plugin activate wpmcp-plugin
```

## Features

### File System Operations

**Endpoints:**
- `/wp-json/wpmcp/v1/file/read` - Read file contents
- `/wp-json/wpmcp/v1/file/write` - Create/modify files
- `/wp-json/wpmcp/v1/file/delete` - Remove files
- `/wp-json/wpmcp/v1/file/copy` - Duplicate files
- `/wp-json/wpmcp/v1/file/move` - Relocate files
- `/wp-json/wpmcp/v1/file/list` - List directory contents
- `/wp-json/wpmcp/v1/file/info` - Get file metadata

**Security:**
- Allowed directories: `wp-content/themes/`, `wp-content/plugins/`, `wp-content/uploads/`, `wp-content/mu-plugins/`
- Allowed extensions: `.php`, `.js`, `.css`, `.scss`, `.json`, `.html`, `.xml`, `.txt`, `.md`, images
- Automatic backups before modifications
- Path validation (prevents directory traversal)
- File size limit: 10MB
- Requires `edit_themes` + `edit_plugins` capabilities

### Shortcode Management

**Endpoints:**
- `/wp-json/wpmcp/v1/shortcodes/list` - Get all registered shortcodes
- `/wp-json/wpmcp/v1/shortcodes/execute` - Process shortcode string

**Use Cases:**
- Discover available shortcodes
- Test shortcode output
- Execute shortcodes programmatically

### Cron Job Scheduling

**Endpoints:**
- `/wp-json/wpmcp/v1/cron/list` - Get all scheduled events
- `/wp-json/wpmcp/v1/cron/schedule` - Create scheduled task
- `/wp-json/wpmcp/v1/cron/unschedule` - Remove scheduled event
- `/wp-json/wpmcp/v1/cron/run` - Trigger cron manually

**Use Cases:**
- Monitor scheduled tasks
- Add custom recurring events
- Debug cron issues
- Run maintenance tasks

### Widget System

**Access via WordPress REST API:**
- `/wp/v2/sidebars` - Widget areas
- `/wp/v2/widgets` - All widgets
- `/wp/v2/widget-types` - Available widget types

**Note:** Widgets use standard WordPress REST API endpoints.

### WP-CLI Execution

**Endpoints:**
- `POST /wp-json/wpmcp/v1/cli/run` - Run a whitelisted WP-CLI command
- `GET /wp-json/wpmcp/v1/cli/allowed` - List permitted commands

**Allowlist** (two- or three-token subcommands):
`plugin install|update|delete|activate|deactivate`, `theme install|update|delete|activate`, `core update|update-db|version`, `cache flush`, `cron event run|list`, `db export|size`, `user list`, `option get|update`.

**Safety:**
- The remote MCP server validates the command before forwarding; this plugin re-validates server-side as defense in depth.
- Shell metacharacters (`; | & $ \` > <`) are rejected — WP-CLI arguments only.
- Commands run with array-form `proc_open` (PHP 7.4+) which bypasses the shell entirely, so no metacharacter can be interpreted.
- Every attempt is appended to `wp-content/wpmcp-logs/cli-audit.log`.
- Requires `manage_options` capability.

**Configure the WP-CLI binary** (if `wp` is not on the server's PATH) via a filter in your theme's `functions.php`:

```php
add_filter('wpmcp_wp_binary', function () {
    return ['php', '/usr/local/bin/wp-cli.phar'];
});
```

## Configuration

### Permissions Required

**File Operations:**
- User must have `edit_themes` capability
- User must have `edit_plugins` capability

**Advanced Features:**
- User must have `manage_options` capability (administrator)

### Backup System

**Location:** `wp-content/wpmcp-backups/`

**Features:**
- Automatic backups before file modifications
- Metadata stored (.meta files)
- Protected with `.htaccess` (deny web access)
- Manual restore capability

**Backup Structure:**
```
wp-content/wpmcp-backups/
├── backup_xyz123.bak       # Backed up file
├── backup_xyz123.bak.meta  # Metadata (JSON)
└── .htaccess               # Protection
```

## Security

### Authentication (production)

The plugin supports two authentication mechanisms, in order of preference:

**1. Bearer API token (recommended for remote/headless use)**

Easiest: open **WPMCP** in the admin sidebar → **Generate connection**. The token is created and stored hashed in the database; copy it (shown once). No file editing.

Power users can instead define constants in `wp-config.php` (above the `/* That's all, stop editing! */` line), which override the database value:

```php
define( 'WPMCP_API_TOKEN', 'long-random-shared-secret' );
define( 'WPMCP_API_USER', 'admin' ); // login of the WP user the token acts as
// define( 'WPMCP_ALLOW_INSECURE', true ); // only for local HTTP testing
```

The MCP server sends `Authorization: Bearer <token>`. The plugin validates it in constant time (`hash_equals` over SHA-256), only over HTTPS, and acts as the configured user for capability checks. Per-IP rate limiting locks out after 5 failed attempts for 15 minutes. All decisions are logged to `wp-content/wpmcp-logs/auth-audit.log`.

**2. WordPress Application Passwords (fallback)**

Standard Basic Auth with a per-user application password, handled natively by WordPress core 5.6+. Create one at **Users → Profile → Application Passwords**. The user's **main login password is never accepted** over the REST API — the legacy Basic Auth handler that allowed it has been removed.

### Namespace guard

Every `/wpmcp/v1/*` route rejects unauthenticated requests with HTTP 401 before any route logic runs.

### File System Protection

**Whitelist Approach:**
- Only specified directories allowed
- Only approved file extensions
- Path traversal attempts blocked
- Automatic backup before changes

**Forbidden Directories:**
- WordPress core files
- System directories
- User directories
- Database directories

### Permission System

All endpoints require proper WordPress capabilities:
- File operations: `edit_themes` AND `edit_plugins`
- Admin operations: `manage_options`

### Best Practices

1. ✅ Use strong admin passwords
2. ✅ Enable HTTPS
3. ✅ Keep WordPress updated
4. ✅ Regular backups
5. ✅ Monitor plugin changes
6. ✅ Limit admin access

## API Usage Examples

### Read Theme File

```http
POST /wp-json/wpmcp/v1/file/read
Content-Type: application/json
Authorization: Basic {base64(username:password)}

{
  "path": "wp-content/themes/mytheme/style.css"
}
```

### List Shortcodes

```http
GET /wp-json/wpmcp/v1/shortcodes/list
Authorization: Basic {base64(username:password)}
```

### Schedule Cron Job

```http
POST /wp-json/wpmcp/v1/cron/schedule
Content-Type: application/json
Authorization: Basic {base64(username:password)}

{
  "hook": "my_custom_task",
  "recurrence": "daily",
  "args": []
}
```

## Troubleshooting

### "Permission denied" Error
- Verify user has required capabilities
- Check file permissions on server
- Ensure WordPress user can write to directories

### "File not found" Error
- Check file path is correct
- Verify file exists in WordPress
- Ensure path uses forward slashes

### "Path not allowed" Error
- File must be in allowed directories
- Cannot access core WordPress files
- Cannot access system files

### Plugin Not Working
- Check plugin is activated
- Verify WordPress version 5.0+
- Ensure PHP 7.4+
- Check REST API is enabled

## Changelog

### Version 2.4.0 (2026-07-22)
- Added one-click **WPMCP** admin page: generate a bearer token (stored hashed), copy Cursor config and self-host `.env` blocks. No `wp-config.php` editing required.
- Authentication now reads the token hash from `wp_options` (with `wp-config.php` constant override for power users).

### Version 2.3.0 (2026-07-22)
- Added WP-CLI execution module (`/cli/run`, `/cli/allowed`) with strict allowlist, metacharacter rejection, shell-bypassing execution, and an audit log.
- Bumped PHP requirement to 7.4+ for array-form `proc_open`.

### Version 2.2.0
- Added database, security, and performance modules.

### Version 2.0.0 (2024-10-25)
- Complete rewrite combining all features
- File system operations
- Shortcode management
- Cron job scheduling
- Enhanced security
- Automatic backups
- Comprehensive error handling

### Version 1.0.0 (2024-10-24)
- Initial release (file system only)

## Support

- **GitHub:** https://github.com/RaheesAhmed/wordpress-mcp-server
- **Issues:** Report bugs or request features
- **Documentation:** See main project README

## License

MIT License - See LICENSE in main project

---

**⚠️ Important:** This plugin provides powerful WordPress control. Only install on trusted WordPress installations with proper admin security.