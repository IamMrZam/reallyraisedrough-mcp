from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime

app = FastAPI(title="Mark Social Auto-Poster MCP")

# ====================== SECURITY ======================
security = HTTPBearer()

# Change this to your own secret key later
API_TOKEN = "TrustNoBitch420"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )
    return credentials.credentials
# =====================================================

class PostRequest(BaseModel):
    platform: str = "all"

@app.get("/")
def root():
    return {"status": "online", "message": "Mark MCP is running (with token)"}

@app.post("/generate_post", dependencies=[Depends(verify_token)])
def generate_post(request: PostRequest):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""New post generated at {now}

Check out https://reallyraisedrough.com

#ReallyRaisedRough"""

    return {
        "status": "success",
        "platform": request.platform,
        "content": content,
        "website": "https://reallyraisedrough.com"
    }

@app.post("/send_email_list", dependencies=[Depends(verify_token)])
def send_email_list():
    return {
        "status": "success",
        "message": "Email list ready to send to reallyraisedrough@gmail.com"
    }
    }
