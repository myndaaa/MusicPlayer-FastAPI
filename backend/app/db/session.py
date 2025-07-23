# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLAlchemy engine with database URL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # true = sql logs
    future=True,  
)

# configured Session class
SessionLocal = sessionmaker(
    autocommit=False,  
    autoflush=False,   
    bind=engine,
    future=True,
)

# Dependency to use inside FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''
How to use:

from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

'''

