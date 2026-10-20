#!/usr/bin/env bash
# Deploys the static site to Hostinger via FTP/FTPS using lftp mirror.
#
# Settings (env vars override the defaults):
#   HOSTINGER_FTP_HOST  - defaults to 31.170.167.153 (hPanel > Files > FTP Accounts)
#   HOSTINGER_FTP_USER  - defaults to u667258270.garnetevents.in
#   HOSTINGER_FTP_PASS  - read from the macOS Keychain when not set. Store it once:
#                         security add-generic-password -s garnet-ftp -a u667258270.garnetevents.in -w
#                         (prompts for the password; run again with -U to update it)
#   HOSTINGER_FTP_PORT  - defaults to 21
#   HOSTINGER_FTP_DIR   - remote target dir, defaults to . (the site's FTP account
#                         already opens inside public_html; "public_html" here
#                         would nest the site one folder too deep)
#
# Usage: scripts/deploy-hostinger.sh

set -euo pipefail

HOSTINGER_FTP_HOST="${HOSTINGER_FTP_HOST:-31.170.167.153}"
HOSTINGER_FTP_USER="${HOSTINGER_FTP_USER:-u667258270.garnetevents.in}"
if [ -z "${HOSTINGER_FTP_PASS:-}" ]; then
  HOSTINGER_FTP_PASS="$(security find-generic-password -s garnet-ftp -a "$HOSTINGER_FTP_USER" -w 2>/dev/null)" || {
    echo "No FTP password in the Keychain. Store it once with:" >&2
    echo "  security add-generic-password -s garnet-ftp -a $HOSTINGER_FTP_USER -w" >&2
    exit 1
  }
fi

PORT="${HOSTINGER_FTP_PORT:-21}"
REMOTE_DIR="${HOSTINGER_FTP_DIR:-.}"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Deploying $LOCAL_DIR -> $HOSTINGER_FTP_USER@$HOSTINGER_FTP_HOST:$PORT/$REMOTE_DIR"

lftp -u "$HOSTINGER_FTP_USER,$HOSTINGER_FTP_PASS" "$HOSTINGER_FTP_HOST" -p "$PORT" <<EOF
set ssl:verify-certificate no
set ftp:ssl-allow yes
set ftp:ssl-force no
set mirror:use-pget-n 1
mkdir -p "$REMOTE_DIR"
mirror --reverse --delete --verbose \
  --exclude-glob ".git/" \
  --exclude-glob "scripts/" \
  --exclude-glob "tools/" \
  --exclude-glob ".claude/" \
  --exclude-glob ".gitignore" \
  --exclude-glob "*.md" \
  "$LOCAL_DIR" "$REMOTE_DIR"
bye
EOF

echo "Deploy complete."
