# Separation of Concern

| Layer    | Location        | Purpose                           |
| -------- | --------------- | --------------------------------- |
| Models   | `app/db/models/`| ORM mapping to DB                 |
| Schemas  | `app/schemas/`  | Request/response validation       |
| CRUD     | `app/crud/`     | Raw DB queries (session.query...) |
| Services | `app/services/` | Business logic                    |

# Folder Structure

```
project/
├── alembic/                    # Alembic migrations folder
│   ├── versions/
│   └── env.py
├── app/                        
│   ├── api/                    # Routers grouped by domain
│   │   ├── v1/                 # API versioning
│   │   │   ├── __init__.py
│   │   │   ├── user.py         # user-related endpoints
│   ├── core/                   
│   │   ├── config.py           # Settings
│   │   ├── auth.py             # JWT and Auth logic
│   ├── crud/                   # Business logic separated from DB and API
│   │   ├── __init__.py
│   │   ├── user.py
│   ├── db/                     # DB models and session management
│   │   ├── base.py             
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   ├── session.py          # DB engine/session maker
│   │   └── seed.py          
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   ├── services/               
│   ├── dependencies/          
│   ├── main.py                 # Entry point 
│   └── __init__.py
├── tests/                      
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_user.py
│   └── test_song.py
├── .env                        
├── .env.example                # template 
├── .gitignore
├── pyproject.toml              # Poetry config
├── alembic.ini                 # Alembic config
├── docker
└── README.md


```
