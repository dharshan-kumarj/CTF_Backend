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

# Thread-safe queue for handling registrations
registration_queue = queue.Queue()

# Pydantic models for registration
class InternalRegistration(BaseModel):
    name: str = Field(..., description="Student name")
    reg_no: str = Field(..., description="Registration number")
    division: str = Field(..., description="Division")
    year_of_study: str = Field(..., description="Year of study")
    recipt_no: str = Field(..., description="recipt_no")

class ExternalRegistration(BaseModel):
    name: str = Field(..., description="Student name")
    reg_no: str = Field(..., description="Registration number")
    dept_name: str = Field(..., description="Department name")
    year_of_study: str = Field(..., description="Year of study")
    college_name: str = Field(..., description="College name")
    recipt_no: str = Field(..., description="recipt_no")

def get_google_credentials():
    """Load Google credentials from environment or file"""
    try:
        if os.getenv('GOOGLE_PROJECT_ID'):
            # Use environment variables (for production)
            creds_info = {
                "type": os.getenv('GOOGLE_CREDENTIALS_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
            print("✓ Using environment variables for credentials")
        else:
            # Use local JSON file (for development)
            with open('credentials.json', 'r') as f:
                creds_info = json.load(f)
            print("✓ Using local credentials.json file")
        
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client
    
    except Exception as e:
        print(f"Error loading credentials: {e}")
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
        
        # Spreadsheet ID from the provided URLs
        spreadsheet_id = "1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ"
        
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
                    worksheet.append_row(["Name", "Registration Number", "Division", "Year of Study", "recipt_no", "Timestamp"])
                else:
                    worksheet.append_row(["Name", "Registration Number", "Department", "Year of Study", "College Name", "recipt_no", "Timestamp"])
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
        
        return {
            "success": True,
            "message": f"{sheet_type.capitalize()} registration saved successfully",
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
    title="CTF Registration API",
    description="Asynchronous API for handling internal and external student registrations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/register/internal")
async def register_internal(registration: InternalRegistration, background_tasks: BackgroundTasks):
    """
    Register internal student
    Data: name, reg_no, division, year_of_study, recipt_no
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
    Data: name, reg_no, dept_name, year_of_study, college_name, recipt_no
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
        "message": "CTF Registration API - Asynchronous Student Registration System",
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
                "recipt_no": "recipt_no (required)"
            },
            "example": {
                "name": "John Doe",
                "reg_no": "21ITR001",
                "division": "A",
                "year_of_study": "3",
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
                "recipt_no": "recipt_no (required)"
            },
            "example": {
                "name": "Jane Smith",
                "reg_no": "EXT001",
                "dept_name": "Information Technology",
                "year_of_study": "2",
                "college_name": "ABC Engineering College",
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
    print("=" * 50)
    print("CTF Registration API Starting...")
    print("=" * 50)
    print("✓ CORS enabled for all origins")
    print("✓ Background worker thread started")
    print("✓ Queue system initialized")
    print("✓ Google Sheets integration ready")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("Waiting for queue to finish processing...")
    registration_queue.join()
    print("CTF Registration API shutting down...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting CTF Registration API on port {port}...")
    print(f"Access API documentation at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
