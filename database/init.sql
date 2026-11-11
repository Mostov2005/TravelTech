SELECT 'CREATE DATABASE recovery_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'recovery_db'
) \gexec

SELECT 'CREATE DATABASE flight_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'flight_db'
) \gexec

SELECT 'CREATE DATABASE monitoring_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'monitoring_db'
) \gexec

SELECT 'CREATE DATABASE identity_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'identity_db'
) \gexec
