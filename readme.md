# medica

## Первый запуск

### Сборка из шаблона

1) Скачать шаблон
```bash
mkdir -p /tmp/tpl && cd /tmp/tpl
git archive --remote=git@github.com:serenereven/django_tpl.git HEAD django_tpl | tar -x
```

2) Команда генерации нового проекта
```bash
django-admin startproject myproj \
  --template /tmp/tpl/django_tpl \
  --extension py,yml,txt,md,env,sh,conf,template
```

3) Копирование .env.example в .env
```bash
cp .env.example .env
docker compose up --build -d
```
---

### Issue cert (пример)

1) Первый запуск: сертификата нет → nginx поднимается на HTTP, challenge работает.
2) Выпустить сертификат:
```bash
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d example.com -d www.example.com \
  --email you@example.com --agree-tos --no-eff-email
```
3) Перезапустить nginx:
```bash
docker compose restart nginx
```
---