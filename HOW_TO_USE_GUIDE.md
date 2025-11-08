# 📖 How to Use Guide - For Everyone

## 🎯 What is This Software?

This is a **Proxy Manager** - a tool that helps you:
- ✅ Connect to the internet through different servers (called "proxies")
- ✅ Automatically find the **best proxy** based on performance
- ✅ Use proxies for web scraping (collecting data from websites)
- ✅ Keep track of which proxies work best

**Think of it like:** A smart assistant that finds you the fastest, most reliable internet connection.

---

## 🚀 Getting Started (Step by Step)

### **Step 1: Open Terminal**

**On Mac:**
- Press `Command + Space` (opens Spotlight)
- Type "Terminal"
- Press Enter

**On Windows:**
- Press `Windows + R`
- Type "cmd"
- Press Enter

**On Linux:**
- Press `Ctrl + Alt + T`

---

### **Step 2: Go to Your Project Folder**

In the Terminal, type:

```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
```

Press Enter.

**What this does:** This tells your computer to go to the folder where the software is located.

---

### **Step 3: Start the Server**

Type this command:

```bash
./run_server.sh
```

Press Enter.

**What you'll see:**
```
🚀 Starting Proxy Manager Server...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Good!** The server is now running.

**⚠️ Important:** Keep this terminal window open! Don't close it while using the software.

---

### **Step 4: Open the Website**

**Open your web browser** (Chrome, Firefox, Safari, etc.)

**Type this in the address bar:**
```
http://localhost:8000/docs
```

Press Enter.

**What you'll see:** A webpage with a list of buttons and options. This is called "Swagger UI" - it's like a control panel for the software.

---

## 👤 Creating Your Account

### **Step 5: Register (First Time Only)**

**On the Swagger UI page:**

1. **Find** the section called **"auth"** (it's usually near the top)
2. **Click** on **"POST /auth/register"** (it's a blue button)
3. **Click** the **"Try it out"** button (top right of that section)
4. **You'll see a form** with three boxes:
   - `username`: Type your username (e.g., "myuser")
   - `email`: Type your email (e.g., "myuser@example.com")
   - `password`: Type your password (e.g., "mypassword123")
5. **Click** the **"Execute"** button (blue button at the bottom)
6. **Look at the response** - you should see your user information

**✅ Done!** You've created your account.

**Note:** The first user you create automatically becomes an "admin" (administrator).

---

## 🔐 Logging In

### **Step 6: Login to Get Your Token**

**On the Swagger UI page:**

1. **Find** **"POST /auth/login"** (under the "auth" section)
2. **Click** **"Try it out"**
3. **You'll see form fields** (not a JSON editor):
   - `username`: Type your username (same as Step 5)
   - `password`: Type your password (same as Step 5)
4. **Click** **"Execute"**
5. **Look at the response** - you'll see something like:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
6. **Copy the `access_token`** - this is your "key" to use the software

**✅ Done!** You're logged in.

**⚠️ Important:** Save this token somewhere safe! You'll need it for every request.

---

## 🔑 Using Your Token (Authorization)

### **Step 7: Use the Authorize Button (Easy Way!)**

**✅ The "Authorize" button now works!** You can use it to add your token once, and it will work for all requests.

**On the Swagger UI page:**

1. **Click** the green **"Authorize"** button (top right)
2. **You'll see a modal** with:
   - **HTTPBearer** section
   - **Value** field (this is where you paste your token!)
3. **Paste your `access_token`** in the "Value" field
   - Just paste the token (starts with `eyJ...`)
   - **Don't** add "Bearer " prefix - it's added automatically
4. **Click** "Authorize"
5. **Click** "Close"

**✅ Done!** All authenticated endpoints will now work automatically!

**Note:** If you prefer, you can still add the token manually to each request (see alternative method below).

**Alternative Method (Manual Token Entry):**

If you prefer to add the token manually to each request:

1. **Click** "Try it out" on any endpoint
2. **Scroll down** to see the request details
3. **Look for** "Authorization" or "Headers" section
4. **Add**:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer YOUR_ACCESS_TOKEN_HERE`
     - Replace `YOUR_ACCESS_TOKEN_HERE` with your actual token from Step 6
     - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
5. **Click** "Execute"

