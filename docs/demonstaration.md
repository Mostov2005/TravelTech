# Демонстрация проекта TravelTech

Документ содержит последовательность показа проекта по требованиям практической работы. 

## 1. Подготовка

Открыть PowerShell в корне проекта `C:\TravelTech`.

Запустить все контейнеры:

```powershell
docker compose up -d
docker compose ps
```

Убедиться, что сервисы запущены. Swagger:

| Сервис | Swagger |
|---|---|
| Trip Service | http://localhost:8000/docs |
| Recovery Service | http://localhost:8001/docs |
| Flight Service | http://localhost:8002/docs |
| Flight Monitoring Service | http://localhost:8003/docs |
| Identity Service | http://localhost:8004/docs |

Дополнительные интерфейсы:
- RabbitMQ Management: http://localhost:15672
    - Логин: guest
    - Пароль: guest
- Redis доступен на `localhost:6379`.
- PostgreSQL доступен на `localhost:5433`.

## 2. Автоматический сценарий

Сценарий создаёт пользователя, два аэропорта, два рейса, поездку, сегмент маршрута, бронирование, мониторинг рейса, кейс нарушения и выполняет Saga-перебронирование.

Запуск из корня проекта:

```powershell
python .\scripts\demo.py
```

Сценарий использует уникальные значения при каждом запуске. Он не удаляет данные после выполнения. Это сделано намеренно: у части сервисов нет API удаления аэропортов, рейсов, пользователей и кейсов.

## 3. Демонстрация 13 требований

### 1. Предметная область

`docs/01_domain_description.md`.

TravelTech — система управления путешествиями, маршрутами, бронированиями, информацией о рейсах, мониторингом и восстановлением поездки при нарушениях.

### 2. DDD и ограниченные контексты

`docs/03_ddd_design.md`.

В проекте выделено пять bounded contexts:
- Identity;
- Trip Management;
- Flight Information;
- Flight Monitoring;
- Travel Recovery.

Каждый контекст реализован отдельным сервисом.

### 3. Микросервисы, REST API и Clean Architecture

Посмотреть структуру `services/` и Swagger каждого сервиса.

В каждом сервисе API отделён от бизнес-логики и доступа к данным. REST используется для внешних и межсервисных HTTP-вызовов.

| Файл | Назначение |
|---|---|
| `main.py` | Точка входа: создание и настройка приложения FastAPI. |
| `api.py` | REST API: обработка HTTP-запросов и вызов сервисов. |
| `services.py` | Бизнес-логика и выполнение операций. |
| `repositories.py` | Работа с данными в базе: CRUD-операции. |
| `models.py` | Описание таблиц базы данных через SQLAlchemy. |
| `schemas.py` | Проверка входных данных и формирование ответов API через Pydantic. |
| `database.py` | Подключение к PostgreSQL и управление сессиями. |
| `domain.py` | Описание предметной области и бизнес-правил. |
| `security.py` | Хеширование паролей и работа с JWT. |
| `cache.py` | Кэширование данных в Redis. |
| `messaging.py` | Обмен сообщениями через RabbitMQ. |
| `__init__.py` | Обозначение директории как Python-пакета. |

Не все файлы присутствуют в каждом микросервисе — дополнительные модули используются там, где это необходимо.

REST API используется для взаимодействия между сервисами и внешними клиентами.


### 4. Docker и Docker Compose

Посмотреть `docker-compose.yml` и результат:

```powershell
docker compose ps
```

В Compose запускаются пять сервисов приложения, PostgreSQL, Redis и RabbitMQ.

### 5. Redis

В Swagger Trip Service дважды выполнить `GET /trips/{trip_id}` для поездки, созданной демонстрационным сценарием.

Первый запрос получает поездку из PostgreSQL и помещает её в Redis. Повторный запрос использует кэш. В реализации ключ имеет вид `trip:{trip_id}`, время жизни — 300 секунд.

При необходимости посмотреть состояние Redis:

```powershell
docker compose exec redis redis-cli PING
docker compose exec redis redis-cli KEYS "trip:*"
```

### 6. PostgreSQL

Посмотреть контейнер PostgreSQL:

```powershell
docker compose exec postgres pg_isready
```

