from fastapi import FastAPI, Request, HTTPException, Form, Depends, status, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
    title="TafsirAI",
    description="Islamic Knowledge Assistant powered by AI",
    version="1.0.0",
)

# Set up static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Default credits for new users
DEFAULT_FREE_CREDITS = 3

# Payment amount in rupees
LIFETIME_ACCESS_COST = 89

# Set up Razorpay (you'll need to sign up for a Razorpay account)
import razorpay

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_zZDvredBawObm6")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "gpfb8quY17d1E0ypTtHHaO1B")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# Helper to get user profile
async def get_user_profile(access_token: str) -> Dict[Any, Any]:
    try:
        # Get user data from Supabase
        print(f"Attempting to get user with token: {access_token[:10]}...")
        user = supabase.auth.get_user(access_token)

        # For debugging - check if user data is retrieved
        if user and user.user:
            print(f"User retrieved: {user.user.email}")

            # Check if we have user metadata in our profiles table
            user_id = user.user.id
            profiles_data = (
                supabase.table("profiles").select("*").eq("id", user_id).execute()
            )

            profile_data = {}
            if profiles_data.data and len(profiles_data.data) > 0:
                profile_data = profiles_data.data[0]
            else:
                # Create a profile entry if it doesn't exist
                credits_remaining = DEFAULT_FREE_CREDITS
                has_lifetime_access = False

                new_profile = {
                    "id": user_id,
                    "credits_remaining": credits_remaining,
                    "has_lifetime_access": has_lifetime_access,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }

                supabase.table("profiles").insert(new_profile).execute()
                profile_data = new_profile

            # Create user profile dict
            user_data = {
                "id": user.user.id,
                "email": user.user.email,
                "first_name": user.user.user_metadata.get("first_name", ""),
                "last_name": user.user.user_metadata.get("last_name", ""),
                "credits_remaining": profile_data.get(
                    "credits_remaining", DEFAULT_FREE_CREDITS
                ),
                "has_lifetime_access": profile_data.get("has_lifetime_access", False),
            }

            return user_data
        else:
            print("User data not found in token response")
            return None

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        # Return None on validation failure
        return None


# Function to check if user can send a message
async def check_user_credits(user_data):
    if user_data.get("has_lifetime_access", False):
        return True

    if user_data.get("credits_remaining", 0) > 0:
        return True

    return False


# Function to reduce user credit
async def reduce_user_credit(user_id):
    try:
        # Get current profile
        profile_data = (
            supabase.table("profiles").select("*").eq("id", user_id).execute()
        )

        if profile_data.data and len(profile_data.data) > 0:
            profile = profile_data.data[0]

            # Skip if has lifetime access
            if profile.get("has_lifetime_access", False):
                return True

            # Check and reduce credits
            credits_remaining = profile.get("credits_remaining", 0)
            if credits_remaining > 0:
                supabase.table("profiles").update(
                    {
                        "credits_remaining": credits_remaining - 1,
                        "updated_at": datetime.now().isoformat(),
                    }
                ).eq("id", user_id).execute()
                return True

        return False
    except Exception as e:
        print(f"Error in reduce_user_credit: {str(e)}")
        return False


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, access_token: Optional[str] = Cookie(None)):
    """Render the home page"""
    user = None
    if access_token:
        user = await get_user_profile(access_token)

    return templates.TemplateResponse("index.html", {"request": request, "user": user})


