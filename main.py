from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI(title="Mark Social Auto-Poster MCP")

class PostRequest(BaseModel):
    platform: str = "all"

@app.get("/")
def root():
    return {"status": "online", "message": "Mark MCP is running for reallyraisedrough.com"}

@app.post("/generate_post")
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

@app.post("/send_email_list")
def send_email_list():
    return {
        "status": "success",
        "message": "Email list ready to send to reallyraisedrough@gmail.com"
    }