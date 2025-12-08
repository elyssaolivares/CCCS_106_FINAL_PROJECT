# FIXIT - System Architecture

## Project Overview

**FIXIT** (Faculty Issue eXchange and Information Tracker) is a cross-platform maintenance reporting system that enables students, faculty, and staff to report facility concerns digitally. The system features AI-powered categorization using Multinomial Naive Bayes classification and provides administrators with centralized report management and activity monitoring.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (Flet UI)                           │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  main.py - Application Entry Point                              │   │
│  │  ├── homepage.py          (Welcome/Landing Page)                │   │
│  │  ├── loginpage.py         (Authentication UI)                   │   │
│  │  │                                                              │   │
│  │  ├── userdashboard.py     (Legacy User Dashboard)               │   │
│  │  ├── admin_dashboard.py   (Legacy Admin Dashboard)              │   │
│  │  │                                                              │   │
│  │  └── dashboard/           (New Dashboard Structure)             │   │
│  │      ├── user_dashboard.py          (User Main View)            │   │
│  │      ├── account_page.py            (User Profile)              │   │
│  │      ├── report_issue_page.py       (Report Submission Form)    │   │
│  │      ├── report_card.py             (Report Display Widget)     │   │
│  │      ├── report_statistics.py       (Report Analytics)          │   │
│  │      ├── navigation_drawer.py       (Menu Navigation)           │   │
│  │      ├── dashboard_ui.py            (UI Components)             │   │
│  │      │                                                          │   │
│  │      └── admin/                     (Admin-Only Views)          │   │
│  │          ├── admin_dashboard.py         (Admin Home)            │   │
│  │          ├── admin_all_reports.py       (All Reports List)      │   │
│  │          ├── admin_all_categories.py    (Category Management)   │   │
│  │          ├── admin_category_reports.py  (Reports per Category)  │   │
│  │          ├── admin_dashboard_ui.py      (Admin UI Components)   │   │
│  │          ├── dashboard_controller.py    (Logic Controller)      │   │
│  │          ├── dashboard_data_manager.py  (Data Management)       │   │
│  │          ├── user_activity_monitoring.py (Activity Tracking)    │   │
│  │          └── audit_logs_viewer.py       (Audit Log Display)     │   │
│  │                                                                  │   │
│  └── components/                (Reusable UI Components)              │   │
│      └── session_timeout_ui.py      (Session Timeout Warning)        │   │
│                                                                       │   │
└──────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────────┐
│              SERVICES LAYER (app/services/)                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │  DATABASE SERVICE           │  │  AUTHENTICATION SERVICE         │  │
│  │  (database/)                │  │  (auth/)                        │  │
│  │                             │  │                                 │  │
│  │  database.py                │  │  admin_account.py               │  │
│  │  ├── SQLite3 Connection     │  │  └── Admin credential validation│  │
│  │  ├── CRUD Operations        │  │                                 │  │
│  │  ├── Reports Table          │  │                                 │  │
│  │  ├── Users Table            │  │                                 │  │
│  │  ├── Query Reports          │  │                                 │  │
│  │  ├── Update Status          │  │                                 │  │
│  │  └── User Management        │  │                                 │  │
│  │                             │  │                                 │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                           │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │  SESSION MANAGEMENT         │  │  ACTIVITY MONITORING            │  │
│  │  (session/)                 │  │  (activity/)                    │  │
│  │                             │  │                                 │  │
│  │  session_manager.py         │  │  activity_monitor.py            │  │
│  │  ├── Create Session         │  │  ├── Log Login Attempts         │  │
│  │  ├── Validate Session       │  │  ├── Track User Actions         │  │
│  │  ├── Session Timeout        │  │  ├── Monitor Activity           │  │
│  │  ├── Refresh Tokens         │  │  ├── Report Submissions         │  │
│  │  ├── SessionConfig          │  │  └── Admin Activities           │  │
│  │  ├── SessionInfo Storage    │  │                                 │  │
│  │  └── Timeout Callbacks      │  │                                 │  │
│  │                             │  │                                 │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                           │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │  AI/ML CATEGORIZATION       │  │  GOOGLE OAUTH                   │  │
│  │  (ai/)                      │  │  (google/)                      │  │
│  │                             │  │                                 │  │
│  │  ai_services.py             │  │  google_auth.py                 │  │
│  │  ├── Load & Train Model     │  │  ├── OAuth 2.0 Flow             │  │
│  │  ├── Multinomial Naive Bayes│  │  ├── Redirect Handler           │  │
│  │  ├── Predict Categories     │  │  ├── Token Exchange             │  │
│  │  ├── CV Vectorizer          │  │  ├── User Info Retrieval        │  │
│  │  ├── dataset.csv (training) │  │  ├── CSPC Email Validation      │  │
│  │  └── Text Preprocessing     │  │  └── client_secret.json         │  │
│  │                             │  │                                 │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  AUDIT LOGGING                                                  │   │
│  │  (audit/)                                                       │   │
│  │                                                                 │   │
│  │  audit_logger.py                                               │   │
│  │  ├── Log User Actions                                          │   │
│  │  ├── Log Report Changes                                        │   │
│  │  ├── Track Admin Operations                                    │   │
│  │  ├── Generate Audit Trails                                     │   │
│  │  └── Timestamp All Events                                      │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SQLite3 Database (app_database.db)                             │   │
│  │                                                                  │   │
│  │  Tables:                                                         │   │
│  │  ├── reports                                                     │   │
│  │  │   ├── id (PRIMARY KEY)                                       │   │
│  │  │   ├── user_email, user_name, user_type                       │   │
│  │  │   ├── issue_description, location, category, status          │   │
│  │  │                                                               │   │
│  │  └── users                                                       │   │
│  │      ├── id, email (UNIQUE), name, role, profile_picture        │   │
│  │      ├── password_hash, created_at, updated_at                  │   │
│  │                                                                  │   │
│  │  ├── audit logs (via audit_logger.py)                           │   │
│  │  └── activity logs (via activity_monitor.py)                    │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  File Storage                                                    │   │
│  │                                                                  │   │
│  │  assets/                                                         │   │
│  │  └── fonts/              (Custom Poppins font family)           │   │
│  │                                                                  │   │
│  │  storage/                                                        │   │
│  │  ├── data/               (Persistent data files)                │   │
│  │  └── temp/               (Temporary data)                       │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - Authentication Flow

