from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import EmailStr
import os
from datetime import datetime

app = FastAPI(title="Mark MCP Server - Email Collection")

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables")

engine = create_engine(DATABASE_URL)

# Database Model
class Subscriber(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    source: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Create tables automatically
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Request model
class SubscribeRequest(SQLModel):
    email: EmailStr
    source: str | None = "website"

@app.post("/subscribe")
def subscribe(data: SubscribeRequest):
    with Session(engine) as session:
        # Check if already subscribed
        existing = session.exec(
            select(Subscriber).where(Subscriber.email == data.email)
        ).first()
        
        if existing:
            return {"message": "You're already subscribed!"}
        
        new_sub = Subscriber(email=data.email, source=data.source)
        session.add(new_sub)
        session.commit()
        
        return {
            "message": "Thank you! You've been subscribed successfully.",
            "email": data.email
        }

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Mark MCP Server",
        "website": "https://reallyraisedrough.com"
    }
