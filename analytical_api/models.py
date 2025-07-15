from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Float
from .database import Base

class Message(Base):
    __tablename__ = 'fct_messages'
    __table_args__ = {'schema': 'marts'}

    message_id = Column(BigInteger, primary_key=True, index=True)
    message_ts = Column(DateTime(timezone=True))
    date_day = Column(DateTime)
    clean_channel_name = Column(String)
    message_text = Column(String)
    view_count = Column(Integer)
    has_image = Column(Boolean)
    message_length = Column(Integer)

class ImageDetection(Base):
    __tablename__ = 'fct_image_detections'
    __table_args__ = {'schema': 'marts'}

    message_id = Column(BigInteger, primary_key=True)
    detected_object = Column(String, primary_key=True)
    confidence_score = Column(Float)