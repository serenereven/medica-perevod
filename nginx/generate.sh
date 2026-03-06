#!/bin/sh
set -e

CERT="/etc/letsencrypt/live/${LETSENCRYPT_DOMAIN}/fullchain.pem"
KEY="/etc/letsencrypt/live/${LETSENCRYPT_DOMAIN}/privkey.pem"

rm -f /etc/nginx/conf.d/*.conf

if [ -f "$CERT" ] && [ -f "$KEY" ]; then
  echo "nginx: using HTTPS config"
  envsubst '$NGINX_SERVER_NAME $LETSENCRYPT_DOMAIN' \
    < /opt/nginx-templates/https.conf.template \
    > /etc/nginx/conf.d/app.conf
else
  echo "nginx: using HTTP config (no cert yet)"
  envsubst '$NGINX_SERVER_NAME' \
    < /opt/nginx-templates/http.conf.template \
    > /etc/nginx/conf.d/app.conf
fi