```
┌──────────────┐
│   User       │
└──────┬───────┘
       │
       ├─ Option 1: Admin Login (Email + Password)
       │  │
       │  ↓
       │  ┌──────────────────┐
       │  │ loginpage.py     │
       │  │ • Get credentials│
       │  └────────┬─────────┘
       │           │
       │           ↓
       │  ┌────────────────────────────┐
       │  │ admin_account.py           │
       │  │ • Hash password            │
       │  │ • Compare with stored hash │
       │  └────────┬───────────────────┘
       │           │
       │           ↓ (Success/Failure)
       │
       └─ Option 2: OAuth (Google - CSPC Email)
          │
          ↓
          ┌──────────────────────────┐
          │ google_auth.py           │
          │ • Open Google OAuth flow │
          │ • Get auth code          │
          │ • Exchange for token     │
          │ • Get user info          │
          │ • Validate @my.cspc.edu.ph
          └────────┬─────────────────┘
                   │
                   ↓
┌────────────────────────────────────┐
│ Session Management                 │
│ • session_manager.py               │
│ • Create session record            │
│ • Set timeout (30min admin/60min)  │
│ • Store session info               │
└────────┬──────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ Audit Logging                      │
│ • audit_logger.py                  │
│ • Log login event                  │
│ • Timestamp & user details         │
└────────┬──────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ Load Dashboard                     │
│ • User Dashboard OR                │
│ • Admin Dashboard                  │
└────────────────────────────────────┘
```

---

## Data Flow - Report Submission

