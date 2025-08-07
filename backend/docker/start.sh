#!/bin/bash

echo "========================================"
echo "🎵Music Player Backend Starting..."
echo "🎵========================================"

echo ""
echo "📦 Installing Python dependencies..."
poetry install --no-dev --no-interaction --no-ansi

echo ""
echo "Waiting for PostgreSQL database to be ready..."
until poetry run python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_SERVER'),
        port=os.getenv('POSTGRES_PORT')
    )
    conn.close()
    print('Database is ready!')
except:
    print('Database not ready yet...')
    exit(1)
"
do
    echo "Database not ready yet, waiting..."
    sleep 2
done

echo ""
echo "Running Alembic database migrations..."
poetry run alembic upgrade head

echo ""
echo "Database migrations completed successfully!"

echo ""
echo "Starting FastAPI server with uvicorn..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"

echo ""
echo "========================================"
echo "Music Player Backend is ready!"
echo "========================================"

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
