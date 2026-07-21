<?php
/**
 * WPMCP WP-CLI Operations
 *
 * Executes a strict allowlist of WP-CLI commands in the WordPress root.
 * The remote MCP server validates the command before forwarding it; this
 * module re-validates server-side as defense in depth, then runs the command
 * without a shell (array-form proc_open on PHP 7.4+) so no metacharacter can
 * ever be interpreted. Every attempt is written to an append-only audit log.
 */

if (!defined('ABSPATH')) exit;

class WPMCP_CLI {

    /** @var string[] Allowlisted two- or three-token WP-CLI subcommands. */
    private $allowed = [
        'plugin install',
        'plugin update',
        'plugin delete',
        'plugin activate',
        'plugin deactivate',
        'theme install',
        'theme update',
        'theme delete',
        'theme activate',
        'core update',
        'core update-db',
        'core version',
        'cache flush',
        'cron event run',
        'cron event list',
        'db export',
        'db size',
        'user list',
        'option get',
        'option update',
    ];

    public function __construct() {
        add_action('rest_api_init', [$this, 'register_routes']);
    }

    public function register_routes() {
        $ns = 'wpmcp/v1';
        register_rest_route($ns, '/cli/run', [
            'methods'             => 'POST',
            'callback'            => [$this, 'run_command'],
            'permission_callback' => [$this, 'check_permissions'],
        ]);
        register_rest_route($ns, '/cli/allowed', [
            'methods'             => 'GET',
            'callback'            => [$this, 'list_allowed'],
            'permission_callback' => [$this, 'check_permissions'],
        ]);
    }

    public function check_permissions() {
        return current_user_can('manage_options');
    }

    /**
     * Return the current allowlist (mirrors the MCP server's catalog).
     */
    public function list_allowed() {
        return ['allowed' => $this->allowed, 'count' => count($this->allowed)];
    }

    /**
     * Validate and execute a whitelisted WP-CLI command.
     */
    public function run_command($request) {
        $command = trim((string) $request->get_param('command'));
        if ($command === '') {
            return new WP_Error('empty_command', 'Command is required.');
        }

        // Defense in depth: reject shell metacharacters before any execution.
        if (preg_match('/[;|&$`><\n\r]/', $command)) {
            $this->audit('rejected:metachar', $command);
            return new WP_Error(
                'forbidden_metachar',
                'Command contains forbidden shell metacharacters. Only WP-CLI arguments are allowed.'
            );
        }

        $tokens = array_values(array_filter(preg_split('/\s+/', $command)));
        if (count($tokens) < 2) {
            $this->audit('rejected:not_allowed', $command);
            return new WP_Error(
                'not_allowed',
                'Command is not on the allowlist. Use /cli/allowed to see permitted commands.'
            );
        }

        // Match the command's leading tokens against any allowlist entry.
        $matched = false;
        foreach ($this->allowed as $allowed) {
            $allowedTokens = preg_split('/\s+/', $allowed);
            $n = count($allowedTokens);
            if ($n >= 2 && array_slice($tokens, 0, $n) === $allowedTokens) {
                $matched = true;
                break;
            }
        }
        if (!$matched) {
            $this->audit('rejected:not_allowed', $command);
            return new WP_Error(
                'not_allowed',
                'Command is not on the allowlist. Permitted: ' . implode(', ', $this->allowed) . '.'
            );
        }

        $binary = apply_filters('wpmcp_wp_binary', ['wp']);
        if (!is_array($binary)) {
            $binary = array_values(array_filter(preg_split('/\s+/', (string) $binary)));
        }
        $argv = array_merge($binary, $tokens);

        $this->audit('dispatched', $command);

        $result = $this->execute($argv);
        $this->audit('complete:' . $result['exit_code'], $command);
        return $result;
    }

    /**
     * Execute an argv array in the WordPress root, bypassing the shell when
     * possible (PHP 7.4+ array-form proc_open). Falls back to an escaped string.
     */
    private function execute(array $argv) {
        $cwd = untrailingslashit(ABSPATH);
        $descriptors = [
            0 => ['file', '/dev/null', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $use_array = version_compare(PHP_VERSION, '7.4.0', '>=');
        $command = $use_array ? $argv : implode(' ', array_map('escapeshellarg', $argv));

        $proc = @proc_open($command, $descriptors, $pipes, $cwd);
        if (!is_resource($proc)) {
            return [
                'success'    => false,
                'stdout'      => '',
                'stderr'      => 'Failed to start WP-CLI. Is it installed and on PATH? Filter "wpmcp_wp_binary" to set its path.',
                'exit_code'   => 127,
            ];
        }

        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        $exit_code = proc_close($proc);

        return [
            'success'    => $exit_code === 0,
            'stdout'      => $stdout,
            'stderr'      => $stderr,
            'exit_code'   => $exit_code,
            'command'     => implode(' ', $argv),
        ];
    }

    /**
     * Append one audit record to the plugin's CLI audit log.
     */
    private function audit($status, $command) {
        $dir = WP_CONTENT_DIR . '/wpmcp-logs';
        if (!is_dir($dir)) {
            wp_mkdir_p($dir);
            @file_put_contents($dir . '/.htaccess', "Deny from all\n");
            @file_put_contents($dir . '/index.html', '');
        }
        $line = sprintf(
            "[%s] %s | %s\n",
            current_time('mysql'),
            $status,
            $command
        );
        @file_put_contents($dir . '/cli-audit.log', $line, FILE_APPEND);
    }
}
