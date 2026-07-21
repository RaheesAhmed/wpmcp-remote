"""Standalone checks for wp_cli validation and the password generator."""

from wpmcp.core.exceptions import SecurityError
from wpmcp.services.cli_service import ALLOWED_COMMANDS, _validate
from wpmcp.services.users_service import _generate_password

CASES = [
    ("plugin install akismet", True),
    ("plugin update --all", True),
    ("core update", True),
    ("core update-db", True),
    ("option get siteurl", True),
    ("db export /tmp/x.sql", True),
    ("user list", True),
    ("cron event list", True),
    ("plugin install x; rm -rf /", False),  # shell metacharacter
    ("core update && whoami", False),       # shell chaining
    ("option get x > /etc/passwd", False),   # redirection
    ("eval phpinfo();", False),              # not on allowlist + metachar
    ("shell", False),                        # single token, not allowed
    ("rewrite flush", False),                # not on allowlist
    ("db query SELECT 1", False),            # db query not allowed
]

print(f"allowlist size: {len(ALLOWED_COMMANDS)}\n")
all_ok = True
for command, should_pass in CASES:
    try:
        _validate(command)
        passed = True
        err = ""
    except SecurityError as exc:
        passed = False
        err = str(exc)
    status = "PASS" if passed == should_pass else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"[{status}] expect={'allow' if should_pass else 'reject'} cmd={command!r}")
    if err:
        print(f"        -> {err}")

pw = _generate_password()
print(f"\nsample password ({len(pw)} chars): {pw}")
print("all cases passed:", all_ok)
