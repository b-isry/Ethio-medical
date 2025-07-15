from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kara Solutions - Ethiopian Medical Data API")

@app.get("/api/search/messages", response_model=List[schemas.Message], tags=["Messages"])
def search_for_messages(query: str, db: Session = Depends(get_db)):
    """
    Searches for messages containing a specific keyword (e.g., 'paracetamol').
    """
    messages = crud.search_messages(db, query=query)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this query")
    return messages

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct], tags=["Reports"])
def get_top_mentioned_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the most frequently mentioned products/drugs across all channels.
    This endpoint performs simple text analysis to identify product names.
    """
    return crud.get_top_products(db, limit=limit)


@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity], tags=["Channels"])
def get_channel_posting_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns the daily posting activity (number of messages per day) for a specific channel.
    Channel name should match the 'clean_channel_name' from your dbt model (e.g., 'Chemed App').
    """
    activity = crud.get_channel_activity(db, channel_name=channel_name)
    if not activity:
        raise HTTPException(status_code=404, detail="No activity found for this channel name")
    return activity