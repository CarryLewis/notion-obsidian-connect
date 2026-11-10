#!/usr/bin/env bash
# Diagnose Notion → Obsidian auto-sync on macOS.
set -u

REPO="${RESEARCH_BRIEF_REPO:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)}"
VAULT="${OBSIDIAN_VAULT:-${DEFAULT_VAULT_PATH:-}}"
LABEL="${THINKING_LAUNCHAGENT_LABEL:-io.personal-knowledge-bridge.thinking-sync-daily}"
PLIST="${THINKING_LAUNCHAGENT_PLIST:-$HOME/Library/LaunchAgents/$LABEL.plist}"
LOG="${SYNC_LOG:-$HOME/Library/Logs/thinking-vault-sync.log}"
UID_NUM="$(id -u)"

echo "=== Thinking Vault local sync check ==="
echo "time: $(date)"
echo "repo:  $REPO"
echo "vault: $VAULT"
echo

ok=0; warn=0; bad=0
pass() { echo "OK   $1"; ok=$((ok+1)); }
warn() { echo "WARN $1"; warn=$((warn+1)); }
fail() { echo "FAIL $1"; bad=$((bad+1)); }

# 1) repo + script
if [[ -e "$REPO/.git" ]]; then pass "git repo present"; else fail "missing clone at $REPO"; fi
if [[ -x "$REPO/scripts/sync-to-local-obsidian.sh" ]]; then
  pass "sync script executable"
elif [[ -f "$REPO/scripts/sync-to-local-obsidian.sh" ]]; then
  warn "sync script exists but not executable (chmod +x needed)"
else
  fail "sync script missing — run: cd \"$REPO\" && git pull"
fi

# 2) .env secrets (do not print values)
ENV_FILE="${THINKING_ENV_FILE:-$REPO/.env}"
for field in NOTION_TOKEN NOTION_THINKING_DATABASE_ID; do
  if [[ -n "${!field:-}" ]] || { [[ -f "$ENV_FILE" ]] && grep -Eq "^${field}=.+" "$ENV_FILE"; }; then
    pass "$field configured"
  else
    fail "$field missing from process environment and .env"
  fi
done

# 3) vault path
if [[ -z "$VAULT" && -f "$PLIST" ]]; then
  VAULT="$(/usr/libexec/PlistBuddy -c 'Print :EnvironmentVariables:OBSIDIAN_VAULT' "$PLIST" 2>/dev/null || true)"
fi
if [[ -d "$VAULT" ]]; then
  pass "Obsidian vault directory exists"
  if [[ -d "$VAULT/Thinking" ]]; then
    count="$(find "$VAULT/Thinking" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
    pass "Thinking/ has ${count} markdown files"
  else
    warn "Thinking/ folder not created yet (run sync once)"
  fi
else
  fail "set OBSIDIAN_VAULT to an existing vault, or configure it in the LaunchAgent plist"
fi

# 4) LaunchAgent
if [[ -f "$PLIST" ]]; then
  pass "LaunchAgent plist installed"
  if grep -q 'OBSIDIAN_VAULT' "$PLIST"; then
    echo "     plist OBSIDIAN_VAULT=$(/usr/libexec/PlistBuddy -c 'Print :EnvironmentVariables:OBSIDIAN_VAULT' "$PLIST" 2>/dev/null || echo '?')"
  fi
  if grep -q 'StartInterval' "$PLIST"; then
    echo "     StartInterval=$(/usr/libexec/PlistBuddy -c 'Print :StartInterval' "$PLIST" 2>/dev/null || echo '?') seconds"
  fi
else
  fail "LaunchAgent plist missing at $PLIST"
fi

if launchctl print "gui/${UID_NUM}/${LABEL}" >/dev/null 2>&1; then
  pass "LaunchAgent loaded (gui/${UID_NUM}/${LABEL})"
  launchctl print "gui/${UID_NUM}/${LABEL}" 2>/dev/null | grep -E 'state =|runs =|last exit code =|path =' | sed 's/^/     /'
else
  fail "LaunchAgent not loaded — bootstrap the plist"
fi

# 5) recent log
if [[ -f "$LOG" ]]; then
  pass "log file exists: $LOG"
  if grep -q 'OK: Notion synced' "$LOG" 2>/dev/null; then
    pass "log contains a successful Notion sync"
  else
    warn "no 'OK: Notion synced' yet — run sync once or check errors above"
  fi
  if grep -qiE 'ERROR|Traceback' "$LOG" 2>/dev/null; then
    warn "log contains errors (inspect locally)"
  fi
else
  warn "no log yet at $LOG (LaunchAgent may not have run)"
fi

# 6) proxy hint
if git config --global --get http.proxy >/dev/null 2>&1 || git config --global --get https.proxy >/dev/null 2>&1; then
  warn "git global proxy is set (verify availability for unattended jobs)"
fi

echo
echo "=== summary: ok=$ok warn=$warn fail=$bad ==="
if [[ "$bad" -gt 0 ]]; then
  echo "Next: fix FAIL items, then:"
  echo "  $REPO/scripts/sync-to-local-obsidian.sh"
  echo "  launchctl kickstart -k gui/${UID_NUM}/${LABEL}"
  exit 1
fi
exit 0
