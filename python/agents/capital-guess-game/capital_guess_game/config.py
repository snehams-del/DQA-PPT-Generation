import os
import logging

from dotenv import load_dotenv

load_dotenv()

AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-pro")
LOGGING_LEVEL = logging.INFO

# Suppress verbose logs from Google SDK components
logging.getLogger("google_llm").setLevel(logging.WARNING)
logging.getLogger("google.adk.llm").setLevel(logging.WARNING)
logging.getLogger("google.adk.agents").setLevel(logging.WARNING)
logging.getLogger("google.generativeai").setLevel(logging.WARNING)
logging.getLogger("google.cloud").setLevel(logging.WARNING)
logging.getLogger("google.auth").setLevel(logging.WARNING)

def configure_logging_suppression():
    """Configure logging to suppress verbose logs from Google SDK components."""
    # Google SDK related loggers
    google_loggers = [
        "google_llm",
        "google_adk",
        "google.adk.llm",
        "google.adk.agents", 
        "google.adk.tools",
        "google.generativeai",
        "google.cloud",
        "google.auth",
        "google.auth.transport",
        "google.oauth2",
        "googleapiclient",
        "httplib2",
        "urllib3"
    ]
    
    for logger_name in google_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # If you want to completely suppress specific loggers
    # logging.getLogger("google_llm").setLevel(logging.CRITICAL)
    
    print("Logging suppression configured for Google SDK components")


configure_logging_suppression()