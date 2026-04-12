"""
Pydantic models for API request validation.
AicuSa Interiors — FastAPI Backend
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ContactForm(BaseModel):
    """Validates the contact form submission from contact.html"""
    name: str = Field(..., min_length=1, max_length=100, description="Sender's full name")
    email: EmailStr = Field(..., description="Sender's email address")
    contact_no: str = Field(..., min_length=10, max_length=15, description="10-digit mobile number")
    subject: str = Field(default="Contact Form", max_length=200, description="Message subject")
    project_type: str = Field(default="Not selected", description="Type of project")
    possession: str = Field(default="Not selected", description="Status of possession")
    budget: str = Field(default="Not selected", description="Budget range")
    scope: str = Field(default="None selected", description="Scope of work")
    other_project_text: Optional[str] = Field(default=None, max_length=500, description="Details if 'Other' project type")


class NewsletterForm(BaseModel):
    """Validates the newsletter subscription form in the footer"""
    name: str = Field(..., min_length=1, max_length=100, description="Subscriber's name")
    email: EmailStr = Field(..., description="Subscriber's email address")


class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
