import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from resend import Resend

app = FastAPI(title="Really Raised Rough MCP - Email Service")

# ====================== CORS (Important if calling from your website) ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Change this later to your domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== Resend Setup ======================
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("⚠️ WARNING: RESEND_API_KEY is not set!")

resend_client = Resend(RESEND_API_KEY)


def send_email(to_email: str, subject: str, html_content: str):
    """Send emails to drive traffic to Reallyraisedrough.com"""
    if not RESEND_API_KEY:
        return {"error": "RESEND_API_KEY not configured"}

    params = {
        "from": "Really Raised Rough <hello@reallyraisedrough.com>",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    try:
        email = resend_client.emails.send(params)
        return {"success": True, "id": email.get("id")}
    except Exception as e:
        return {"error": str(e)}


# ====================== Routes ======================

@app.get("/")
async def root():
    return {"message": "Really Raised Rough MCP is running 🚀"}


@app.get("/health")
async def health():
    """Health check endpoint - keeps your free Render instance awake"""
    return {"status": "healthy"}


@app.post("/send-welcome")
async def send_welcome_email(request: Request):
    """Send welcome email that drives traffic to Reallyraisedrough.com"""
    try:
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

        result = send_email(
            to_email=email,
            subject="Welcome to Really Raised Rough 🌱",
            html_content=html_content
        )
        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ====================== Run (for local testing) ======================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