В проекте используются отдельные базы данных для сервисов: `identity_db`, `trip_db`, `flight_db`, `monitoring_db`, `recovery_db`. Сервисы владеют своими данными; межсервисные связи по UUID не оформлены внешними ключами между базами.

### 7. Распределённая транзакция — Saga

В Swagger Recovery Service:
- `POST /recovery/cases`;
- `POST /recovery/cases/{case_id}/rebooking`.

1. Recovery Service — создан кейс задержки рейса.
2. Recovery Service — создано предложение альтернативного рейса.
3. Saga — Recovery Service запросил у Trip Service новое бронирование.
4. Trip Service — создано бронирование на альтернативный рейс.
5. Recovery Service — сохранён результат, операция завершилась успешно (completed).

В автоматическом сценарии этот процесс выполняется последним этапом.

### 8. Transactional Outbox

При создании поездки Trip Service сохраняет запись о поездке и событие `trip.created` в таблице Outbox в рамках одной транзакции PostgreSQL.

Для демонстрации можно открыть базу `trip_db` в DBeaver и выполнить:

```sql
SELECT id, event_type, payload, created_at, processed_at
FROM outbox_events
ORDER BY created_at DESC
LIMIT 10;
```

**Важное ограничение текущей версии:** фоновый worker публикации Outbox в RabbitMQ не запускается автоматически из `main.py`: поток создан без `target=run_outbox_worker`. Поэтому в этой демонстрации показывается атомарная запись события в Outbox, но не автоматическая доставка этого события в RabbitMQ. Код проекта для демонстрации не изменяется.

### 9. RabbitMQ

Посмотреть RabbitMQ Management: http://localhost:15672.

Стандартные учётные данные, заданные в `docker-compose.yml`, используются для входа. В проекте настроена очередь `trip_events`, а модуль Trip Service содержит публикацию сообщений с persistent delivery mode и consumer с подтверждением `ack`.

Из-за ограничения, указанного в пункте 8, автоматическая публикация Outbox-событий при демонстрационном запуске не выполняется.

### 10. gRPC
Посмотреть код взаимодействия Flight Monitoring Service с Flight Service через gRPC.

При создании мониторинга Flight Monitoring Service проверяет существование рейса через gRPC-метод `GetFlight`. В демонстрационном сценарии это происходит при запросе `POST /monitoring/`.

При создании мониторинга (POST /monitoring/) происходит следующее:
1. Flight Monitoring Service получает ID рейса.
2. Через gRPC вызывает метод GetFlight сервиса Flight Service.
3. Flight Service проверяет наличие рейса и возвращает его данные.
4. Если рейс существует, Flight Monitoring Service создаёт запись мониторинга.

Flight Service предоставляет gRPC на порту `50051`.

### 11. Централизованная авторизация и JWT

В Swagger Identity Service посмотреть:
- `POST /auth/register`;
- `POST /auth/login`;
- `POST /auth/refresh`;
- `GET /auth/me`.

После входа сервис выдаёт JWT. Для защищённых endpoint других сервисов используется `Authorization: Bearer <access_token>`. Автоматический сценарий регистрирует отдельного пользователя и использует его access token для запросов.

### 12. Unit- и integration-тесты

Из корня проекта выполнить:

```powershell
pytest services/ -v
```

Ожидаемый результат последнего проверенного запуска: 55 тестов — 52 unit-теста и 3 integration-теста.

Для просмотра состава тестов:

```powershell
pytest services/ --collect-only -q
```

### 13. CI pipeline

Посмотреть `.github/workflows/tests.yml` в GitHub и последний успешный запуск GitHub Actions.

Pipeline автоматически устанавливает зависимости и запускает тесты при push и pull request в репозиторий.

## 4. Документы проекта

| Файл | Содержание |
|---|---|
| `README.md` | Обзор проекта, запуск и структура |
| `docs/01_domain_description.md` | Предметная область |
| `docs/02_business_processes.md` | Бизнес-процессы |
| `docs/03_ddd_design.md` | DDD и bounded contexts |
| `docs/04_architecture.md` | Архитектура и взаимодействие сервисов |
| `docs/05_database_design.md` | Базы данных и сущности |
| `docs/TESTING.md` | Запуск и описание тестов |