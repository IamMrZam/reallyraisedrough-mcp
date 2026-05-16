import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import resend

app = FastAPI(title="Really Raised Rough MCP")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== Resend (Correct way) ======================
resend.api_key = os.environ.get("RESEND_API_KEY")


def send_email(to_email: str, subject: str, html_content: str):
    if not resend.api_key:
        return {"error": "RESEND_API_KEY is not set"}

    params = {
        "from": "Really Raised Rough <hello@reallyraisedrough.com>",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    try:
        email = resend.Emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    return {"message": "Really Raised Rough MCP is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/send-welcome")
async def send_welcome_email(request: Request):
    data = await request.json()
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    html_content = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #166534;">Welcome to the Really Raised Rough family 🌿</h1>
        <p>Thanks for joining. You're now part of a community that stays lifted and stays sober.</p>
        
        <p><strong>Check out the latest merch drop and sober living content:</strong></p>
        
        <a href="https://reallyraisedrough.com" 
           style="display: inline-block; background-color: #4ade80; color: white; 
                  padding: 14px 28px; text-decoration: none; border-radius: 8px; 
                  font-weight: bold; margin: 20px 0;">
            Visit ReallyRaisedRough.com →
        </a>
        
        <p>Stay lifted. Stay strong. Stay you.</p>
        <p>— The Really Raised Rough Team</p>
    </div>
    """

    result = send_email(email, "Welcome to Really Raised Rough 🌱", html_content)
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
