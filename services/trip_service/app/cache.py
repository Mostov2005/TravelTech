import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

try:
    redis_client.ping()
    print("Подключение к Redis успешно!")
except redis.ConnectionError:
    print("Не удалось подключиться к Redis")