```
┌──────────────────────────────────┐
│ User Dashboard                    │
│ • report_issue_page.py            │
│ • Form Input:                     │
│   - Issue Description             │
│   - Location                      │
│   - (Category optional)           │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Validation                        │
│ • Input sanitization              │
│ • Required field check            │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ AI Categorization                 │
│ • ai_services.py                  │
│ • Vectorize description (CV)      │
│ • Predict category (Naive Bayes)  │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Database Service                  │
│ • database.py                     │
│ • db.add_report()                 │
│ • Generate ID                     │
│ • Store in reports table          │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Activity Logging                  │
│ • activity_monitor.py             │
│ • Log submission event            │
│ • Track report creation           │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Success Response                  │
│ • Show confirmation               │
│ • Display Report ID               │
│ • Update UI                       │
└──────────────────────────────────┘
```

---

## Data Flow - Admin Report Management

```
┌────────────────────────────────────┐
│ Admin Dashboard                    │
│ • admin/admin_dashboard.py         │
└──────────┬───────────────────────┘
           │
     ┌─────┴──────┬─────────┬──────────┐
     │            │         │          │
     ↓            ↓         ↓          ↓
┌─────────┐  ┌──────┐  ┌────────┐  ┌──────────┐
│ All     │  │By    │  │By      │  │Statistics│
│Reports  │  │Status│  │Category│  │Dashboard │
└────┬────┘  └──┬───┘  └───┬────┘  └─────┬────┘
     │          │          │             │
     └──────────┴──────────┴─────────────┘
                │
                ↓
     ┌──────────────────────────┐
     │ Dashboard Data Manager   │
     │ • Query database         │
     │ • Filter & sort          │
     │ • Prepare data           │
     └──────────┬───────────────┘
                │
                ↓
     ┌──────────────────────────┐
     │ Dashboard Controller     │
     │ • Process user actions   │
     │ • Update status          │
     │ • Manage UI state        │
     └──────────┬───────────────┘
                │
     ┌──────────┴─────────────┐
     │                        │
     ↓                        ↓
┌──────────────────┐  ┌──────────────────┐
│Update Report     │  │Delete Report     │
│Status:           │  │                  │
│- Pending         │  │- Remove from DB  │
│- In Progress     │  │- Log action      │
│- Resolved        │  │- Update UI       │
│- Rejected        │  │                  │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ↓
         ┌──────────────────────┐
         │ Database Update      │
         │ • database.py        │
         │ • Update reports table
         └──────────┬───────────┘
                    │
                    ↓
         ┌──────────────────────┐
         │ Audit Log            │
         │ • Log all changes    │
         │ • Record admin action│
         │ • Timestamp          │
         └──────────┬───────────┘
                    │
                    ↓
         ┌──────────────────────┐
         │ Activity Monitor     │
         │ • Track admin edits  │
         │ • Update statistics  │
         └──────────────────────┘
```

---

## Technology Stack

