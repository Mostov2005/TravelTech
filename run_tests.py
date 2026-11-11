import subprocess
import sys

services = [
    "trip_service",
    "flight_service",
    "flight_monitoring_service",
    "recovery_service",
    "identity_service"
]

for service in services:
    print(f"\n{'=' * 60}")
    print(f"Тестирование: {service}")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            f"services/{service}/tests/",
            "-v"
        ]
    )

    if result.returncode != 0:
        print(f"\nОшибка в {service}")
        sys.exit(result.returncode)

print("\nВсе тесты успешно пройдены!")
