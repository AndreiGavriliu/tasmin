from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the Base class for SQLAlchemy models
Base = declarative_base()

# Database connection URL (modify this as needed)
DATABASE_URL = "sqlite:///./db/app.db"

# Create engine for database connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)