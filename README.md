# CTF Registration Backend

Asynchronous FastAPI-based registration system for internal and external students with Google Sheets integration.

## Features

- ✅ Asynchronous processing with queue system
- ✅ No data loss - all registrations are queued
- ✅ Separate endpoints for internal and external students
- ✅ Automatic duplicate detection
- ✅ Thread-safe operations
- ✅ Google Sheets integration
- ✅ Automatic timestamp addition

## Setup Instructions

### 1. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
# Sync dependencies from pyproject.toml
uv sync

# Or install directly
uv pip install fastapi uvicorn pydantic gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### 3. Set Up Google Credentials

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create a new project (e.g., "CTF Registration System")

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Create Credentials > Service Account
   - Name: `ctf-registration-service`
   - Download JSON key file
   - Save as `credentials.json` in project root

4. **Share Google Sheet**
   - Copy the `client_email` from `credentials.json`
   - Share your Google Sheet with this email
   - Give **Editor** access

### 4. Run the Application

```bash
# Using UV
uv run python main.py

# Or activate virtual environment first
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Internal Registration
```bash
POST /register/internal
Content-Type: application/json

{
  "name": "John Doe",
  "reg_no": "21ITR001",
  "dept_name": "Computer Science",
  "year_of_study": "3",
  "transaction_id": "TXN123456789"
}
```

### External Registration
```bash
POST /register/external
Content-Type: application/json

{
  "name": "Jane Smith",
  "reg_no": "EXT001",
  "dept_name": "Information Technology",
  "year_of_study": "2",
  "college_name": "ABC Engineering College",
  "transaction_id": "TXN987654321"
}
```

### Queue Status
```bash
GET /queue/status
```

## Google Sheets Structure

### Internal Students Sheet (gid=0)
| Name | Registration Number | Department | Year of Study | Transaction ID | Timestamp |
|------|-------------------|------------|---------------|----------------|-----------|

### External Students Sheet (gid=1179914067)
| Name | Registration Number | Department | Year of Study | College Name | Transaction ID | Timestamp |
|------|-------------------|------------|---------------|--------------|----------------|-----------|

## Environment Variables (Production)

For deployment, set these environment variables:

```env
GOOGLE_CREDENTIALS_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-key-id
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_CLIENT_EMAIL=service-account@project-id.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=123456789
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...
GOOGLE_UNIVERSE_DOMAIN=googleapis.com
PORT=8000
```

## Testing

```bash
# Install dev dependencies
uv sync --dev

# Run tests
pytest
```

## Security Notes

- Never commit `credentials.json` to version control
- Use environment variables in production
- Rotate service account keys periodically
- Limit service account permissions to required scopes only

## Troubleshooting

### Module Not Found Error
```bash
uv sync
```

### Permission Denied on Google Sheets
- Ensure service account email has Editor access to the Google Sheet
- Check that Google Sheets API is enabled

### Queue Processing Issues
- Check `/queue/status` endpoint
- View logs for error messages

## License

MIT License
