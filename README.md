# 🎯 CTF Registration Backend API

Fast, async registration system with Google Sheets integration. Built with FastAPI.

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server runs at: **http://localhost:8000**

## 📖 Documentation

- **📚 Complete API Docs:** [API_DOCS.md](./API_DOCS.md)
- **🔧 Interactive Docs:** http://localhost:8000/docs
- **📘 Alternative Docs:** http://localhost:8000/redoc

## 🌐 API Endpoints

### 1. Internal Student Registration
```bash
POST /register/internal
```
**Required fields:** name, reg_no, dept_name, year_of_study, recipt_no

### 2. External Student Registration
```bash
POST /register/external
```
**Required fields:** name, reg_no, dept_name, year_of_study, college_name, recipt_no

### 3. Queue Status
```bash
GET /queue/status
```

## 💡 Quick Integration (Frontend)

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:8000/register/internal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "John Doe",
    reg_no: "21ITR001",
    dept_name: "Computer Science",
    year_of_study: "3",
    recipt_no: "TXN123456789"
  })
});
const data = await response.json();
```

### Axios
```javascript
const response = await axios.post('http://localhost:8000/register/internal', {
  name: "John Doe",
  reg_no: "21ITR001",
  dept_name: "Computer Science",
  year_of_study: "3",
  recipt_no: "TXN123456789"
});
```

## 🔧 Setup Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable Google Sheets API
3. Create Service Account → Download JSON key
4. Save as `credentials.json` in project root
5. Share your Google Sheet with service account email

**For detailed setup instructions, see [API_DOCS.md](./API_DOCS.md#-backend-setup)**

## 📧 Setup Email Notifications

Configure SMTP to send confirmation emails after successful registration.

1. Copy `.env.example` to `.env`
2. Add SMTP credentials (Gmail, Outlook, SendGrid, etc.)
3. For Gmail: Generate App Password at https://myaccount.google.com/apppasswords

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CTF Registration Team
```

**For detailed email setup, see [EMAIL_SETUP.md](./EMAIL_SETUP.md)**

### Test Email Configuration
```bash
python test_email.py
```

## 📊 Features

✅ Asynchronous processing with queue system  
✅ No data loss - thread-safe operations  
✅ Automatic duplicate detection  
✅ Real-time Google Sheets integration  
✅ **📧 Email confirmation after successful registration**  
✅ Beautiful HTML email templates  
✅ CORS enabled for all origins  
✅ Automatic timestamps  

## 🧪 Test API

```bash
# cURL example
curl -X POST http://localhost:8000/register/internal \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","reg_no":"T001","dept_name":"CS","year_of_study":"3","recipt_no":"TXN123"}'
```

## 🏗️ Architecture

```
Frontend → FastAPI → Queue → Worker Thread → Google Sheets
                ↓
         Instant Response
```

## 📝 Requirements

- Python 3.8+
- FastAPI, Uvicorn, Pydantic
- gspread, google-auth
- Google Cloud Project with Sheets API

## 🔒 Security

- Never commit `credentials.json`
- Use environment variables in production
- HTTPS recommended for production

## 📞 Support

- **Full Documentation:** [API_DOCS.md](./API_DOCS.md)
- **Interactive API Testing:** http://localhost:8000/docs
- **Issues:** GitHub Issues

---

**Made with ❤️ for CTF Registration System**