---

## 📊 Adding Proxies

### **Step 8: Add a Proxy**

**What is a proxy?** A proxy is a server that acts as a middleman between you and the internet. It helps you access websites through a different IP address.

**On the Swagger UI page:**

1. **Find** **"POST /proxies"** (under the "proxies" section)
2. **Click** **"Try it out"**
3. **Add your token** (from Step 7):
   - Header name: `Authorization`
   - Header value: `Bearer YOUR_TOKEN`
4. **Enter proxy details:**
   ```json
   {
     "ip": "192.168.1.100",
     "port": 8080,
     "protocol": "http"
   }
   ```
   - `ip`: The proxy server's IP address
   - `port`: The port number (usually 8080, 3128, or 1080)
   - `protocol`: Usually "http" or "https"
   - `username`: (Optional) If your proxy requires a username
   - `password`: (Optional) If your proxy requires a password
5. **Click** **"Execute"**
6. **See the response** - your proxy has been added!

**✅ Done!** Your proxy is now in the system.

**Note:** If you don't have a proxy, you can use free proxy services or test proxies. The system will automatically test if the proxy works.

---

## ⭐ Getting the Best Proxy (Health Score)

### **Step 9: Get the Best Proxy by Health Score**

**What is Health Score?** Health Score is a rating from 0 to 100 that tells you how good a proxy is. Higher score = better proxy.

**The system automatically calculates health score based on:**
- ✅ Is the proxy working? (40 points)
- ✅ How fast is it? (30 points)
- ✅ How many times has it failed? (20 points)
- ✅ When was it last checked? (10 points)

**On the Swagger UI page:**

1. **Find** **"GET /proxy"** (under the "proxy" section)
2. **Click** **"Try it out"**
3. **Add your token** (from Step 7):
   - Header name: `Authorization`
   - Header value: `Bearer YOUR_TOKEN`
4. **Set the strategy:**
   - Find the `strategy` parameter
   - Type: `health_score`
   - This tells the system to give you the **best proxy** based on health score
5. **Click** **"Execute"**
6. **See the response:**
   ```json
   {
     "id": 1,
     "ip": "192.168.1.100",
     "port": 8080,
     "address": "192.168.1.100:8080",
     "protocol": "http",
     "health_score": 85.5,
     "latency": 120.5,
     "is_working": true
   }
   ```

**✅ Done!** You got the best proxy!

**What the numbers mean:**
- `health_score`: 85.5 out of 100 (very good!)
- `latency`: 120.5 milliseconds (how fast it responds)
- `is_working`: true (the proxy is working)

---

## 🕷️ Using Proxy for Web Scraping

### **Step 10: Web Scraping with Python**

**What is web scraping?** Web scraping is automatically collecting data from websites.

**Option A: Use the Provided Script (Easiest)**

**Open a NEW terminal window** (keep the server running in the first one):

1. **Go to your project folder:**
   ```bash
   cd /Users/yadhukrishna/Downloads/capstone/CapProj
   ```

2. **Run the test script:**
   ```bash
   python3 simple_proxy_test.py
   ```

**What this does:**
- ✅ Automatically logs in
- ✅ Gets the best proxy by health score
- ✅ Tests the connection
- ✅ Shows you the results

**✅ Done!** If you see "Proxy is working!", you're all set!

---

**Option B: Full Web Scraping Example**

**In the same terminal:**

```bash
python3 web_scraping_with_proxy.py
```

**What this does:**
- ✅ Gets the best proxy by health score
- ✅ Shows web scraping examples
- ✅ Tests multiple websites
- ✅ Shows all proxies with health scores

**✅ Done!** You've seen a complete web scraping demonstration!

---

## 📋 Common Tasks

### **View All Proxies**

1. **Find** **"GET /proxies"** (under "proxies" section)
2. **Click** **"Try it out"**
3. **Add your token** (Authorization header)
4. **Set parameters:**
   - `working_only`: true (only show working proxies)
   - `limit`: 100 (how many to show)
5. **Click** **"Execute"**
6. **See the list** of all your proxies with health scores!

---

### **Test a Proxy**

