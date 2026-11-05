# 🚀 Techie Park

> **Find your coding buddies, build crazy projects, and turn those "Bro, we should build this!" moments into reality.**

Techie Park is a platform designed for tech students who find it difficult to search for compatible teammates for hackathons or collaborative side projects (Frontend, Backend, ML, etc.).

---

## 🎨 Design System & Color Palette

Built using GitHub Dark-mode color scheme:
- **Main Background**: `#0D1117`
- **Secondary Background**: `#161B22` (Cards, panels, sidebars)
- **Elevated Surface**: `#21262D`
- **Border**: `#30363D`
- **Primary Text**: `#E6EDF3`
- **Secondary Text**: `#8B949E`
- **Muted Text**: `#6E7681`
- **Accent Blue**: `#58A6FF`
- **GitHub Green**: `#3FB950`
- **Danger Red**: `#F85149`
- **Warning Yellow**: `#D29922`
- **Purple**: `#A371F7`

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: FastAPI (Python async REST API)
- **Database**: MySQL (with PyMySQL & connection pooling)
- **Auth**: JWT (JSON Web Tokens), bcrypt password hashing, Google OAuth

---

## 📂 Project Structure

```
TechiePark/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py         # App & environment configuration
│   │   ├── database.py       # MySQL connection & queries (with auto-table setup)
│   │   ├── security.py       # bcrypt hashing & JWT token generation
│   │   ├── schemas.py        # Pydantic models for validation
│   │   ├── main.py           # FastAPI entrypoint & static frontend server
│   │   └── routers/
│   │       └── auth.py       # Register, Login, Google OAuth, /me routes
│   └── init_db.py            # Standalone database initialization script
├── frontend/
│   ├── index.html            # Main landing & Login/Sign-up page
│   ├── css/
│   │   └── style.css         # GitHub Dark theme design system
│   └── js/
│       └── auth.js           # Interactive form switching & API integration
├── schema.sql                # Complete MySQL DDL schema
├── start.bat                 # One-click Windows startup script
├── .env                      # Active environment configuration
├── .env.example              # Template environment configuration
└── requirements.txt          # Python dependencies
```

---

## ⚡ Quick Start

### 1. Configure MySQL Database
Edit the `.env` file in the project root:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_NAME=techiepark
```

### 2. Initialize Database Tables
Run the database setup script to create the `techiepark` database and required tables:
```bash
.\.venv\Scripts\python.exe backend/init_db.py
```
*(Or import `schema.sql` into MySQL Workbench).*

### 3. Run the Application
Double-click `start.bat` or run:
```bash
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**
* Interactive API Documentation (Swagger UI): **`http://127.0.0.1:8000/docs`**