# Add these route handlers after your existing routes

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Render the terms and conditions page"""
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Render the privacy policy page"""
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/refund", response_class=HTMLResponse)
async def refund_page(request: Request):
    """Render the refund and cancellation policy page"""
    return templates.TemplateResponse("refundPolicy.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Render the contact information page"""
    return templates.TemplateResponse("contact.html", {"request": request})

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

        # The profile is automatically created by the database trigger,
        # so we don't need to create it here anymore.

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
        print(f"Credits remaining: {user.get('credits_remaining')}")
        print(f"Has lifetime access: {user.get('has_lifetime_access')}")

        # Add Razorpay key to context
        razorpay_key = RAZORPAY_KEY_ID

        # Render chat page with user data
        return templates.TemplateResponse(
            "chat.html",
            {
                "request": request,
                "user": user,
                "razorpay_key": razorpay_key,
                "payment_amount": LIFETIME_ACCESS_COST,
            },
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

        # Check if user has credits or lifetime access
        can_send = await check_user_credits(user)
        if not can_send:
            return {
                "status": "credits_required",
                "response": "You've used all your free credits. Please upgrade to continue using TafsirAI.",
            }

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

                # Reduce user credit after successful response
                await reduce_user_credit(user["id"])

                # Update user data
                updated_user = await get_user_profile(access_token)
                response_data["credits_remaining"] = updated_user.get(
                    "credits_remaining", 0
                )
                response_data["has_lifetime_access"] = updated_user.get(
                    "has_lifetime_access", False
                )

                return response_data
            else:
                # If response is not a dict, wrap it
                reduced = await reduce_user_credit(user["id"])
                updated_user = await get_user_profile(access_token)

                return {
                    "status": "success",
                    "response": str(response_data),
                    "credits_remaining": updated_user.get("credits_remaining", 0),
                    "has_lifetime_access": updated_user.get(
                        "has_lifetime_access", False
                    ),
                }
        except Exception as e:
            print(f"Error in agent processing: {str(e)}")
            return {
                "status": "error",
                "response": f"I encountered an error while processing your question: {str(e)}",
            }

    except Exception as e:
        print(f"Error in API: {str(e)}")
        return {"status": "error", "response": f"An error occurred: {str(e)}"}


# Create a payment order
@app.post("/api/create-payment")
async def create_payment(request: Request, access_token: Optional[str] = Cookie(None)):
    # Check if user is logged in
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Validate token by getting user
        user = await get_user_profile(access_token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Skip if user already has lifetime access
        if user.get("has_lifetime_access", False):
            return {"status": "error", "message": "You already have lifetime access"}

        # Create a Razorpay order
        payment_data = {
            "amount": LIFETIME_ACCESS_COST * 100,  # amount in paise
            "currency": "INR",
            "receipt": f"receipt_{user['id'][:8]}",
            "notes": {"user_id": user["id"], "email": user["email"]},
        }

        order = razorpay_client.order.create(payment_data)

        return {
            "status": "success",
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": RAZORPAY_KEY_ID,
        }

    except Exception as e:
        print(f"Error creating payment: {str(e)}")
        return {"status": "error", "message": f"Error creating payment: {str(e)}"}


# Verify payment
@app.post("/api/verify-payment")
async def verify_payment(request: Request, access_token: Optional[str] = Cookie(None)):
    # Check if user is logged in
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Validate token by getting user
        user = await get_user_profile(access_token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Get payment data
        data = await request.json()
        payment_id = data.get("razorpay_payment_id", "")
        order_id = data.get("razorpay_order_id", "")
        signature = data.get("razorpay_signature", "")

        # Verify signature
        params_dict = {
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": order_id,
            "razorpay_signature": signature,
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Payment is verified, update user to have lifetime access
            supabase.table("profiles").update(
                {"has_lifetime_access": True, "updated_at": datetime.now().isoformat()}
            ).eq("id", user["id"]).execute()

            # Also store payment details
            payment_record = {
                "user_id": user["id"],
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": LIFETIME_ACCESS_COST,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
            }

            supabase.table("payments").insert(payment_record).execute()

            return {
                "status": "success",
                "message": "Payment verified and lifetime access granted!",
            }

        except Exception as e:
            # Invalid signature
            # Store failed payment attempt
            payment_record = {
                "user_id": user["id"],
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": LIFETIME_ACCESS_COST,
                "status": "failed",
                "error": str(e),
                "created_at": datetime.now().isoformat(),
            }

            supabase.table("payments").insert(payment_record).execute()

            return {"status": "error", "message": "Payment verification failed"}

    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return {"status": "error", "message": f"Error verifying payment: {str(e)}"}


# @app.get("/api/status")
# async def status():
#     """Health check endpoint to keep the connection alive"""
#     return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
