# Flux Kontext Max - Secure Setup Guide

## 🔐 Environment Setup

### 1. Configure Your API Key

1. Open the `.env` file in the backend folder
2. Replace `your_api_key_here` with your actual Black Forest Labs API key:
   ```
   BFL_API_KEY=your_actual_api_key_here
   ```

### 2. Get Your API Key

1. Visit: https://api.bfl.ml
2. Sign up/login to your account
3. Generate an API key
4. Copy it to your `.env` file

### 3. Install Requirements

Run: `install_requirements.bat`

### 4. Start Server

Run: `start.bat`

### 5. Access App

Open: http://localhost:8002

## 🛡️ Security Features

- ✅ API key stored securely on server
- ✅ No client-side API key exposure
- ✅ Environment variable protection
- ✅ Secure backend processing

## 📁 Important Files

- `.env` - Your secure configuration (never share this!)
- `start.bat` - Server launcher
- `install_requirements.bat` - Dependencies installer

## 🚀 Ready to Use

Your app now has enterprise-level security with:
- Server-side API key management
- No frontend security risks
- Professional deployment ready