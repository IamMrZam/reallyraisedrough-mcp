from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Mark MCP Server - reallyraisedrough.com")

# ==================== SECURITY ====================
security = HTTPBearer()
API_TOKEN = "TrustNoBitch420"

def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )
    return credentials.credentials
# =================================================

class PostRequest(BaseModel):
    platform: str = "all"

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Mark MCP Server",
        "website": "https://reallyraisedrough.com"
    }

@app.post("/generate_post", dependencies=[Depends(get_current_token)])
def generate_post(request: PostRequest):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    content = f"""New content generated at {timestamp}

Check out https://reallyraisedrough.com

#ReallyRaisedRough #Marketing"""

    return {
        "status": "success",
        "platform": request.platform,
        "content": content,
        "website": "https://reallyraisedrough.com",
        "timestamp": timestamp
    }

@app.post("/send_email_list", dependencies=[Depends(get_current_token)])
def send_email_list():
    return {
        "status": "success",
        "message": "Email list ready. Send to reallyraisedrough@gmail.com",
        "website": "https://reallyraisedrough.com"
    }
