# 🐳 Docker Setup for Music Player Backend

This directory contains the Docker configuration for the Music Player backend.

## 📁 Files

- `Dockerfile` - Container definition for the FastAPI backend
- `docker-compose.yml` - Multi-container orchestration
- `start.sh` - Startup script with detailed logging
- `.dockerignore` - Files to exclude from Docker build

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Commands

```bash
# Navigate to the backend/docker directory
cd backend/docker

# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Stop all services
docker-compose down

# Stop and remove volumes (database data)
docker-compose down -v
```

## 🎯 What Happens on Startup

1. **PostgreSQL Database** starts first
2. **Backend Container** waits for database to be healthy
3. **Dependencies** are installed via Poetry
4. **Database Migrations** run via Alembic
5. **FastAPI Server** starts with uvicorn

## 🌐 Access Points

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Database**: localhost:5432

## 🔧 Environment Variables

The docker-compose.yml uses the `.env` file from the backend directory:

- `POSTGRES_DB=music_stream`
- `POSTGRES_USER=mynda`
- `POSTGRES_PASSWORD=dev`
- `JWT_SECRET_KEY=4-RX58-q787gFuNLuTUxsGjWXstRZxD9IBcqak7b0zw`
- `PASSWORD_PEPPER=KuR0m1`

## 📊 Monitoring

```bash
# Check container status
docker-compose ps

# View real-time logs
docker-compose logs -f

# Check health status
curl http://localhost:8000/health
```

## 🛠️ Development

For development with hot reload:

```bash
# The app directory is mounted as a volume
# Changes to your code will automatically reload
docker-compose up --build
```

## 🗄️ Database

- **Database**: PostgreSQL 15
- **Name**: music_stream
- **User**: mynda
- **Password**: dev
- **Port**: 5432

## 🔍 Troubleshooting

```bash
# Rebuild without cache
docker-compose build --no-cache

# Reset database
docker-compose down -v
docker-compose up --build

# Check database connection
docker-compose exec web poetry run python -c "
import psycopg2
conn = psycopg2.connect(
    dbname='music_stream',
    user='mynda',
    password='dev',
    host='db',
    port='5432'
)
print('Database connection successful!')
conn.close()
"
```

## 📋 Container Names

As per the project README, the containers are named:
- `music-db-1` - PostgreSQL database
- `music-web-1` - FastAPI backend

## 🎵 Expected Output

When `docker-compose up --build` is run, output be 

```
========================================
🎵Music Player Backend Starting...
========================================

Installing Python dependencies...
Waiting for PostgreSQL database to be ready...
Database not ready yet, waiting...
Running Alembic database migrations...
Database migrations completed successfully!

Starting FastAPI server with uvicorn...
Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health

========================================
Music Player Backend is ready!
========================================
``` 
