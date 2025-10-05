# 🎯 CTF Registration API

> **Asynchronous FastAPI backend for handling student registrations with real-time Google Sheets integration**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34a853?style=flat&logo=google-sheets&logoColor=white)](https://www.google.com/sheets/about/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Frontend Integration](#-frontend-integration-guide)
- [Backend Setup](#-backend-setup)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⚡ **Async Processing** | Non-blocking queue system ensures instant responses |
| 🔒 **No Data Loss** | Thread-safe queue persists registrations during high load |
| 🎓 **Dual Registration** | Separate endpoints for internal & external students |
| 🚫 **Duplicate Detection** | Automatic validation based on reg_no + recipt_no |
| 📊 **Real-time Sheets** | Direct integration with Google Sheets |
| ⏱️ **Auto Timestamps** | Automatic timestamp for every registration |
| 🌐 **CORS Enabled** | Ready for cross-origin requests |

---

## 🚀 Quick Start

### 1️⃣ Backend Setup (5 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd ctf_backend

# Install dependencies
pip install -r requirements.txt

# Add your Google credentials
# Place credentials.json in project root

# Start the server
python main.py
```

**Server will be running at:** `http://localhost:8000`

### 2️⃣ Verify Installation

```bash
# Check server status
curl http://localhost:8000

# Check queue status
curl http://localhost:8000/queue/status
```

---

## 📚 API Documentation

### Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

### Interactive Docs
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🎨 Frontend Integration Guide

### 📍 Endpoint 1: Internal Student Registration

**Endpoint:** `POST /register/internal`

#### Request Format

```javascript
// Fetch API Example
const registerInternal = async (studentData) => {
  try {
    const response = await fetch('http://localhost:8000/register/internal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: "John Doe",
        reg_no: "21ITR001",
        dept_name: "Computer Science",
        year_of_study: "3",
        email: "john.doe@example.com",
        recipt_no: "TXN123456789"
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Registration successful:', data);
      // Show success message to user
    } else {
      console.error('❌ Registration failed:', data);
      // Show error message to user
    }
  } catch (error) {
    console.error('❌ Network error:', error);
  }
};
```

#### Axios Example

```javascript
import axios from 'axios';

const registerInternal = async (studentData) => {
  try {
    const response = await axios.post('http://localhost:8000/register/internal', {
      name: studentData.name,
      reg_no: studentData.regNo,
      dept_name: studentData.department,
      year_of_study: studentData.year,
      email: studentData.email,
      recipt_no: studentData.recipt_no
    });
    
    console.log('✅ Success:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    throw error;
  }
};
```

#### Request Body Schema

```typescript
interface InternalRegistration {
  name: string;           // Student full name
  reg_no: string;         // Registration number (e.g., "21ITR001")
  dept_name: string;      // Department name
  year_of_study: string;  // Year (e.g., "1", "2", "3", "4")
  email: string;          // Email address
  recipt_no: string; // Payment recipt_no
}
```

#### Response Schema

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Internal registration queued successfully",
  "status": "processing",
  "data": {
    "name": "John Doe",
    "reg_no": "21ITR001",
    "type": "internal",
    "queued_at": "2025-10-05 14:30:45"
  }
}
```

**Error Response (400/500):**
```json
{
  "detail": {
    "error": "Validation error",
    "message": "Registration number is required"
  }
}
```

---

### 📍 Endpoint 2: External Student Registration

**Endpoint:** `POST /register/external`

#### Request Format

```javascript
// React Example with useState
const [formData, setFormData] = useState({
  name: '',
  reg_no: '',
  dept_name: '',
  year_of_study: '',
  college_name: '',
  email: '',
  recipt_no: ''
});

const handleSubmit = async (e) => {
  e.preventDefault();
  
  try {
    const response = await fetch('http://localhost:8000/register/external', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert('✅ Registration successful!');
      // Reset form or redirect
    } else {
      alert('❌ Registration failed: ' + data.detail.message);
    }
  } catch (error) {
    alert('❌ Network error. Please try again.');
  }
};
```

#### Request Body Schema

```typescript
interface ExternalRegistration {
  name: string;           // Student full name
  reg_no: string;         // Registration number
  dept_name: string;      // Department name
  year_of_study: string;  // Year of study
  college_name: string;   // College/University name (Required for external)
  email: string;          // Email address
  recipt_no: string; // Payment recipt_no
}
```

#### Vue.js Example

```vue
<template>
  <form @submit.prevent="registerExternal">
    <input v-model="form.name" placeholder="Name" required />
    <input v-model="form.reg_no" placeholder="Reg No" required />
    <input v-model="form.dept_name" placeholder="Department" required />
    <input v-model="form.year_of_study" placeholder="Year" required />
    <input v-model="form.college_name" placeholder="College Name" required />
    <input v-model="form.email" placeholder="Email" required />
    <input v-model="form.recipt_no" placeholder="recipt_no" required />
    <button type="submit">Register</button>
  </form>
</template>

<script>
export default {
  data() {
    return {
      form: {
        name: '',
        reg_no: '',
        dept_name: '',
        year_of_study: '',
        college_name: '',
        email: '',
        recipt_no: ''
      }
    }
  },
  methods: {
    async registerExternal() {
      try {
        const response = await fetch('http://localhost:8000/register/external', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.$toast.success('Registration successful!');
        } else {
          this.$toast.error(data.detail.message);
        }
      } catch (error) {
        this.$toast.error('Network error. Please try again.');
      }
    }
  }
}
</script>
```

---

### 📍 Endpoint 3: Queue Status

**Endpoint:** `GET /queue/status`

Check the current registration queue status.

```javascript
const checkQueueStatus = async () => {
  const response = await fetch('http://localhost:8000/queue/status');
  const data = await response.json();
  
  console.log('Queue size:', data.queue_size);
  console.log('Worker active:', data.worker_active);
  console.log('Timestamp:', data.timestamp);
};
```

**Response:**
```json
{
  "queue_size": 5,
  "worker_active": true,
  "timestamp": "2025-10-05 14:35:20"
}
```

---

## 🔧 Complete Frontend Examples

### React + TypeScript Example

```typescript
// types.ts
export interface InternalStudent {
  name: string;
  reg_no: string;
  dept_name: string;
  year_of_study: string;
  email: string;
  recipt_no: string;
}

export interface ExternalStudent extends InternalStudent {
  college_name: string;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  status: string;
  data: any;
}

// api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const registrationAPI = {
  internal: async (data: InternalStudent): Promise<ApiResponse> => {
    const response = await axios.post(`${API_BASE_URL}/register/internal`, data);
    return response.data;
  },
  
  external: async (data: ExternalStudent): Promise<ApiResponse> => {
    const response = await axios.post(`${API_BASE_URL}/register/external`, data);
    return response.data;
  },
  
  queueStatus: async () => {
    const response = await axios.get(`${API_BASE_URL}/queue/status`);
    return response.data;
  }
};

