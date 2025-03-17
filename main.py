from fastapi import FastAPI, Request, HTTPException, Form, Depends, status, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uvicorn
from supabase import create_client, Client
import json, asyncio
from agentic import get_agent

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create FastAPI app
app = FastAPI(
    title="NoorAI",
    description="Islamic Knowledge Assistant powered by AI",
    version="1.0.0",
)

# Set up static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Helper to get user profile
async def get_user_profile(access_token: str) -> Dict[Any, Any]:
    try:
        # Get user data from Supabase
        print(f"Attempting to get user with token: {access_token[:10]}...")
        user = supabase.auth.get_user(access_token)

        # For debugging - check if user data is retrieved
        if user and user.user:
            print(f"User retrieved: {user.user.email}")

            # Create user profile dict
            user_data = {
                "id": user.user.id,
                "email": user.user.email,
                "first_name": user.user.user_metadata.get("first_name", ""),
                "last_name": user.user.user_metadata.get("last_name", ""),
            }

            return user_data
        else:
            print("User data not found in token response")
            return None

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        # Return None on validation failure
        return None


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, access_token: Optional[str] = Cookie(None)):
    """Render the home page"""
    user = None
    if access_token:
        user = await get_user_profile(access_token)

    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request, message: Optional[str] = None, message_type: Optional[str] = None
):
    """Render the login page"""
    # Get message and message_type from query parameters if available
    if not message and "message" in request.query_params:
        message = request.query_params.get("message")

    if not message_type and "message_type" in request.query_params:
        message_type = request.query_params.get("message_type")

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": message, "message_type": message_type},
    )


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Process login form submission with Supabase"""
    try:
        # Authenticate with Supabase
        print(f"Attempting login for user: {email}")
        auth_response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        # Log successful authentication
        print(f"Login successful for: {email}")
        print(f"Token generated: {auth_response.session.access_token[:10]}...")

        # Create response with redirect to chat page instead of home
        response = RedirectResponse(url="/chat", status_code=status.HTTP_303_SEE_OTHER)

        # Set access token cookie
        max_age = (
            30 * 24 * 60 * 60 if remember else None
        )  # 30 days if remember me is checked

        # Make sure the cookie settings are correct for your environment
        # In development, you might need to set secure=False
        secure = os.getenv("ENVIRONMENT", "development") == "production"

        response.set_cookie(
            key="access_token",
            value=auth_response.session.access_token,
            httponly=True,
            max_age=max_age,
            secure=secure,  # Only use True in production with HTTPS
            samesite="lax",
        )

        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=auth_response.session.refresh_token,
            httponly=True,
            max_age=max_age,
            secure=secure,  # Only use True in production with HTTPS
            samesite="lax",
        )

        print("Cookies set, redirecting to chat")
        return response

    except Exception as e:
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            message = "Invalid email or password"
        else:
            message = "An error occurred during login. Please try again."

        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": message, "message_type": "error"},
        )


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request, message: Optional[str] = None, message_type: Optional[str] = None
):
    """Render the registration page"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": message, "message_type": message_type},
    )


@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(...),
):
    """Process registration form submission with Supabase"""
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": "Passwords do not match",
                "message_type": "error",
            },
        )

    # Validate password strength
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": "Password must be at least 8 characters",
                "message_type": "error",
            },
        )

    try:
        # Register user with Supabase
        auth_response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"first_name": first_name, "last_name": last_name}},
            }
        )

        # Redirect to login with success message
        response = RedirectResponse(
            url="/login?message=Registration+successful!+You+can+now+log+in.&message_type=success",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        return response
    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message:
            message = "This email is already registered"
        else:
            message = f"An error occurred during registration: {error_message}"

        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": message, "message_type": "error"},
        )


@app.get("/logout")
async def logout():
    """Log out the user by clearing the session"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, access_token: Optional[str] = Cookie(None)):
    """Render the chat interface"""
    # Debug log to track auth issues
    print(f"Chat page accessed. Token exists: {access_token is not None}")

    # Check if user is logged in
    if not access_token:
        print("No access token found, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Get user data from Supabase
        user = await get_user_profile(access_token)

        if not user:
            print("User profile not found, redirecting to login")
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        # For debugging - print user data (remove in production)
        print(f"User authenticated successfully: {user.get('email')}")

        # Render chat page with user data
        return templates.TemplateResponse(
            "chat.html", {"request": request, "user": user}
        )
    except Exception as e:
        # Log the specific error for debugging
        print(f"Error in chat page: {str(e)}")

        # Handle token validation errors by clearing the invalid token
        response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response


# API endpoint for Islamic knowledge questions
@app.post("/api/ask")
async def ask_question(request: Request, access_token: Optional[str] = Cookie(None)):
    """Process questions for the AI assistant using the agent"""
    # Check if user is logged in
    if not access_token:
        print("API request without access token")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Validate token by getting user
        user = await get_user_profile(access_token)
        if not user:
            print("API request with invalid token")
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Get the question from request body
        data = await request.json()
        question = data.get("question", "")

        print(f"Processing question from {user.get('email')}: {question[:30]}...")

        # For testing to see if the problem is with the agent or the API
        # Uncomment this code and comment out the agent code to test
        # return {
        #     "status": "success",
        #     "response": f"This is a test response to: {question}\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        # }

        # Get agent instance
        agent = get_agent()

        # The agent processing might be blocking and slow down the event loop
        # To avoid this, we run it in a separate thread using run_in_executor
        loop = asyncio.get_event_loop()
        try:
            response_data = await loop.run_in_executor(
                None,  # uses default executor (ThreadPoolExecutor)
                agent.answer_question,
                question,
            )

            print(f"Agent response generated for: {question[:30]}...")

            # Ensure it's valid JSON
            if isinstance(response_data, dict):
                # Make sure the response is a string
                if response_data.get("response") is None:
                    response_data["response"] = (
                        "I apologize, but I couldn't generate a proper response."
                    )

                # Sanitize the response
                if isinstance(response_data["response"], str):
                    # Limit response length if needed
                    if len(response_data["response"]) > 50000:
                        response_data["response"] = (
                            response_data["response"][:50000]
                            + "...[content truncated due to length]"
                        )
                else:
                    response_data["response"] = str(response_data["response"])

                return response_data
            else:
                # If response is not a dict, wrap it
                return {"status": "success", "response": str(response_data)}
        except Exception as e:
            print(f"Error in agent processing: {str(e)}")
            return {
                "status": "error",
                "response": f"I encountered an error while processing your question: {str(e)}",
            }

    except Exception as e:
        print(f"Error in API: {str(e)}")
        return {"status": "error", "response": f"An error occurred: {str(e)}"}


# @app.get("/api/status")
# async def status():
#     """Health check endpoint to keep the connection alive"""
#     return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