1. **Find** **"POST /proxies/{proxy_id}/test"** (under "proxies" section)
2. **Click** **"Try it out"**
3. **Add your token**
4. **Enter** the `proxy_id` (the ID number of the proxy)
5. **Click** **"Execute"**
6. **See the result** - the system will test if the proxy works

---

### **Delete a Proxy**

1. **Find** **"DELETE /proxies/{proxy_id}"** (under "proxies" section)
2. **Click** **"Try it out"**
3. **Add your token**
4. **Enter** the `proxy_id` (the ID number of the proxy)
5. **Click** **"Execute"**
6. **Done!** The proxy has been removed

---

## ❓ Troubleshooting (Common Problems)

### **Problem 1: "401 Unauthorized" Error**

**What it means:** You're not logged in or your token is wrong.

**Solution:**
1. Go back to Step 6 and login again
2. Copy your new `access_token`
3. Make sure you're adding it correctly:
   - Header name: `Authorization`
   - Header value: `Bearer YOUR_TOKEN` (with "Bearer " at the start)

---

### **Problem 2: "404 Not Found - No working proxies available"**

**What it means:** You don't have any working proxies yet.

**Solution:**
1. Add some proxies (Step 8)
2. Wait a few minutes for the system to test them
3. Or manually test a proxy (see "Test a Proxy" above)

---

### **Problem 3: "500 Internal Server Error"**

**What it means:** Something went wrong on the server.

**Solution:**
1. Check if the server is still running (Step 3)
2. If not, restart it: `./run_server.sh`
3. Try again

---

### **Problem 4: "ModuleNotFoundError" or "command not found"**

**What it means:** Python or a required package is missing.

**Solution:**
1. Make sure Python is installed:
   ```bash
   python3 --version
   ```
2. Install required packages:
   ```bash
   pip install requests httpx
   ```

---

### **Problem 5: Can't Connect to Server**

**What it means:** The server isn't running or the address is wrong.

**Solution:**
1. Check if the server is running (Step 3)
2. Make sure you're using: `http://localhost:8000/docs`
3. If still not working, restart the server

---

## 🎯 Quick Reference

### **Important URLs:**
- **API Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### **Important Commands:**
- **Start server:** `./run_server.sh`
- **Test proxy:** `python3 simple_proxy_test.py`
- **Full example:** `python3 web_scraping_with_proxy.py`

### **Important Endpoints:**
- **Register:** `POST /auth/register`
- **Login:** `POST /auth/login`
- **Get best proxy:** `GET /proxy?strategy=health_score`
- **Add proxy:** `POST /proxies`
- **List proxies:** `GET /proxies`

---

## 📚 Understanding Health Score

**Health Score (0-100)** tells you how good a proxy is:

- **90-100:** Excellent! Use this proxy for important tasks
- **70-89:** Good! Reliable for most tasks
- **50-69:** Fair! Might work, but could be slow
- **0-49:** Poor! Avoid using this proxy
- **0:** Not working! The proxy is down

**Always use `strategy=health_score` to get the best proxy!**

---

## ✅ Summary: Complete Workflow

1. ✅ **Start server** (`./run_server.sh`)
2. ✅ **Open browser** (`http://localhost:8000/docs`)
3. ✅ **Register** (first time only)
4. ✅ **Login** (get your token)
5. ✅ **Add proxies** (if you have them)
6. ✅ **Get best proxy** (`GET /proxy?strategy=health_score`)
7. ✅ **Use proxy for web scraping** (Python scripts)

---

## 🆘 Need Help?

**If something doesn't work:**

1. **Check the server** - Is it running? (Step 3)
2. **Check your token** - Did you add it correctly? (Step 7)
3. **Check the error message** - What does it say?
4. **Try the troubleshooting section** above
5. **Read the detailed guides:**
   - `WORKING_WEB_SCRAPING.md` - Complete web scraping guide
   - `DEMONSTRATION_GUIDE.md` - Step-by-step demo
   - `QUICK_START_SCRAPING.md` - Quick start

---

## 🎉 You're Ready!

You now know how to:
- ✅ Start the software
- ✅ Create an account
- ✅ Login and get your token
- ✅ Add proxies
- ✅ Get the best proxy by health score
- ✅ Use proxies for web scraping

**Happy scraping! 🕷️**

---

**Last Updated:** This guide covers all the basics. For advanced features, see the other documentation files.