// InternalRegistrationForm.tsx
import React, { useState } from 'react';
import { registrationAPI } from './api';
import { InternalStudent } from './types';

const InternalRegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState<InternalStudent>({
    name: '',
    reg_no: '',
    dept_name: '',
    year_of_study: '',
    email: '',
    recipt_no: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      const response = await registrationAPI.internal(formData);
      setMessage('✅ Registration successful! Your data is being processed.');
      // Reset form
      setFormData({
        name: '',
        reg_no: '',
        dept_name: '',
        year_of_study: '',
        email: '',
        recipt_no: ''
      });
    } catch (error: any) {
      setMessage('❌ ' + (error.response?.data?.detail?.message || 'Registration failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" value={formData.name} onChange={handleChange} placeholder="Full Name" required />
      <input name="reg_no" value={formData.reg_no} onChange={handleChange} placeholder="Registration No" required />
      <input name="dept_name" value={formData.dept_name} onChange={handleChange} placeholder="Department" required />
      <input name="year_of_study" value={formData.year_of_study} onChange={handleChange} placeholder="Year" required />
      <input name="email" value={formData.email} onChange={handleChange} placeholder="Email" required />
      <input name="recipt_no" value={formData.recipt_no} onChange={handleChange} placeholder="recipt_no" required />
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Register'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};

export default InternalRegistrationForm;
```

### Next.js API Route Example

```typescript
// pages/api/register.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { type, ...studentData } = req.body;
  const endpoint = type === 'external' ? 'external' : 'internal';

  try {
    const response = await fetch(`http://localhost:8000/register/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(studentData)
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(data);
    }

    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

---

## 🏗️ Backend Setup

### Prerequisites

- Python 3.8+
- pip or uv package manager
- Google Cloud Project with Sheets API enabled

### Installation Steps

#### Option 1: Using pip (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd ctf_backend

# 2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add credentials.json (see below)

# 5. Run server
python main.py
```

#### Option 2: Using UV

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Run server
uv run python main.py
```

### Google Credentials Setup

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project"
3. Name: `CTF Registration System`
4. Click "Create"

#### Step 2: Enable APIs

1. Go to "APIs & Services" → "Library"
2. Enable:
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

#### Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Name:** `ctf-registration-service`
   - **Description:** Service account for CTF registration
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

#### Step 4: Generate Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose **JSON** format
5. Click "Create"
6. File downloads as `credentials.json`

#### Step 5: Place Credentials

```bash
# Move downloaded file to project root
mv ~/Downloads/your-project-*.json credentials.json
```

#### Step 6: Share Google Sheets

1. Open your Google Sheets:
   - **Internal:** https://docs.google.com/spreadsheets/d/1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ/edit?gid=0
   - **External:** https://docs.google.com/spreadsheets/d/1NXwX5RkuPMPxOonmD7cJDjCK5sxhUnvytwj7O3FMyuQ/edit?gid=1179914067

2. Click "Share" button
3. Copy `client_email` from `credentials.json`
   - Example: `ctf-registration-service@project-id.iam.gserviceaccount.com`
4. Paste in share dialog
5. Set permission: **Editor**
6. Uncheck "Notify people"
7. Click "Share"

### Environment Variables (Production)

Create `.env` file:

```env
GOOGLE_CREDENTIALS_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=key-id-here
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

---

## 🏛️ Architecture

### How It Works

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│   Frontend  │────────▶│   FastAPI    │────────▶│   Queue    │
│   (React/   │  POST   │   Endpoint   │  Add    │ (Thread-   │
│   Vue/etc)  │  JSON   │              │  Item   │   Safe)    │
└─────────────┘         └──────────────┘         └────────────┘
                              │                         │
                              │ Immediate                │
                              │ Response                 │
                              ▼                         ▼
                        ┌──────────────┐         ┌────────────┐
                        │   Success    │         │  Worker    │
                        │   Message    │         │  Thread    │
                        └──────────────┘         └────────────┘
                                                       │
                                                       │ Process
                                                       │ Items
                                                       ▼
                                                 ┌────────────┐
                                                 │   Google   │
                                                 │   Sheets   │
                                                 └────────────┘
```

### Key Components

| Component | Description |
|-----------|-------------|
| **FastAPI Endpoints** | Receive HTTP requests and validate data |
| **Queue System** | Thread-safe buffer that prevents data loss |
| **Worker Thread** | Background process that saves to Google Sheets |
| **Google Sheets** | Final destination for registration data |

### Why This Architecture?

✅ **Fast Response:** Users get instant feedback  
✅ **No Data Loss:** Queue persists during high traffic  
✅ **Resilient:** If Sheets API is slow, queue handles it  
✅ **Scalable:** Can handle concurrent requests safely  

---

## 📊 Google Sheets Structure

### Internal Students Sheet (gid=0)

| Name | Registration Number | Department | Year of Study | Email | Email | recipt_no | Timestamp |
|------|---------------------|------------|---------------|-------|-------|----------------|-----------|
| John Doe | 21ITR001 | Computer Science | 3 | john.doe@example.com | TXN123456 | 2025-10-05 14:30:00 |

### External Students Sheet (gid=1179914067)

| Name | Registration Number | Department | Year of Study | College Name | Email | Email | recipt_no | Timestamp |
|------|---------------------|------------|---------------|--------------|-------|-------|----------------|-----------|
| Jane Smith | EXT001 | IT | 2 | ABC College | jane.smith@example.com | TXN789012 | 2025-10-05 14:35:00 |

---

## 🔍 Troubleshooting

### Common Issues

#### ❌ Module Not Found Error

```bash
pip install -r requirements.txt
```

#### ❌ Permission Denied on Google Sheets

**Solution:**
1. Check service account email has **Editor** access
2. Verify Google Sheets API is enabled
3. Confirm `credentials.json` is in project root

#### ❌ CORS Error from Frontend

**Solution:** CORS is already enabled for all origins. If you still face issues:

```python
# In main.py, update CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### ❌ Queue Processing Slow

**Check queue status:**
```bash
curl http://localhost:8000/queue/status
```

**Solution:** If queue is growing, check Google Sheets API quota and permissions.

#### ❌ Duplicate Registration Error

This is expected behavior! The API prevents duplicate registrations based on:
- Registration Number + recipt_no combination

---

## 🧪 Testing

### Test with cURL

```bash
# Test Internal Registration
curl -X POST http://localhost:8000/register/internal \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Student",
    "reg_no": "TEST001",
    "dept_name": "Computer Science",
    "year_of_study": "3",
    "email": "test.student@example.com",
    "recipt_no": "TXN_TEST_123"
  }'

# Test External Registration
curl -X POST http://localhost:8000/register/external \
  -H "Content-Type: application/json" \
  -d '{
    "name": "External Test",
    "reg_no": "EXT001",
    "dept_name": "IT",
    "year_of_study": "2",
    "college_name": "Test College",
    "email": "external.test@example.com",
    "recipt_no": "TXN_EXT_456"
  }'

# Check Queue
curl http://localhost:8000/queue/status
```

### Test with Postman

1. Create new POST request
2. URL: `http://localhost:8000/register/internal`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "name": "John Doe",
  "reg_no": "21ITR001",
  "dept_name": "Computer Science",
  "year_of_study": "3",
  "email": "john.doe@example.com",
  "recipt_no": "TXN123456789"
}
```

---

## 🔒 Security Best Practices

- ✅ Never commit `credentials.json` to Git (already in `.gitignore`)
- ✅ Use environment variables in production
- ✅ Rotate service account keys every 90 days
- ✅ Limit service account permissions to Sheets API only
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for production
- ✅ Add authentication for sensitive operations

---

## 📞 Support

For issues or questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review API docs at `http://localhost:8000/docs`
3. Open an issue on GitHub

---

## 📄 License

MIT License

---

**Made with ❤️ for CTF Registration System**
