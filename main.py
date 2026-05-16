from fastapi import FastAPI, HTTPException, Header
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import EmailStr
from datetime import datetime
import logging
import os
from resend import Resend

resend = Resend(os.environ["RESEND_API_KEY"])

def send_email(to_email: str, subject: str, html_content: str):
    """Send an email using Resend. Use this to drive traffic to Reallyraisedrough.com"""
    params = {
        "from": "Really Raised Rough <hello@reallyraisedrough.com>",  # Update after you verify domain
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    return resend.emails.send(params)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mark MCP Server")
from fastapi import FastAPI

app = FastAPI()

# ====================== HEALTH CHECK ======================
@app.get('/health')
def health_check():
    return {"status": "healthy", "service": "reallyraisedrough-mcp"}
    
# ========================================================

# Your existing routes go below this line...
# ====================== CONFIG ======================
DATABASE_URL = "sqlite:///./subscribers.db"
API_KEY = "TrustNoBitch420"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    logger.warning("RESEND_API_KEY not found. Emails will not be sent.")

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
    logger.info("Database initialized")

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
@app.post("/send-welcome")          # or use @app.route if you're on Flask
async def send_welcome_email(data: dict):
    email = data.get("email")
    if not email:
        return {"error": "Email is required"}, 400

    html = """
    <h1>Welcome to Really Raised Rough 🌿</h1>
    <p>Thanks for joining the family. Check out the latest merch and sober living content:</p>
    <a href="https://reallyraisedrough.com" style="background:#4ade80;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;">Visit ReallyRaisedRough.com →</a>
    <p>Stay lifted. Stay strong.</p>
    """

    result = send_email(
        to_email=email,
        subject="Welcome to the Really Raised Rough family",
        html_content=html
    )
    return {"message": "Email sent", "id": result.get("id")}
@app.post("/)
def subscribe_user(data: SubscribeRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    with Session(engine) as session:
        # Check if already exists
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
                    "from": "Really Raised Rough <onboarding@resend.dev>",
                    "to": [data.email],
                    "subject": "Welcome to Really Raised Rough",
                    "html": f"""
                        <h2>Welcome!</h2>
                        <p>Thank you for subscribing to Really Raised Rough.</p>
                        <p>Visit your store here: <a href="https://reallyraisedrough.com">https://reallyraisedrough.com</a></p>
                    """
                }
                resend.Emails.send(params)
                logger.info(f"Welcome email sent to {data.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        return {
            "message": "Thank you! A welcome email has been sent.",
            "email": data.email
        }
