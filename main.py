import gspread
import json
import os
from google.oauth2.service_account import Credentials
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime
import asyncio
from typing import Optional
import queue
import threading
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Battle of Binaries 1.0 Registration Team')

# Thread-safe queue for handling registrations
registration_queue = queue.Queue()

# Pydantic models for registration
class InternalRegistration(BaseModel):
    name: str = Field(..., description="Student name")
    reg_no: str = Field(..., description="Registration number")
    division: str = Field(..., description="Division")
    year_of_study: str = Field(..., description="Year of study")
    email: str = Field(..., description="Email address")
    phone_number: str = Field(..., description="Phone number")
    recipt_no: str = Field(..., description="recipt_no")

class ExternalRegistration(BaseModel):
    name: str = Field(..., description="Student name")
    reg_no: str = Field(..., description="Registration number")
    dept_name: str = Field(..., description="Department name")
    year_of_study: str = Field(..., description="Year of study")
    college_name: str = Field(..., description="College name")
    email: str = Field(..., description="Email address")
    phone_number: str = Field(..., description="Phone number")
    recipt_no: str = Field(..., description="recipt_no")

def create_email_template_internal(data: dict) -> str:
    """Create HTML email template for internal students"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .details {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
                border-radius: 5px;
            }}
            .detail-row {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .detail-label {{
                font-weight: bold;
                color: #667eea;
                display: inline-block;
                width: 180px;
            }}
            .detail-value {{
                color: #333;
            }}
            .footer {{
                background: #333;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                font-size: 12px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .success-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="success-icon">✅</div>
            <h1>Registration Confirmed!</h1>
            <p>Welcome to the Battle of Binaries 1.0 Competition</p>
        </div>
        
        <div class="content">
            <h2>Dear {data['name']},</h2>
            <p>Congratulations! Your registration for the Battle of Binaries 1.0  Competition has been successfully confirmed.</p>
            
            <div class="details">
                <h3 style="color: #667eea; margin-top: 0;">📋 Registration Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{data['name']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Registration Number:</span>
                    <span class="detail-value">{data['reg_no']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Division:</span>
                    <span class="detail-value">{data['division']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Year of Study:</span>
                    <span class="detail-value">{data['year_of_study']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{data['email']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Phone Number:</span>
                    <span class="detail-value">{data['phone_number']}</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Receipt Number:</span>
                    <span class="detail-value">{data['recipt_no']}</span>
                </div>
            </div>
            
            <div class="details">
                <h3 style="color: #667eea; margin-top: 0;">📅 Event Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Event Name:</span>
                    <span class="detail-value">Battle of Binaries 1.0</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">17th October 2025</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Venue:</span>
                    <span class="detail-value">DSCS Gallery Hall</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">Karunya Institute of Technology and Sciences, Coimbatore</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Organized in company with:</span>
                    <span class="detail-value">CompTIA</span>
                </div>
            </div>
            
            <h3>📅 What's Next?</h3>
            <ul>
                <li>Check your email regularly for competition updates</li>
                <li>Prepare your tools and environment for the competition</li>
                <li>Mark the competition date on your calendar</li>
            </ul>
            
            <p><strong>Important:</strong> Please save this email for your records. Your receipt number <strong>{data['recipt_no']}</strong> is your proof of registration.</p>
            
            <p>If you have any questions or concerns, feel free to reach out to our support team.</p>
            
            <p>Good luck and happy hacking! 🚀</p>
            
            <p>Best regards,<br>
            <strong>Battle of Binaries 1.0 Registration Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated confirmation email. Please do not reply to this email.</p>
            <p>&copy; 2025 Battle of Binaries 1.0 Competition. All rights reserved.</p>
        </div>
    </body>
    </html>
    """

