# DocSign — Secure & Modern Document Signing

**GitHub Description:**  
*A full-stack document signing app. Upload PDFs or images, annotate them with text, drawn signatures, dates, and freehand drawing, then save and download the signed result.*.*

---

## 📖 Overview

DocSign is a full-stack document management and signing platform built with Django. It provides an intuitive, seamless workflow for users to upload PDFs or images, annotate them with text, dates, and freehand signatures, and securely save the finalized documents. 

Designed with modern web aesthetics (glassmorphism, vibrant gradients, and fluid micro-animations), DocSign offers an enterprise-level signing experience without the enterprise price tag. It is built to run locally for development and is fully configured for serverless deployment on Vercel.

## ✨ Key Features

- **Secure Authentication System:**
  - Local email/password registration with SMTP email verification codes.
  - Seamless Google OAuth2 integration for one-click sign-in.
- **Rich Document Editor:**
  - Responsive canvas overlay for drawing freehand signatures.
  - Drag-and-drop text and date annotations.
  - Supports PDF parsing (via PDF.js) and direct Image (PNG/JPG) rendering.
- **Interactive API Explorer:**
  - Custom-built, interactive API documentation at `/docs/`.
  - Test endpoints directly from the browser with automatic CSRF token handling.
- **Production-Ready Architecture:**
  - Decoupled `accounts` and `signer` apps for clear separation of concerns.
  - Pre-configured `vercel.json` and `build.sh` for instant Vercel deployment.
  - Dynamic database routing (SQLite for local, Vercel PostgreSQL for production).
  - WhiteNoise integration for efficient static file serving.

---

## 🛠️ Tech Stack

- **Backend:** Python, Django 4.2+
- **Frontend:** HTML5, Vanilla CSS (Custom Design System), JavaScript
- **Database:** SQLite (Local) / PostgreSQL (Production)
- **Deployment:** Vercel (Serverless Functions)
- **Icons & Typography:** Tabler Icons, Google Fonts (Inter, Fira Code)

---

## 🚀 Local Development Setup

Follow these steps to get DocSign running on your local machine.

### 1. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/FavieCodes/DocSign.git
cd DocSign

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (next to `manage.py`) by copying the example:
```bash
cp .env.example .env
```
Fill in the following variables in your `.env` file:
- `SECRET_KEY`: A random secure string.
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: For Google OAuth.
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`: For sending verification emails (Use a Google App Password).

*(Note: If you don't want to set up SMTP locally, you can add `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` to your `.env` to print verification codes to the terminal).*

### 4. Database Setup & Run Server
```bash
# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## 🌐 API Documentation

DocSign includes a beautifully designed, built-in interactive API Explorer.

Once the server is running and you are logged in, navigate to:  
👉 **`http://127.0.0.1:8000/docs/`**

From there, you can view request payloads, required parameters, and execute live API calls to manage your documents.

---

## ☁️ Vercel Deployment

This project is pre-configured for Vercel. 

1. Push your code to GitHub.
2. Go to the [Vercel Dashboard](https://vercel.com/) and import the repository.
3. Under **Build & Development Settings**, Vercel should automatically detect Django. The `build.sh` script handles static file collection.
4. Go to the **Storage** tab in Vercel and create a **Vercel Postgres** database. Link it to your project (this automatically injects the `DATABASE_URL` environment variable).
5. Add your remaining Environment Variables in Vercel (`SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SMTP` credentials).
6. Click **Deploy**.

---

## 📁 Project Structure

```text
docsign/
├── accounts/           # Authentication app (Login, Signup, Google OAuth)
├── docsign/            # Core Django configuration & root routing
├── signer/             # Main document management & API app
│   ├── templates/      # Landing page, Dashboard, and API Docs UI
│   └── views.py        # Core application logic
├── media/              # User-uploaded files (excluded from git)
├── staticfiles/        # Compiled static assets for production
├── .env.example        # Template for environment variables
├── build.sh            # Vercel deployment script
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel serverless routing configuration
└── manage.py           # Django execution script
```

---

## 📄 License
This project is licensed under the MIT License.
