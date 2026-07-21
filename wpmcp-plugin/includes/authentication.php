<?php
/**
 * WPMCP Authentication — production-grade.
 *
 * Two supported mechanisms:
 *  1. Bearer API token (recommended): `Authorization: Bearer <WPMCP_API_TOKEN>`
 *     - Defined as a constant in wp-config.php (or via the `wpmcp_api_token` filter).
 *     - Honored only over HTTPS unless WPMCP_ALLOW_INSECURE is true.
 *     - Acts as the user whose login is WPMCP_API_USER (or `wpmcp_api_user` filter).
 *  2. WordPress Application Passwords (core): standard Basic Auth with a
 *     per-user application password. Handled natively by WP core 5.6+.
 *
 * The legacy main-password Basic Auth handler has been removed — this plugin
 * never accepts a user's real login password over the REST API.
 *
 * Hardening:
 *  - The wpmcp/v1 namespace rejects unauthenticated requests with a 401.
 *  - Failed bearer attempts are rate-limited per IP via transients.
 *  - All auth decisions are written to wp-content/wpmcp-logs/auth-audit.log.
 *  - Token comparison is constant-time (hash_equals over SHA-256 hashes).
 */

if ( ! defined( 'ABSPATH' ) ) exit;

class WPMCP_Authentication {

	const RATE_LIMIT_MAX  = 5;    // failures before lockout
	const RATE_LIMIT_LOCK = 900;  // 15-minute lockout window

	public function __construct() {
		add_filter( 'determine_current_user', array( $this, 'authenticate_bearer' ), 15 );
		add_filter( 'rest_pre_dispatch', array( $this, 'enforce_namespace_auth' ), 10, 3 );
	}

	/** The expected bearer token hash (from option, or constant override). */
	private function expected_hash() {
		$hash = '';
		if ( defined( 'WPMCP_API_TOKEN' ) && WPMCP_API_TOKEN ) {
			$hash = hash( 'sha256', WPMCP_API_TOKEN );
		} else {
			$hash = (string) get_option( 'wpmcp_token_hash', '' );
		}
		return (string) apply_filters( 'wpmcp_token_hash', $hash );
	}

	/** The WP user login the token acts as. */
	private function api_user_login() {
		$login = '';
		if ( defined( 'WPMCP_API_USER' ) && WPMCP_API_USER ) {
			$login = (string) WPMCP_API_USER;
		} else {
			$login = (string) get_option( 'wpmcp_api_user', '' );
		}
		return (string) apply_filters( 'wpmcp_api_user', $login );
	}

	private function allow_insecure() {
		$allow = defined( 'WPMCP_ALLOW_INSECURE' ) && WPMCP_ALLOW_INSECURE;
		return (bool) apply_filters( 'wpmcp_allow_insecure_transport', $allow );
	}

	/**
	 * Authenticate a bearer token. Falls through silently if no bearer header
	 * is present, so core can still handle Application Passwords.
	 */
	public function authenticate_bearer( $user_id ) {
		if ( ! empty( $user_id ) ) {
			return $user_id;
		}
		if ( ! ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
			return $user_id;
		}

		$auth = '';
		if ( isset( $_SERVER['HTTP_AUTHORIZATION'] ) ) {
			$auth = $_SERVER['HTTP_AUTHORIZATION'];
		} elseif ( function_exists( 'apache_request_headers' ) ) {
			$headers = apache_request_headers();
			$auth = $headers['Authorization'] ?? ( $headers['authorization'] ?? '' );
		}

		if ( ! preg_match( '/^Bearer\s+(.+)$/i', $auth, $m ) ) {
			return $user_id; // Not a bearer request — let core handle app passwords.
		}

		$provided      = trim( $m[1] );
		$expected_hash = $this->expected_hash();

		if ( '' === $expected_hash ) {
			$this->audit( 'bearer:rejected', 'no token configured' );
			return $user_id;
		}

		if ( ! is_ssl() && ! $this->allow_insecure() ) {
			$this->audit( 'bearer:rejected', 'insecure transport (http)' );
			return $user_id;
		}

		if ( $this->is_locked_out() ) {
			$this->audit( 'bearer:locked', 'rate limit exceeded' );
			return $user_id;
		}

		// Constant-time comparison of the provided token's hash to the stored hash.
		$valid = hash_equals( $expected_hash, hash( 'sha256', $provided ) );

		if ( ! $valid ) {
			$this->record_failure();
			$this->audit( 'bearer:failed', 'bad token' );
			return $user_id;
		}

		$login  = $this->api_user_login();
		$actor  = $login ? get_user_by( 'login', $login ) : false;
		if ( ! $actor ) {
			$this->audit( 'bearer:failed', 'unknown api user: ' . $login );
			return $user_id;
		}

		$this->clear_failures();
		$this->audit( 'bearer:success', 'user=' . $actor->user_login );
		return $actor->ID;
	}

	/**
	 * Reject any unauthenticated request to the wpmcp/v1 namespace with a 401.
	 * Runs after determine_current_user so the user is already resolved.
	 */
	public function enforce_namespace_auth( $result, $server, $request ) {
		if ( null !== $result ) {
			return $result;
		}
		$route = $request->get_route();
		if ( $route && 0 === strpos( $route, '/wpmcp/v1' ) && ! get_current_user_id() ) {
			return new WP_Error(
				'wpmcp_not_authenticated',
				'WPMCP endpoints require authentication (bearer token or application password).',
				array( 'status' => 401 )
			);
		}
		return $result;
	}

	private function client_ip() {
		$ip = isset( $_SERVER['REMOTE_ADDR'] ) ? $_SERVER['REMOTE_ADDR'] : '0.0.0.0';
		return preg_replace( '/[^0-9a-fA-F.:]/', '', $ip );
	}

	private function lock_key() {
		return 'wpmcp_auth_fail_' . md5( $this->client_ip() );
	}

	private function is_locked_out() {
		return (int) get_transient( $this->lock_key() ) >= self::RATE_LIMIT_MAX;
	}

	private function record_failure() {
		$key   = $this->lock_key();
		$count = (int) get_transient( $key );
		set_transient( $key, $count + 1, self::RATE_LIMIT_LOCK );
	}

	private function clear_failures() {
		delete_transient( $this->lock_key() );
	}

	private function audit( $status, $detail ) {
		$dir = WP_CONTENT_DIR . '/wpmcp-logs';
		if ( ! is_dir( $dir ) ) {
			wp_mkdir_p( $dir );
			@file_put_contents( $dir . '/.htaccess', "Deny from all\n" );
			@file_put_contents( $dir . '/index.html', '' );
		}
		$line = sprintf( "[%s] %s | ip=%s | %s\n", current_time( 'mysql' ), $status, $this->client_ip(), $detail );
		@file_put_contents( $dir . '/auth-audit.log', $line, FILE_APPEND );
	}
}
