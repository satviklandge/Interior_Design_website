"""
AicuSa Interiors — FastAPI Backend Server
==========================================
Serves all static files and provides REST API endpoints
for the contact form and newsletter subscription.

Run:  python main.py
  or: uvicorn main:app --reload --port 8000
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import ContactForm, NewsletterForm, APIResponse
from email_service import send_contact_email, send_newsletter_notification

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("aicusa")

# Base directory (where all HTML/CSS/JS/IMG files are)
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AicuSa Interiors API",
    description="Backend API for AicuSa Interiors website",
    version="1.0.0",
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount static asset directories
# ---------------------------------------------------------------------------
# These must be mounted BEFORE the catch-all HTML routes
app.mount("/css", StaticFiles(directory=str(BASE_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(BASE_DIR / "js")), name="js")
app.mount("/img", StaticFiles(directory=str(BASE_DIR / "img")), name="img")
app.mount("/lib", StaticFiles(directory=str(BASE_DIR / "lib")), name="lib")

# ---------------------------------------------------------------------------
# HTML Page Routes
# ---------------------------------------------------------------------------
# Map clean URLs to their HTML files
PAGE_ROUTES = {
    "/": "index.html",
    "/index": "index.html",
    "/about": "about.html",
    "/service": "service.html",
    "/project": "project.html",
    "/blog": "blog.html",
    "/single": "single.html",
    "/contact": "contact.html",
}


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the homepage."""
    return FileResponse(str(BASE_DIR / "index.html"))


@app.get("/index.html", response_class=HTMLResponse)
async def serve_index_html():
    """Serve index.html by direct filename."""
    return FileResponse(str(BASE_DIR / "index.html"))


@app.get("/about", response_class=HTMLResponse)
@app.get("/about.html", response_class=HTMLResponse)
async def serve_about():
    """Serve about page."""
    return FileResponse(str(BASE_DIR / "about.html"))


@app.get("/service", response_class=HTMLResponse)
@app.get("/service.html", response_class=HTMLResponse)
async def serve_service():
    """Serve service page."""
    return FileResponse(str(BASE_DIR / "service.html"))


@app.get("/project", response_class=HTMLResponse)
@app.get("/project.html", response_class=HTMLResponse)
async def serve_project():
    """Serve project page."""
    return FileResponse(str(BASE_DIR / "project.html"))


@app.get("/blog", response_class=HTMLResponse)
@app.get("/blog.html", response_class=HTMLResponse)
async def serve_blog():
    """Serve blog page."""
    return FileResponse(str(BASE_DIR / "blog.html"))


@app.get("/single", response_class=HTMLResponse)
@app.get("/single.html", response_class=HTMLResponse)
async def serve_single():
    """Serve single blog post page."""
    return FileResponse(str(BASE_DIR / "single.html"))


@app.get("/contact", response_class=HTMLResponse)
@app.get("/contact.html", response_class=HTMLResponse)
async def serve_contact():
    """Serve contact page."""
    return FileResponse(str(BASE_DIR / "contact.html"))


# ---------------------------------------------------------------------------
# Submissions Log (saves every form submission to a local JSON file)
# ---------------------------------------------------------------------------
SUBMISSIONS_FILE = BASE_DIR / "submissions.json"


def _save_submission(form_type: str, data: dict):
    """Save a form submission to the local JSON log file."""
    entry = {
        "type": form_type,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    # Load existing submissions
    submissions = []
    if SUBMISSIONS_FILE.exists():
        try:
            submissions = json.loads(SUBMISSIONS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            submissions = []
    # Append and save
    submissions.append(entry)
    SUBMISSIONS_FILE.write_text(json.dumps(submissions, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Submission saved to {SUBMISSIONS_FILE}")


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/contact", response_model=APIResponse)
async def handle_contact(form: ContactForm):
    """
    Handle contact form submission.
    Validates the form data, saves to local log, and sends an email via SMTP.
    """
    try:
        logger.info(f"Contact form received from: {form.name} <{form.email}>")
        # Always save locally so you can verify submissions
        _save_submission("contact", form.model_dump())
        # Try to send email (gracefully skips if SMTP not configured)
        await send_contact_email(form)
        return APIResponse(success=True, message="Your message has been sent successfully! We will contact you soon.")
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Sorry, something went wrong. Please try again later."},
        )


@app.post("/api/newsletter", response_model=APIResponse)
async def handle_newsletter(form: NewsletterForm):
    """
    Handle newsletter subscription.
    Saves to local log and sends a notification email.
    """
    try:
        logger.info(f"Newsletter subscription from: {form.name} <{form.email}>")
        # Always save locally
        _save_submission("newsletter", form.model_dump())
        # Try to send email
        await send_newsletter_notification(form)
        return APIResponse(success=True, message="Thank you for subscribing to our newsletter!")
    except Exception as e:
        logger.error(f"Newsletter error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Sorry, something went wrong. Please try again later."},
        )


# ---------------------------------------------------------------------------
# View Submissions (for testing/verification)
# ---------------------------------------------------------------------------

@app.get("/api/submissions")
async def view_submissions():
    """
    View all saved form submissions.
    Open http://localhost:8000/api/submissions in your browser to check.
    """
    if SUBMISSIONS_FILE.exists():
        try:
            data = json.loads(SUBMISSIONS_FILE.read_text(encoding="utf-8"))
            return {"total": len(data), "submissions": data}
        except Exception:
            return {"total": 0, "submissions": []}
    return {"total": 0, "submissions": []}


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "AicuSa Interiors API"}


# ---------------------------------------------------------------------------
# Run with: python main.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AicuSa Interiors server at http://localhost:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