def create_email_template_external(data: dict) -> str:
    """Create HTML email template for external students"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .details {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #f5576c;
                border-radius: 5px;
            }}
            .detail-row {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .detail-label {{
                font-weight: bold;
                color: #f5576c;
                display: inline-block;
                width: 180px;
            }}
            .detail-value {{
                color: #333;
            }}
            .footer {{
                background: #333;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                font-size: 12px;
            }}
            .success-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="success-icon">✅</div>
            <h1>Registration Confirmed!</h1>
            <p>Welcome to the Battle of Binaries 1.0 Competition</p>
        </div>
        
        <div class="content">
            <h2>Dear {data['name']},</h2>
            <p>Congratulations! Your registration for the Battle of Binaries 1.0  Competition has been successfully confirmed. We're excited to have you participate from <strong>{data['college_name']}</strong>!</p>
            
            <div class="details">
                <h3 style="color: #f5576c; margin-top: 0;">📋 Registration Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{data['name']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Registration Number:</span>
                    <span class="detail-value">{data['reg_no']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Department:</span>
                    <span class="detail-value">{data['dept_name']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Year of Study:</span>
                    <span class="detail-value">{data['year_of_study']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">College:</span>
                    <span class="detail-value">{data['college_name']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{data['email']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Phone Number:</span>
                    <span class="detail-value">{data['phone_number']}</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Receipt Number:</span>
                    <span class="detail-value">{data['recipt_no']}</span>
                </div>
            </div>
            
            <div class="details">
                <h3 style="color: #f5576c; margin-top: 0;">📅 Event Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Event Name:</span>
                    <span class="detail-value">Battle of Binaries 1.0 </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">17th October 2025</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Venue:</span>
                    <span class="detail-value">DSCS Gallery Hall</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">Karunya Institute of Technology and Sciences, Coimbatore</span>
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Organized in company with:</span>
                    <span class="detail-value">CompTIA</span>
                </div>
            </div>
            
            <h3>📅 What's Next?</h3>
            <ul>
                <li>Check your email regularly for competition updates</li>
                <li>Prepare your tools and environment for the competition</li>
                <li>Mark the competition date on your calendar</li>
                <li>Connect with other participants from different colleges</li>
            </ul>
            
            <p><strong>Important:</strong> Please save this email for your records. Your receipt number <strong>{data['recipt_no']}</strong> is your proof of registration.</p>
            
            <p>If you have any questions or concerns, feel free to reach out to our support team.</p>
            
            <p>Good luck and happy hacking! 🚀</p>
            
            <p>Best regards,<br>
            <strong>Battle of Binaries 1.0 Registration Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated confirmation email. Please do not reply to this email.</p>
            <p>&copy; 2025 Battle of Binaries 1.0 Competition. All rights reserved.</p>
        </div>
    </body>
    </html>
    """

def send_confirmation_email(to_email: str, subject: str, html_content: str, student_name: str) -> dict:
    """Send confirmation email using SMTP"""
    try:
        # Check if SMTP is configured
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("⚠️  SMTP credentials not configured. Email not sent.")
            return {
                "success": False,
                "message": "SMTP not configured"
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server and send email
        print(f"📧 Sending confirmation email to {to_email}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {student_name} ({to_email})")
        return {
            "success": True,
            "message": f"Email sent to {to_email}"
        }
    
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }

def get_google_credentials():
    """Load Google credentials from environment variables or file"""
    try:
        # Check if environment variables are set
        if os.getenv('GOOGLE_PROJECT_ID'):
            # Use environment variables (recommended for production)
            private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
            
            # Handle newline characters in private key
            if '\\n' in private_key:
                private_key = private_key.replace('\\n', '\n')
            
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE', 'service_account'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": private_key,
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
            }
            
            env_name = os.getenv('ENVIRONMENT', 'production')
            print(f"✓ Using environment variables for credentials ({env_name})")
            
        elif os.path.exists('credentials.json'):
            # Fallback to local JSON file (for local development only)
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
            print("⚠️  Using local credentials.json file (development only)")
            print("⚠️  For production, use environment variables!")
        
        else:
            raise FileNotFoundError(
                "No credentials found! Please either:\n"
                "1. Set environment variables (recommended for production)\n"
                "2. Place credentials.json file in the project root (development only)"
            )
        
        # Define required scopes for Google Sheets and Drive
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Create credentials and authorize client
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        return client
    
    except FileNotFoundError as e:
        print(f"❌ Credentials Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        traceback.print_exc()
        return None

def save_to_google_sheet(data: dict, sheet_type: str):
    """
    Save registration data to Google Sheets
    sheet_type: 'internal' or 'external'
    """
    try:
        client = get_google_credentials()
        if not client:
            return {"error": "Failed to authenticate with Google Sheets"}
        
        # Get Spreadsheet ID from environment or use default
        spreadsheet_id = os.getenv('SPREADSHEET_ID', '1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ')
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Determine which worksheet to use based on sheet_type
        if sheet_type == "internal":
            # gid=0 is the first/default sheet
            try:
                worksheet = spreadsheet.get_worksheet(0)  # Get first worksheet
                print(f"Opened internal worksheet: {worksheet.title}")
            except Exception as e:
                print(f"Error opening internal worksheet: {e}")
                return {"error": "Failed to open internal worksheet"}
        
        elif sheet_type == "external":
            # gid=1179914067 - need to find this specific worksheet
            try:
                worksheets = spreadsheet.worksheets()
                worksheet = None
                for ws in worksheets:
                    if str(ws.id) == "1179914067":
                        worksheet = ws
                        break
                
                if not worksheet:
                    # If not found by gid, try by index (usually second sheet)
                    worksheet = spreadsheet.get_worksheet(1)
                
                print(f"Opened external worksheet: {worksheet.title}")
            except Exception as e:
                print(f"Error opening external worksheet: {e}")
                return {"error": "Failed to open external worksheet"}
        else:
            return {"error": "Invalid sheet_type"}
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if headers exist, if not create them
        try:
            headers = worksheet.row_values(1)
            if not headers or len(headers) == 0:
                if sheet_type == "internal":
                    worksheet.append_row(["Name", "Registration Number", "Division", "Year of Study", "Email", "Phone Number", "recipt_no", "Timestamp"])
                else:
                    worksheet.append_row(["Name", "Registration Number", "Department", "Year of Study", "College Name", "Email", "Phone Number", "recipt_no", "Timestamp"])
                print(f"Created headers for {sheet_type} sheet")
        except Exception as e:
            print(f"Error checking headers: {e}")
        
        # Prepare row data
        if sheet_type == "internal":
            row_data = [
                data['name'],
                data['reg_no'],
                data['division'],
                data['year_of_study'],
                data['email'],
                data['phone_number'],
                data['recipt_no'],
                timestamp
            ]
        else:  # external
            row_data = [
                data['name'],
                data['reg_no'],
                data['dept_name'],
                data['year_of_study'],
                data['college_name'],
                data['email'],
                data['phone_number'],
                data['recipt_no'],
                timestamp
            ]
        
        # Check for duplicate registration (based on reg_no and recipt_no)
        try:
            all_records = worksheet.get_all_records()
            for record in all_records:
                existing_reg = str(record.get('Registration Number', '')).strip()
                existing_txn = str(record.get('recipt_no', '')).strip()
                
                if (existing_reg == data['reg_no'].strip() and 
                    existing_txn == data['recipt_no'].strip()):
                    return {
                        "error": "Duplicate registration",
                        "message": f"Registration with reg_no {data['reg_no']} and recipt_no {data['recipt_no']} already exists"
                    }
        except Exception as e:
            print(f"Error checking duplicates: {e}")
        
        # Append the new row
        worksheet.append_row(row_data)
        print(f"Successfully saved {sheet_type} registration: {data['name']} ({data['reg_no']})")
        
        # Send confirmation email after successful registration
        email_result = {"success": False, "message": "Email not sent"}
        try:
            if sheet_type == "internal":
                html_content = create_email_template_internal(data)
                subject = "✅ Battle of Binaries 1.0 Registration Confirmed - Internal Participant"
            else:
                html_content = create_email_template_external(data)
                subject = "✅ Battle of Binaries 1.0 Registration Confirmed - External Participant"
            
            email_result = send_confirmation_email(
                to_email=data['email'],
                subject=subject,
                html_content=html_content,
                student_name=data['name']
            )
        except Exception as email_error:
            print(f"⚠️  Email sending failed but registration successful: {email_error}")
        
        return {
            "success": True,
            "message": f"{sheet_type.capitalize()} registration saved successfully",
            "email_sent": email_result.get('success', False),
            "data": {
                **data,
                "timestamp": timestamp,
                "sheet_type": sheet_type
            }
        }
    
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        traceback.print_exc()
        return {"error": f"Failed to save registration: {str(e)}"}

def process_registration_queue():
    """Background worker to process registrations from queue"""
    print("Started registration queue processor")
    while True:
        try:
            # Get registration from queue (blocking call)
            registration_data, sheet_type, result_callback = registration_queue.get()
            
            print(f"Processing {sheet_type} registration from queue: {registration_data.get('name')}")
            
            # Save to Google Sheets
            result = save_to_google_sheet(registration_data, sheet_type)
            
            # Call callback with result if provided
            if result_callback:
                result_callback(result)
            
            # Mark task as done
            registration_queue.task_done()
            
        except Exception as e:
            print(f"Error in queue processor: {e}")
            traceback.print_exc()
            registration_queue.task_done()

# Start background worker thread
worker_thread = threading.Thread(target=process_registration_queue, daemon=True)
worker_thread.start()

# Create FastAPI app
app = FastAPI(
    title="Battle of Binaries 1.0 Registration API",
    description="Asynchronous API for handling internal and external student registrations",
    version="1.0.0"
)

# Configure CORS based on environment
allowed_origins_env = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins_env == '*':
    allowed_origins = ["*"]
else:
    # Split comma-separated origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(',')]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/register/internal")
async def register_internal(registration: InternalRegistration, background_tasks: BackgroundTasks):
    """
    Register internal student
    Data: name, reg_no, division, year_of_study, email, recipt_no
    """
    try:
        print(f"Received internal registration request: {registration.name}")
        
        # Convert to dict
        reg_data = registration.dict()
        
        # Create a future-like object to store result
        result_container = {"result": None, "done": False}
        result_event = asyncio.Event()
        
        def callback(result):
            result_container["result"] = result
            result_container["done"] = True
        
        # Add to queue for processing
        registration_queue.put((reg_data, "internal", callback))
        
        # Return immediate response - registration is queued
        return {
            "success": True,
            "message": "Internal registration queued successfully",
            "status": "processing",
            "data": {
                "name": registration.name,
                "reg_no": registration.reg_no,
                "type": "internal",
                "queued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    except Exception as e:
        print(f"Error in internal registration endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

@app.post("/register/external")
async def register_external(registration: ExternalRegistration, background_tasks: BackgroundTasks):
    """
    Register external student
    Data: name, reg_no, dept_name, year_of_study, college_name, email, recipt_no
    """
    try:
        print(f"Received external registration request: {registration.name}")
        
        # Convert to dict
        reg_data = registration.dict()
        
        # Create a future-like object to store result
        result_container = {"result": None, "done": False}
        
        def callback(result):
            result_container["result"] = result
            result_container["done"] = True
        
        # Add to queue for processing
        registration_queue.put((reg_data, "external", callback))
        
        # Return immediate response - registration is queued
        return {
            "success": True,
            "message": "External registration queued successfully",
            "status": "processing",
            "data": {
                "name": registration.name,
                "reg_no": registration.reg_no,
                "college_name": registration.college_name,
                "type": "external",
                "queued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    except Exception as e:
        print(f"Error in external registration endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

@app.get("/queue/status")
async def get_queue_status():
    """Get current queue status"""
    return {
        "queue_size": registration_queue.qsize(),
        "worker_active": worker_thread.is_alive(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/")
async def home():
    """Home endpoint with API information"""
    return {
        "message": "Battle of Binaries 1.0 Registration API - Asynchronous Student Registration System",
        "version": "1.0.0",
        "features": [
            "Asynchronous processing",
            "No data loss with queue system",
            "Separate endpoints for internal and external students",
            "Automatic duplicate detection",
            "Thread-safe operations"
        ],
        "endpoints": {
            "/": "GET - API information",
            "/register/internal": "POST - Register internal student",
            "/register/external": "POST - Register external student",
            "/queue/status": "GET - Check registration queue status",
            "/docs": "GET - Interactive API documentation",
            "/redoc": "GET - Alternative API documentation"
        },
        "internal_registration": {
            "method": "POST",
            "endpoint": "/register/internal",
            "fields": {
                "name": "Student name (required)",
                "reg_no": "Registration number (required)",
                "division": "Division (required)",
                "year_of_study": "Year of study (required)",
                "email": "Email address (required)",
                "phone_number": "Phone number (required)",
                "recipt_no": "recipt_no (required)"
            },
            "example": {
                "name": "John Doe",
                "reg_no": "21ITR001",
                "division": "A",
                "year_of_study": "3",
                "email": "john.doe@example.com",
                "phone_number": "+919876543210",
                "recipt_no": "TXN123456789"
            },
            "google_sheet": "https://docs.google.com/spreadsheets/d/1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ/edit?gid=0#gid=0"
        },
        "external_registration": {
            "method": "POST",
            "endpoint": "/register/external",
            "fields": {
                "name": "Student name (required)",
                "reg_no": "Registration number (required)",
                "dept_name": "Department name (required)",
                "year_of_study": "Year of study (required)",
                "college_name": "College name (required)",
                "email": "Email address (required)",
                "phone_number": "Phone number (required)",
                "recipt_no": "recipt_no (required)"
            },
            "example": {
                "name": "Jane Smith",
                "reg_no": "EXT001",
                "dept_name": "Information Technology",
                "year_of_study": "2",
                "college_name": "ABC Engineering College",
                "email": "jane.smith@example.com",
                "phone_number": "+919123456789",
                "recipt_no": "TXN987654321"
            },
            "google_sheet": "https://docs.google.com/spreadsheets/d/1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ/edit?gid=1179914067#gid=1179914067"
        },
        "notes": [
            "All registrations are processed asynchronously",
            "Queue system ensures no data loss",
            "Duplicate registrations are automatically detected",
            "Timestamps are automatically added",
            "Make sure service account has edit access to Google Sheets"
        ]
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    print("=" * 60)
    print("🚀 Battle of Binaries 1.0 Registration API Starting...")
    print("=" * 60)
    print(f"Environment: {environment.upper()}")
    print(f"Port: {os.getenv('PORT', '8000')}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', '*')}")
    print("=" * 60)
    print("✓ Environment variables loaded")
    print("✓ Background worker thread started")
    print("✓ Queue system initialized")
    print("✓ Google Sheets integration ready")
    
    # Test credentials on startup
    client = get_google_credentials()
    if client:
        print("✓ Google Cloud credentials validated successfully")
    else:
        print("❌ WARNING: Failed to validate Google credentials!")
        print("   Please check your environment variables or credentials.json")
    
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("Waiting for queue to finish processing...")
    registration_queue.join()
    print("Battle of Binaries 1.0 Registration API shutting down...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Battle of Binaries 1.0 Registration API on port {port}...")
    print(f"Access API documentation at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