```
┌────────────────────────────────────────────────────┐
│            TECHNOLOGY STACK                         │
├────────────────────────────────────────────────────┤
│                                                    │
│  Frontend Framework:                               │
│  • Flet 0.28.3 - Cross-platform UI (Python)      │
│  • Material Design UI Components                  │
│  • Responsive Layout (Web, Desktop, Mobile)       │
│                                                    │
│  Backend/Logic:                                    │
│  • Python 3.x                                     │
│  • Service-Oriented Architecture                  │
│                                                    │
│  Database:                                         │
│  • SQLite3 (Local relational database)            │
│  • 2 main tables: reports, users                  │
│  • Additional audit/activity tables               │
│                                                    │
│  Authentication:                                   │
│  • Custom Admin Accounts (email + password hash) │
│  • Google OAuth 2.0 (CSPC email validation)      │
│  • Session Management (timeout-based)             │
│                                                    │
│  AI/ML:                                            │
│  • scikit-learn 1.7.2 - ML library               │
│  • Multinomial Naive Bayes - Text classification │
│  • CountVectorizer - Text feature extraction     │
│  • Pandas 2.3.3 - Data processing                │
│                                                    │
│  External Services:                                │
│  • Google OAuth 2.0                              │
│  • CSPC Email domain validation                  │
│                                                    │
│  Key Dependencies:                                 │
│  • flet==0.28.3                                  │
│  • google-auth==2.41.1                           │
│  • google-auth-oauthlib==1.2.3                   │
│  • requests==2.32.5                              │
│  • scikit-learn==1.7.2                           │
│  • pandas==2.3.3                                 │
│  • python-dotenv==1.2.1                          │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│          SECURITY IMPLEMENTATION                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Layer 1: Input Validation                          │
│  ├── HTML/Script injection prevention              │
│  ├── Email format validation                       │
│  ├── Text preprocessing (AI model)                 │
│  └── Required field validation                     │
│                                                     │
│  Layer 2: Authentication                            │
│  ├── Admin credentials:                            │
│  │   • Email validation                            │
│  │   • SHA-256 password hashing                    │
│  │   • Stored hash comparison                      │
│  │                                                 │
│  └── OAuth 2.0:                                    │
│      • Google OAuth flow                          │
│      • CSPC email domain validation (@my.cspc)    │
│      • Token-based authentication                 │
│                                                     │
│  Layer 3: Session Management                       │
│  ├── SessionConfig:                                │
│  │   • Admin timeout: 30 minutes                   │
│  │   • User timeout: 60 minutes                    │
│  │   • Inactivity tracking                         │
│  │   • Automatic session expiry                    │
│  │                                                 │
│  └── SessionInfo:                                  │
│      • Per-user session storage                    │
│      • Activity timestamp tracking                 │
│      • Session state management                    │
│                                                     │
│  Layer 4: Authorization                            │
│  ├── Role-based access (admin vs user)            │
│  ├── Admin-only views protected                    │
│  ├── Dashboard access control                      │
│  └── Report visibility by role                     │
│                                                     │
│  Layer 5: Audit & Monitoring                        │
│  ├── Comprehensive audit logging:                  │
│  │   • All user logins                            │
│  │   • Report submissions                         │
│  │   • Admin status changes                       │
│  │   • Deletion operations                        │
│  │                                                 │
│  └── Activity monitoring:                          │
│      • Track user actions                         │
│      • Monitor admin operations                   │
│      • Generate activity reports                  │
│                                                     │
│  Layer 6: Data Protection                          │
│  ├── Password hashing (SHA-256)                   │
│  ├── Database file permissions                    │
│  ├── Secure OAuth token handling                  │
│  └── Sensitive data in .env (not committed)       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                  COMPONENT COMMUNICATION                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Views                 Services              Database           │
│  ─────                 ────────              ────────           │
│                                                                 │
│  loginpage         ←→  google_auth      ←→  SQLite3            │
│                   ←→  admin_account                            │
│                   ←→  session_manager                          │
│                                                                 │
│  user_dashboard    ←→  database         ←→  reports table      │
│                   ←→  activity_monitor  ←→  activity logs      │
│                   ←→  ai_services                              │
│                                                                 │
│  report_issue_page ←→  ai_services      ←→  dataset.csv        │
│                   ←→  database          ←→  reports table      │
│                   ←→  activity_monitor                         │
│                                                                 │
│  admin_dashboard  ←→  database          ←→  reports table      │
│                   ←→  session_manager                          │
│                   ←→  activity_monitor  ←→  activity logs      │
│                   ←→  audit_logger      ←→  audit logs         │
│                                                                 │
│  admin modules    ←→  dashboard_data_mgr ←→ Database queries   │
│                   ←→  dashboard_controller                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Project File Structure

```
CCCS_106_FINAL_PROJECT/
│
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── SYSTEM_ARCHITECTURE.md            # This file
│
├── app/
│   ├── views/                        # Presentation Layer (Flet UI)
│   │   ├── homepage.py               # Landing page
│   │   ├── loginpage.py              # Authentication UI
│   │   ├── userdashboard.py          # Legacy user dashboard
│   │   ├── admin_dashboard.py        # Legacy admin dashboard
│   │   │
│   │   ├── dashboard/                # New Dashboard Structure
│   │   │   ├── user_dashboard.py     # User main interface
│   │   │   ├── account_page.py       # User profile page
│   │   │   ├── report_issue_page.py  # Report submission form
│   │   │   ├── report_card.py        # Report display widget
│   │   │   ├── report_statistics.py  # Analytics view
│   │   │   ├── navigation_drawer.py  # Menu navigation
│   │   │   ├── dashboard_ui.py       # Shared UI components
│   │   │   │
│   │   │   └── admin/                # Admin-only pages
│   │   │       ├── admin_dashboard.py         # Admin home
│   │   │       ├── admin_all_reports.py       # All reports view
│   │   │       ├── admin_all_categories.py    # Categories view
│   │   │       ├── admin_category_reports.py  # Category details
│   │   │       ├── admin_dashboard_ui.py      # Admin UI components
│   │   │       ├── dashboard_controller.py    # Admin logic handler
│   │   │       ├── dashboard_data_manager.py  # Data fetching
│   │   │       ├── user_activity_monitoring.py # Activity viewer
│   │   │       └── audit_logs_viewer.py       # Audit log display
│   │   │
│   │   └── components/               # Reusable UI Components
│   │       └── session_timeout_ui.py # Inactivity warning popup
│   │
│   └── services/                     # Business Logic Layer
│       ├── database/
│       │   └── database.py           # SQLite3 CRUD operations
│       │
│       ├── session/
│       │   └── session_manager.py    # Session management & timeout
│       │
│       ├── auth/
│       │   └── admin_account.py      # Admin credential validation
│       │
│       ├── google/
│       │   ├── google_auth.py        # Google OAuth 2.0 flow
│       │   └── client_secret.json    # OAuth credentials
│       │
│       ├── ai/
│       │   ├── ai_services.py        # Naive Bayes classifier
│       │   └── dataset.csv           # Training data
│       │
│       ├── activity/
│       │   └── activity_monitor.py   # Activity logging
│       │
│       └── audit/
│           └── audit_logger.py       # Audit trail logging
│
├── assets/                           # Static Assets
│   └── fonts/
│       ├── Poppins-Regular.ttf
│       ├── Poppins-Bold.ttf
│       ├── Poppins-SemiBold.ttf
│       ├── Poppins-Medium.ttf
│       └── Poppins-Light.ttf
│
└── storage/                          # Local Storage
    ├── data/                         # Persistent data
    └── temp/                         # Temporary files
