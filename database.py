from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# DATABASE_URL = "postgresql://postgres.ntkhrbxtuvoehutkamnz:http%3A%2F%2Fbangladesh_lite_tube.com%2F%23%23%23%23%23%23%23%23%23%23%23%23%23@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# engine = create_engine(DATABASE_URL, echo=True) #For Supabase


# 1. This is the factory setup (Done once at startup)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()  # 1. Open a clean, isolated database session
    try:
        yield db         # 2. Hand over the 'db' object to the API route and pause here
    finally:
        db.close()       # 3. Resume here AFTER the API route finishes to safely close the session
