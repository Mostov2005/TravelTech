
import secrets
import string
import uuid
from datetime import datetime, timedelta

import requests


SERVICES = {
    "Identity": "http://localhost:8004",
    "Trip": "http://localhost:8000",
    "Flight": "http://localhost:8002",
    "Monitoring": "http://localhost:8003",
    "Recovery": "http://localhost:8001",
}

ACCESS_TOKEN = None


def invoke_api(name, method, path, description, body=None, authorized=False):
    headers = {}

    if authorized:
        if not ACCESS_TOKEN:
            raise RuntimeError("Нет access token. Сначала выполните вход.")
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    url = SERVICES[name] + path

    print(f"\n{description}")
    print(f"[{method}] {name}{path}")

    try:
        response = requests.request(
            method, url, json=body, headers=headers, timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as error:
        if error.response is not None:
            print("Ответ сервера:", error.response.text)
        raise RuntimeError(f"Ошибка запроса {method} {url}: {error}") from error

    if not response.content:
        return None

    result = response.json()
    print(result)
    return result


def new_airport_code():
    return "".join(
        secrets.choice(string.ascii_uppercase) for _ in range(3)
    )


def main():
    global ACCESS_TOKEN

    print("TravelTech demo")
    print("Каждый запуск создаёт новые данные; существующие записи не удаляются.")

    suffix = uuid.uuid4().hex[:10]
    email = f"demo_{suffix}@example.com"
    username = f"demo_{suffix}"
    password = f"DemoPass_{suffix}"

    # 1. Identity Service: регистрация и авторизация.
    invoke_api(
        "Identity", "POST", "/auth/register",
        "1. Регистрация нового пользователя",
        body={
            "email": email,
            "username": username,
            "password": password,
        }
    )

    login = invoke_api(
        "Identity", "POST", "/auth/login",
        "2. Авторизация пользователя и получение JWT-токена",
        body={
            "email": email,
            "password": password,
        }
    )

    ACCESS_TOKEN = login.get("access_token")

    if not ACCESS_TOKEN:
        raise RuntimeError("В ответе /auth/login не найден access_token.")

    invoke_api(
        "Identity", "GET", "/auth/me",
        "3. Получение данных авторизованного пользователя",
        authorized=True
    )

    # 2. Flight Service: создание аэропортов и рейсов.
    departure_code = new_airport_code()
    arrival_code = new_airport_code()

    while arrival_code == departure_code:
        arrival_code = new_airport_code()

    departure_airport = invoke_api(
        "Flight", "POST", "/flights/airports",
        "4. Создание аэропорта отправления",
        authorized=True,
        body={
            "iata_code": departure_code,
            "name": f"Demo Departure Airport {suffix}",
            "city": "Demo City A",
            "country": "Demo Country",
        }
    )

    arrival_airport = invoke_api(
        "Flight", "POST", "/flights/airports",
        "5. Создание аэропорта прибытия",
        authorized=True,
        body={
            "iata_code": arrival_code,
            "name": f"Demo Arrival Airport {suffix}",
            "city": "Demo City B",
            "country": "Demo Country",
        }
    )

    departure_time = datetime.now() + timedelta(days=3)
    arrival_time = departure_time + timedelta(hours=2)
    alternative_departure_time = departure_time + timedelta(hours=4)
    alternative_arrival_time = alternative_departure_time + timedelta(hours=2)

    flight = invoke_api(
        "Flight", "POST", "/flights/",
        "6. Создание основного рейса между аэропортами",
        authorized=True,
        body={
            "flight_number": f"D{suffix}",
            "airline": "TravelTech Demo Airline",
            "departure_airport_id": departure_airport["id"],
            "arrival_airport_id": arrival_airport["id"],
            "departure_time": departure_time.isoformat(timespec="seconds"),
            "arrival_time": arrival_time.isoformat(timespec="seconds"),
        }
    )

    alternative_flight = invoke_api(
        "Flight", "POST", "/flights/",
        "7. Создание альтернативного рейса для перебронирования",
        authorized=True,
        body={
            "flight_number": f"A{suffix}",
            "airline": "TravelTech Demo Airline",
            "departure_airport_id": departure_airport["id"],
            "arrival_airport_id": arrival_airport["id"],
            "departure_time": alternative_departure_time.isoformat(timespec="seconds"),
            "arrival_time": alternative_arrival_time.isoformat(timespec="seconds"),
        }
    )

    # 3. Trip Service: создание поездки, маршрута и бронирования.
    trip_start = (datetime.now() + timedelta(days=3)).date()
    trip_end = trip_start + timedelta(days=2)

    trip = invoke_api(
        "Trip", "POST", "/trips/",
        "8. Создание новой поездки",
        authorized=True,
        body={
            "name": f"Demo trip {suffix}",
            "start_date": trip_start.isoformat(),
            "end_date": trip_end.isoformat(),
        }
    )

    trip_id = trip.get("id")

    if not trip_id:
        raise RuntimeError("В ответе Trip Service не найден id поездки.")

    invoke_api(
        "Trip", "POST", f"/trips/{trip_id}/segments",
        "9. Добавление основного рейса в маршрут поездки",
        authorized=True,
        body={
            "flight_id": flight["id"],
            "departure_airport": departure_code,
            "arrival_airport": arrival_code,
            "departure_time": departure_time.isoformat(timespec="seconds"),
            "arrival_time": arrival_time.isoformat(timespec="seconds"),
            "position": 1,
        }
    )

    invoke_api(
        "Trip", "POST", f"/trips/{trip_id}/bookings",
        "10. Создание бронирования билета",
        authorized=True,
        body={
            "flight_id": flight["id"],
            "booking_reference": f"BK{suffix}",
            "ticket_number": f"TK{suffix}",
        }
    )

    invoke_api(
        "Trip", "GET", f"/trips/{trip_id}",
        "11. Первое получение данных поездки",
        authorized=True
    )

    invoke_api(
        "Trip", "GET", f"/trips/{trip_id}",
        "12. Повторное получение данных поездки для проверки Redis cache",
        authorized=True
    )

    # 4. Flight Monitoring Service: мониторинг рейса.
    monitoring = invoke_api(
        "Monitoring", "POST", "/monitoring/",
        "13. Создание мониторинга основного рейса",
        authorized=True,
        body={
            "flight_id": flight["id"],
            "status": "scheduled",
        }
    )

    monitoring_id = monitoring.get("id")

    if monitoring_id:
        invoke_api(
            "Monitoring", "POST", f"/monitoring/{monitoring_id}/status",
            "14. Изменение статуса рейса на delayed",
            authorized=True,
            body={
                "status": "delayed",
                "description": "Демонстрационное изменение статуса рейса",
            }
        )

        invoke_api(
            "Monitoring", "GET", f"/monitoring/{monitoring_id}/history",
            "15. Получение истории изменения статусов рейса",
            authorized=True
        )

    # 5. Recovery Service: обработка нарушения и Saga-перебронирование.
    case = invoke_api(
        "Recovery", "POST", "/recovery/cases",
        "16. Создание кейса нарушения из-за задержки рейса",
        authorized=True,
        body={
            "trip_id": trip_id,
            "flight_id": flight["id"],
            "disruption_type": "delay",
            "description": "Демонстрационный случай задержки рейса",
        }
    )

    case_id = case.get("id")

    if not case_id:
        raise RuntimeError("В ответе Recovery Service не найден id кейса.")

    invoke_api(
        "Recovery", "POST", f"/recovery/cases/{case_id}/proposals",
        "17. Создание предложения с альтернативным рейсом",
        authorized=True,
        body={
            "alternative_flight_id": alternative_flight["id"],
            "description": "Демонстрационное альтернативное предложение",
        }
    )

    invoke_api(
        "Recovery", "POST", f"/recovery/cases/{case_id}/rebooking",
        "18. Запуск Saga для перебронирования на альтернативный рейс",
        authorized=True,
        body={
            "alternative_flight_id": alternative_flight["id"],
            "booking_reference": f"RB{suffix}",
            "ticket_number": f"RT{suffix}",
            "description": "Демонстрационное перебронирование через Saga",
        }
    )

    print("\nDEMO COMPLETED")
    print(f"Email: {email}")
    print(f"Trip ID: {trip_id}")
    print(f"Flight ID: {flight['id']}")
    print(f"Alternative flight ID: {alternative_flight['id']}")
    print(f"Recovery case ID: {case_id}")
    print("Данные не удаляются; при следующем запуске будут созданы новые записи.")


if __name__ == "__main__":
    main()
