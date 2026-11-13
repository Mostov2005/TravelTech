$ErrorActionPreference = "Stop"

# TravelTech: демонстрационный сценарий REST API.
# Перед запуском: docker compose up -d
# Запуск из корня проекта: .\scripts\demo.ps1

$services = @{
    Identity   = "http://localhost:8004"
    Trip       = "http://localhost:8000"
    Flight     = "http://localhost:8002"
    Monitoring = "http://localhost:8003"
    Recovery   = "http://localhost:8001"
}

function Invoke-Api {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Path,
        [object]$Body = $null,
        [switch]$Authorized
    )

    $headers = @{}
    if ($Authorized) {
        if (-not $script:AccessToken) {
            throw "Нет access token. Сначала выполните вход."
        }
        $headers["Authorization"] = "Bearer $script:AccessToken"
    }

    $params = @{
        Uri         = "$($services[$Name])$Path"
        Method      = $Method
        Headers     = $headers
        ErrorAction = "Stop"
    }

    if ($null -ne $Body) {
        $params["ContentType"] = "application/json"
        $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
    }

    Write-Host "`n[$Method] $Name$Path" -ForegroundColor Cyan
    $result = Invoke-RestMethod @params
    $result | ConvertTo-Json -Depth 10 | Write-Host
    return $result
}

function New-AirportCode {
    $letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "X" + $letters[(Get-Random -Minimum 0 -Maximum 26)] + $letters[(Get-Random -Minimum 0 -Maximum 26)]
}

Write-Host "=== TravelTech demo ===" -ForegroundColor Green
Write-Host "Каждый запуск создаёт новые данные; существующие записи не удаляются."

# 1. Identity: регистрация и получение JWT.
$suffix = [Guid]::NewGuid().ToString("N").Substring(0, 10)
$email = "demo_$suffix@example.com"
$username = "demo_$suffix"
$password = "DemoPass_$suffix"

Invoke-Api -Name Identity -Method POST -Path "/auth/register" -Body @{
    email    = $email
    username = $username
    password = $password
} | Out-Null

$login = Invoke-Api -Name Identity -Method POST -Path "/auth/login" -Body @{
    email    = $email
    password = $password
}

$script:AccessToken = $login.access_token
if (-not $script:AccessToken) {
    throw "В ответе /auth/login не найден access_token. Проверьте формат ответа Identity Service."
}

Invoke-Api -Name Identity -Method GET -Path "/auth/me" -Authorized | Out-Null

# 2. Flight Service: два аэропорта и два рейса.
$departureCode = New-AirportCode
$arrivalCode = New-AirportCode
while ($arrivalCode -eq $departureCode) {
    $arrivalCode = New-AirportCode
}

$departureAirport = Invoke-Api -Name Flight -Method POST -Path "/flights/airports" -Authorized -Body @{
    iata_code = $departureCode
    name      = "Demo Departure Airport $suffix"
    city      = "Demo City A"
    country   = "Demo Country"
}

$arrivalAirport = Invoke-Api -Name Flight -Method POST -Path "/flights/airports" -Authorized -Body @{
    iata_code = $arrivalCode
    name      = "Demo Arrival Airport $suffix"
    city      = "Demo City B"
    country   = "Demo Country"
}

$departureTime = (Get-Date).AddDays(3)
$arrivalTime = $departureTime.AddHours(2)
$alternativeDepartureTime = $departureTime.AddHours(4)
$alternativeArrivalTime = $alternativeDepartureTime.AddHours(2)

$flight = Invoke-Api -Name Flight -Method POST -Path "/flights/" -Authorized -Body @{
    flight_number       = "D$suffix"
    airline             = "TravelTech Demo Airline"
    departure_airport_id = $departureAirport.id
    arrival_airport_id   = $arrivalAirport.id
    departure_time      = $departureTime.ToString("yyyy-MM-ddTHH:mm:ss")
    arrival_time        = $arrivalTime.ToString("yyyy-MM-ddTHH:mm:ss")
}

