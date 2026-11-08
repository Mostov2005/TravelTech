trip_service/
│
├── app/
│   ├── api.py              # FastAPI endpoints
│   ├── schemas.py          # Pydantic-схемы запросов и ответов
│   ├── models.py           # Модели SQLAlchemy
│   ├── domain.py           # Бизнес-логика и правила
│   ├── services.py         # Сценарии использования
│   ├── repositories.py     # Работа с PostgreSQL
│   ├── messaging.py        # RabbitMQ
│   ├── cache.py            # Redis
│   ├── database.py         # Подключение к БД
│   └── main.py             # Запуск приложения
│
├── tests/
│   ├── test_unit.py
│   └── test_integration.py
│
├── Dockerfile
├── requirements.txt
└── .env.example