<?php
/**
 * WPMCP Settings — one-click pairing UI.
 *
 * Generates a bearer API token, stores only its SHA-256 hash in wp_options
 * (the plaintext is shown once, like an application password), and renders
 * ready-to-paste connection blocks for Cursor / Claude / self-host .env.
 * No wp-config.php editing required.
 */

if ( ! defined( 'ABSPATH' ) ) exit;

class WPMCP_Settings {

	const OPT_HASH   = 'wpmcp_token_hash';
	const OPT_USER   = 'wpmcp_api_user';
	const OPT_SERVER = 'wpmcp_server_url';
	const DEFAULT_SERVER = 'https://mcp.wpmcp.app/mcp';

	public function __construct() {
		add_action( 'admin_menu', array( $this, 'menu' ) );
		add_action( 'admin_post_wpmcp_save', array( $this, 'handle_save' ) );
	}

	public function menu() {
		add_menu_page(
			'WPMCP',
			'WPMCP',
			'manage_options',
			'wpmcp',
			array( $this, 'render' ),
			'dashicons-rest-api',
			76
		);
	}

	public static function token_hash() {
		return (string) get_option( self::OPT_HASH, '' );
	}

	public static function api_user() {
		$login = (string) get_option( self::OPT_USER, '' );
		if ( '' === $login ) {
			$login = wp_get_current_user()->user_login;
		}
		return $login;
	}

	public static function server_url() {
		$url = (string) get_option( self::OPT_SERVER, '' );
		return '' === $url ? self::DEFAULT_SERVER : $url;
	}

	public function handle_save() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Insufficient permissions.' );
		}
		check_admin_referer( 'wpmcp_save' );

		$action = isset( $_POST['wpmcp_action'] ) ? sanitize_key( $_POST['wpmcp_action'] ) : 'save';

		update_option( self::OPT_USER, sanitize_text_field( wp_unslash( $_POST['api_user'] ?? '' ) ) );
		update_option( self::OPT_SERVER, esc_url_raw( wp_unslash( $_POST['server_url'] ?? self::DEFAULT_SERVER ) ) );

		if ( 'generate' === $action || '' === self::token_hash() ) {
			$token = wp_generate_password( 40, false );
			update_option( self::OPT_HASH, hash( 'sha256', $token ) );
			set_transient( 'wpmcp_new_token_' . get_current_user_id(), $token, 180 );
		}

		wp_safe_redirect( add_query_arg( 'updated', '1', admin_url( 'admin.php?page=wpmcp' ) ) );
		exit;
	}

	public function render() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$server    = self::server_url();
		$user      = self::api_user();
		$has_token = (bool) self::token_hash();
		$new_token = $has_token ? (string) get_transient( 'wpmcp_new_token_' . get_current_user_id() ) : '';
		if ( '' !== $new_token ) {
			delete_transient( 'wpmcp_new_token_' . get_current_user_id() );
		}
		$https = is_ssl();
		?>
		<div class="wrap wpmcp-wrap">
			<h1>WPMCP — Remote WordPress MCP</h1>
			<p class="wpmcp-lead">Connect your AI client to this site in one click. No code, no config files.</p>

			<?php if ( ! $https ) : ?>
				<div class="notice notice-error"><p><strong>HTTPS required.</strong> Bearer tokens are only accepted over HTTPS. Serve this site over HTTPS before generating a connection.</p></div>
			<?php endif; ?>

			<?php if ( '' !== $new_token ) : ?>
				<div class="notice notice-success wpmcp-token-notice">
					<p><strong>Connection token created.</strong> Copy it now — it is shown only once.</p>
					<input class="wpmcp-token-box" readonly value="<?php echo esc_attr( $new_token ); ?>" />
					<button type="button" class="button wpmcp-copy" data-target=".wpmcp-token-box">Copy token</button>
				</div>
			<?php endif; ?>

			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<input type="hidden" name="action" value="wpmcp_save" />
				<?php wp_nonce_field( 'wpmcp_save' ); ?>

				<table class="form-table" role="presentation">
					<tr>
						<th scope="row"><label for="api_user">WordPress user</label></th>
						<td><input name="api_user" id="api_user" class="regular-text" value="<?php echo esc_attr( $user ); ?>" />
							<p class="description">The WP user the MCP server acts as (must be an administrator).</p></td>
					</tr>
					<tr>
						<th scope="row"><label for="server_url">MCP server URL</label></th>
						<td><input name="server_url" id="server_url" class="regular-text" value="<?php echo esc_attr( $server ); ?>" />
							<p class="description">Default is the hosted WPMCP endpoint. Self-hosters: point this at your own server.</p></td>
					</tr>
				</table>

				<p class="submit">
					<button type="submit" name="wpmcp_action" value="generate" class="button button-primary">
						<?php echo $has_token ? 'Regenerate token' : 'Generate connection'; ?>
					</button>
					<button type="submit" name="wpmcp_action" value="save" class="button">Save settings</button>
				</p>
			</form>

			<?php if ( $has_token && '' === $new_token ) : ?>
				<div class="card wpmcp-card">
					<h2>Connection active</h2>
					<p>A token is configured on this site. To reveal a new token (and invalidate the old one), click <em>Regenerate token</em>.</p>
				</div>
			<?php endif; ?>

			<?php if ( $has_token ) : ?>
				<div class="card wpmcp-card">
					<h2>Cursor config</h2>
					<p>Paste into <code>Settings → MCP → Add custom MCP</code>:</p>
					<textarea class="wpmcp-block" readonly>{ "mcpServers": { "wpmcp": { "url": "<?php echo esc_js( $server ); ?>", "headers": { "Authorization": "Bearer <token>" } } } }</textarea>
					<button type="button" class="button wpmcp-copy" data-target=".wpmcp-block">Copy</button>
				</div>

				<div class="card wpmcp-card">
					<h2>Self-host .env (optional)</h2>
					<p>Only if you run the WPMCP server yourself:</p>
					<textarea class="wpmcp-env" readonly>WPMCP_SITE_PRIMARY_URL=<?php echo esc_js( home_url() ); ?>
WPMCP_SITE_PRIMARY_USERNAME=<?php echo esc_js( $user ); ?>
WPMCP_SITE_PRIMARY_PASSWORD=<app-password>
WPMCP_SITE_PRIMARY_TOKEN=<token></textarea>
					<button type="button" class="button wpmcp-copy" data-target=".wpmcp-env">Copy</button>
				</div>
			<?php endif; ?>
		</div>
		<style>
			.wpmcp-lead{font-size:14px;color:#646970}
			.wpmcp-token-box{width:100%;max-width:560px;padding:8px 10px;font-family:monospace;background:#f6f7f7}
			.wpmcp-card{max-width:640px;margin-top:16px;padding:12px 16px}
			.wpmcp-block,.wpmcp-env{width:100%;height:90px;font-family:monospace;font-size:12px;white-space:pre}
			.wpmcp-copy{margin-top:8px}
		</style>
		<script>
			document.querySelectorAll('.wpmcp-copy').forEach(function (btn) {
				btn.addEventListener('click', function () {
					var el = document.querySelector(btn.getAttribute('data-target'));
					el.select(); document.execCommand('copy');
					var t = btn.textContent; btn.textContent = 'Copied!';
					setTimeout(function () { btn.textContent = t; }, 1200);
				});
			});
		</script>
		<?php
	}
}

new WPMCP_Settings();