$alternativeFlight = Invoke-Api -Name Flight -Method POST -Path "/flights/" -Authorized -Body @{
    flight_number       = "A$suffix"
    airline             = "TravelTech Demo Airline"
    departure_airport_id = $departureAirport.id
    arrival_airport_id   = $arrivalAirport.id
    departure_time      = $alternativeDepartureTime.ToString("yyyy-MM-ddTHH:mm:ss")
    arrival_time        = $alternativeArrivalTime.ToString("yyyy-MM-ddTHH:mm:ss")
}

# 3. Trip Service: поездка, сегмент и бронирование.
$tripStart = (Get-Date).Date.AddDays(3)
$tripEnd = $tripStart.AddDays(2)

$trip = Invoke-Api -Name Trip -Method POST -Path "/trips/" -Authorized -Body @{
    name       = "Demo trip $suffix"
    start_date = $tripStart.ToString("yyyy-MM-dd")
    end_date   = $tripEnd.ToString("yyyy-MM-dd")
}

$tripId = $trip.id
if (-not $tripId) {
    throw "В ответе Trip Service не найден id поездки."
}

Invoke-Api -Name Trip -Method POST -Path "/trips/$tripId/segments" -Authorized -Body @{
    flight_id       = $flight.id
    departure_airport = $departureCode
    arrival_airport   = $arrivalCode
    departure_time  = $departureTime.ToString("yyyy-MM-ddTHH:mm:ss")
    arrival_time    = $arrivalTime.ToString("yyyy-MM-ddTHH:mm:ss")
    position        = 1
} | Out-Null

$bookingReference = "BK$suffix"
Invoke-Api -Name Trip -Method POST -Path "/trips/$tripId/bookings" -Authorized -Body @{
    flight_id        = $flight.id
    booking_reference = $bookingReference
    ticket_number    = "TK$suffix"
} | Out-Null

# Повторное чтение поездки позволяет показать работу Redis cache.
Invoke-Api -Name Trip -Method GET -Path "/trips/$tripId" -Authorized | Out-Null
Invoke-Api -Name Trip -Method GET -Path "/trips/$tripId" -Authorized | Out-Null

# 4. Flight Monitoring: создание мониторинга (проверка Flight Service по gRPC).
$monitoring = Invoke-Api -Name Monitoring -Method POST -Path "/monitoring/" -Authorized -Body @{
    flight_id = $flight.id
    status    = "scheduled"
}

if ($monitoring.id) {
    Invoke-Api -Name Monitoring -Method POST -Path "/monitoring/$($monitoring.id)/status" -Authorized -Body @{
        status      = "delayed"
        description = "Демонстрационное изменение статуса рейса"
    } | Out-Null

    Invoke-Api -Name Monitoring -Method GET -Path "/monitoring/$($monitoring.id)/history" -Authorized | Out-Null
}

# 5. Recovery: кейс нарушения, предложение и Saga-перебронирование.
$case = Invoke-Api -Name Recovery -Method POST -Path "/recovery/cases" -Authorized -Body @{
    trip_id         = $tripId
    flight_id       = $flight.id
    disruption_type = "delay"
    description     = "Демонстрационный случай задержки рейса"
}

$caseId = $case.id
if (-not $caseId) {
    throw "В ответе Recovery Service не найден id кейса."
}

Invoke-Api -Name Recovery -Method POST -Path "/recovery/cases/$caseId/proposals" -Authorized -Body @{
    alternative_flight_id = $alternativeFlight.id
    description           = "Демонстрационное альтернативное предложение"
} | Out-Null

Invoke-Api -Name Recovery -Method POST -Path "/recovery/cases/$caseId/rebooking" -Authorized -Body @{
    alternative_flight_id = $alternativeFlight.id
    booking_reference     = "RB$suffix"
    ticket_number         = "RT$suffix"
    description           = "Демонстрационное перебронирование через Saga"
} | Out-Null

Write-Host "`n=== DEMO COMPLETED ===" -ForegroundColor Green
Write-Host "Email: $email"
Write-Host "Trip ID: $tripId"
Write-Host "Flight ID: $($flight.id)"
Write-Host "Alternative flight ID: $($alternativeFlight.id)"
Write-Host "Recovery case ID: $caseId"
Write-Host "Данные намеренно не удаляются. При следующем запуске будут созданы новые уникальные записи."
