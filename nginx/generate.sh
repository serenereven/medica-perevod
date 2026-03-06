#!/bin/sh
set -e

CERT="/etc/letsencrypt/live/${LETSENCRYPT_DOMAIN}/fullchain.pem"
KEY="/etc/letsencrypt/live/${LETSENCRYPT_DOMAIN}/privkey.pem"

if [ -f "$CERT" ] && [ -f "$KEY" ]; then
  echo "nginx: using HTTPS config"
  envsubst '$$NGINX_SERVER_NAME $$LETSENCRYPT_DOMAIN' \
    < /etc/nginx/templates/https.conf.template \
    > /etc/nginx/conf.d/app.conf
else
  echo "nginx: using HTTP config (no cert yet)"
  envsubst '$$NGINX_SERVER_NAME' \
    < /etc/nginx/templates/http.conf.template \
    > /etc/nginx/conf.d/app.conf
fi
