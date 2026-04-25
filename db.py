from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Skapa data-mapp om den inte finns
if not os.path.exists("data"):
    os.makedirs("data")

DATABASE_URL = "sqlite:///data/offert.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Modell: Service
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    price_type = Column(String)

def init_db():
    Base.metadata.create_all(engine)