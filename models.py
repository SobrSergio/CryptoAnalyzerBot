from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
Base = declarative_base()

class UserNotification(Base):
    __tablename__ = 'user_notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    crypto_pair = Column(String(50), nullable=False)
    target_price = Column(Float, nullable=False)
    initial_price = Column(Float, nullable=False) 
    

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