```

---

## Key Features & Implementation

### 1. **Report Management**
- Users submit issues with description and location
- AI automatically categorizes using Naive Bayes
- Admins can view, filter, update status, and delete reports
- Full audit trail of all changes

### 2. **User Authentication**
- Admin login with email + password (hashed)
- Google OAuth 2.0 for students/faculty (CSPC email validation)
- Session timeout (30 min admin, 60 min user)
- Inactivity warnings before expiry

### 3. **Admin Dashboard**
- View all reports with filtering
- Filter by status (pending/in progress/resolved/rejected)
- View reports by category
- User activity monitoring
- Audit log viewer
- Report statistics

### 4. **AI Categorization**
- Text preprocessing of issue descriptions
- Multinomial Naive Bayes classifier
- CountVectorizer for feature extraction
- Real-time category prediction

### 5. **Activity Tracking**
- Login/logout events
- Report submissions
- Admin actions (status changes, deletions)
- Timestamps on all events
- Searchable audit logs

### 6. **Cross-Platform Support**
- Single Flet codebase
- Web browser deployment
- Desktop application
- Mobile-responsive UI

---

## Data Model

### Reports Table
```
id              INTEGER PRIMARY KEY
user_email      TEXT (NOT NULL)
user_name       TEXT (NOT NULL)
user_type       TEXT (admin/student/faculty)
issue_description TEXT
location        TEXT
category        TEXT (AI-predicted)
status          TEXT (pending/in progress/resolved/rejected)
```

### Users Table
```
id              INTEGER PRIMARY KEY
email           TEXT UNIQUE (NOT NULL)
name            TEXT
role            TEXT
profile_picture TEXT
password_hash   TEXT (SHA-256)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

---

This architecture provides:
- ✅ **Scalability** - Modular service design
- ✅ **Security** - Multi-layer protection (auth, validation, audit)
- ✅ **Maintainability** - Clear separation of concerns
- ✅ **Cross-Platform** - Single Flet codebase
- ✅ **Audit Trail** - Complete activity logging
- ✅ **User Experience** - Responsive Material Design UI
- ✅ **AI Integration** - Intelligent categorization
