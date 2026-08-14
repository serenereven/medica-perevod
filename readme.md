# Medica-Perevod

Backend-приложение для управления медицинскими документами. REST API на Django REST Framework с разграничением доступа: публичный просмотр, авторизованное скачивание.

## Стек

Python 3.12 · Django 5.2 · DRF 3.16 · PostgreSQL 16 · django-allauth · Docker · Nginx · Gunicorn · Certbot · pytest · GitHub Actions

## Архитектура

```
config/       Конфигурация Django, корневые URL
common/       Абстрактные модели: SoftDelete, TimeStamped, Publishable, UUID PK
core/         Документы: модели, DRF ViewSet, сериализаторы, SQL-функции
users/        Кастомная модель пользователя (email как USERNAME_FIELD)
```

## Ключевые решения

**Модели**
- Абстрактные базовые классы для переиспользования: `TimeStampedModel`, `PublishableModel`
- Кастомный `UserManager` с авторизацией по email вместо username

**Оптимизация ORM**
- `select_related` для ForeignKey, `only()` для ограничения выборки
- Натуральная сортировка через SQL-функции PostgreSQL
- Пагинация на уровне БД через LIMIT/OFFSET, без выгрузки в память Python


**API**
- `DocumentViewSet` (ReadOnlyModelViewSet) с кастомным `@action` для скачивания
- Атомарное обновление счётчика скачиваний через `F()` выражения
- Проверка прав доступа на уровне action: просмотр публичный, скачивание требует авторизации

**Инфраструктура**
- Docker Compose: PostgreSQL, Gunicorn, Nginx, Certbot
- Nginx раздаёт статику и медиа, проксирует запросы к Gunicorn
- Автоматическое получение SSL-сертификатов через Let's Encrypt
- Утилитный скрипт синхронизации документов с файловой блокировкой (lock file)

## API

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/api/documents/` | Список с пагинацией и фильтрами | Публичный |
| GET | `/api/documents/{id}/` | Детали документа | Публичный |
| GET | `/api/documents/{id}/download/` | Скачивание файла | Авторизованный |
| GET | `/api/documents/meta/` | Категории и типы для фильтров | Публичный |

Фильтрация: `?category={id}&type={value}&q={search}`

## Тестирование и CI

- pytest с фикстурами и фабриками для генерации тестовых данных
- Покрытие критической бизнес-логики: модели, API, права доступа
- GitHub Actions: линтинг (Ruff), проверка форматирования, запуск тестов
- Тестовое окружение изолировано: SQLite в памяти, отключённые миграции
