from fastapi import FastAPI, HTTPException, Header
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import EmailStr
from datetime import datetime
import resend
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mark MCP Server")

# ====================== CONFIG ======================
DATABASE_URL = "sqlite:///./subscribers.db"
API_KEY = "TrustNoBitch420"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")   # We'll add this in Render

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ====================== DATABASE ======================
class Subscriber(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    source: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

@app.on_event("startup")
def create_tables():
    SQLModel.metadata.create_all(engine)

# ====================== SCHEMAS ======================
class SubscribeRequest(SQLModel):
    email: EmailStr
    source: str | None = "website"

# ====================== ENDPOINTS ======================
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Mark MCP Server",
        "website": "https://reallyraisedrough.com"
    }

@app.post("/subscribe")
def subscribe_user(data: SubscribeRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    with Session(engine) as session:
        existing = session.exec(
            select(Subscriber).where(Subscriber.email == data.email)
        ).first()

        if existing:
            return {"message": "You're already subscribed!", "email": data.email}

        # Save to database
        new_subscriber = Subscriber(email=data.email, source=data.source)
        session.add(new_subscriber)
        session.commit()

        # ====================== SEND WELCOME EMAIL ======================
        if RESEND_API_KEY:
            try:
                params = {
                    "from": "Mark MCP Server <onboarding@resend.dev>",
                    "to": [data.email],
                    "subject": "Welcome! Here's your link to reallyraisedrough.com",
                    "html": f"""
                        <h2>Welcome!</h2>
                        <p>Thank you for subscribing.</p>
                        <p>Here's your link: <a href="https://reallyraisedrough.com">https://reallyraisedrough.com</a></p>
                    """
                }
                resend.Emails.send(params)
                logger.info(f"Welcome email sent to {data.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        return {
            "message": "Thank you! You've been subscribed and a welcome email was sent.",
            "email": data.email
        }
