from sqlalchemy import text

from database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("Подключение успешно!")
        print(result.scalar())

except Exception as e:
    print("Ошибка подключения:", e)
