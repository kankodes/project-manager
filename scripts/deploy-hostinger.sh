#!/usr/bin/env bash
# Deploys the static site to Hostinger via FTP/FTPS using lftp mirror.
#
# Required env vars:
#   HOSTINGER_FTP_HOST  - e.g. ftp.garnetevents.in
#   HOSTINGER_FTP_USER  - FTP username
#   HOSTINGER_FTP_PASS  - FTP password
# Optional env vars:
#   HOSTINGER_FTP_PORT  - defaults to 21
#   HOSTINGER_FTP_DIR   - remote target dir, defaults to public_html
#
# Usage: scripts/deploy-hostinger.sh

set -euo pipefail

: "${HOSTINGER_FTP_HOST:?HOSTINGER_FTP_HOST is not set}"
: "${HOSTINGER_FTP_USER:?HOSTINGER_FTP_USER is not set}"
: "${HOSTINGER_FTP_PASS:?HOSTINGER_FTP_PASS is not set}"

PORT="${HOSTINGER_FTP_PORT:-21}"
REMOTE_DIR="${HOSTINGER_FTP_DIR:-public_html}"
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
  --exclude-glob "*.md" \
  "$LOCAL_DIR" "$REMOTE_DIR"
bye
EOF

echo "Deploy complete."
