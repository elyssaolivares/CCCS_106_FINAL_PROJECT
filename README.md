#  FINAL PROJECT
Course: **CCCS 106 - Application Development and Emerging Technologies** <br>
Joint Collaboration: **CS 319 - Information Assurance and Security <br>**
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**CS 3110 - Software Engineering 1 <br>** 
Project Title: **Emerging Tech Flet Framework**<br>
Assessment Type: **Project & Final Examination Equivalent**                   
Term: **Academic Year 2025-2026 - Finals**

# FIXIT - Faculty Issue eXcahange and Information Tracker

## Project Overview 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;To address these challenges, the FIXIT (Faculty Issue eXchange and Information Tracker) introduces a mobile, web, and desktop-based maintenance reporting system that mitigates issue submissions, tracking, and administrative processing. This system enables students, faculty, and staff to conveniently report facility concerns with the use of a standardized digital platform supported by AI-powered categorization feature using NLP-trained Multimonial Naive Bayes Classification model. These allow administrators to efficiently review, edit, and assign issue statuses via a centralized dashboard that is reinforced with analytics, audit logs, and role-based authentication. <br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In order to guarantee the system's continuous usability, FIXIT improves response time, increases transparency, lowers errors, and offers campus stakeholders a dependable tool for upholding a safer and more efficient campus environment by substituting the demanding manual process with a secure and digital-based platform.


## Problem Statement
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The current campus maintenance reporting process involves actual face-to-face reports and sometimes rely on more paper-based forms submitted to the services departments. This manual workflow is so slow, lacks transparency, and prone to human errors. The kind of issues such as illegible handwriting, delayed processing, misplaced forms, and inconsistent documentation between users and maintenance staff. Faculty, students and personnel noticeably do not have reliable ways of tracking their submitted requests status, as administrators also struggle in managing reports efficiently due to absence of a centralized system. As the number of maintenance concerns and reports arise, the institution must require a more efficient, intelligent, and accessible solution for improving the campus service quality and timely repairs. 


## Feature List
The FIXIT system implements a comprehensive set of features divided by user role and system function:

#### 1. Core User Features (Students/Faculty)

- **Secure Authentication**: Google OAuth 2.0 integration allows users to log in securely using their institutional email accounts without managing local passwords.

- **Maintenance Reporting**: A streamlined interface to submit issues containing descriptions and specific location details.

- **Real-time Status Tracking**: Users can view a personal dashboard showing the status of their reports (Pending, On-going, Fixed, Rejected).

#### 2. Administrative Features

- **Centralized Dashboard**: A high-level view of all campus issues with filtering capabilities (by status or category).

- **Status Management**: Admins can update the lifecycle state of a report (e.g., marking a "Pending" issue as "On-going").

- **User Activity Monitoring**: A dedicated view to track active users and recent system interactions.

- **Audit Log Viewer**: An interface to review the CSV-based security logs for compliance and accountability.

### 3. Intelligent & Security Features

- **AI-Powered Categorization**: Utilizes a Multinomial Naive Bayes model to automatically classify report descriptions (e.g., "leaking pipe" → Plumbing).

- **Automated Audit Logging**: Critical actions (logins, submissions, updates) are recorded in immutable CSV files.

- **Session Security**: Includes an inactivity monitor that automatically logs users out after a set period to prevent unauthorized access on shared devices.

## Architecture Diagram
The system follows a Modular Monolithic Architecture layered over a Service-Oriented Design.

Access the System's Architecture Diagram through : https://mdeditor.net/docs/5d31eda6bcb5dd933a83b704c8d1c173 

**1. Presentation Layer (Client)**: Built entirely with Flet (Python), providing a reactive UI that runs on Desktop, Web, and Mobile from a single codebase.

**2. Business Logic Layer (Services)**: Distinct Python modules handle specific domains:

- ai_services.py: Handles ML inference.

- google_auth.py: Manages OAuth tokens.

- audit_logger.py: Writes security logs.

**3. Data Layer**:

- **Primary Storage**: Database (SQLite/Firestore) for User and Report data.

- **Security Storage**: Flat-file CSV storage for Audit Logs (ensuring separation of concerns).


## Data Model
The data model is designed to support security and traceability:

<img width="512" height="348" alt="Screenshot 2025-12-10 at 6 56 50 AM" src="https://github.com/user-attachments/assets/fe694572-d1a0-497a-8107-29903514f28f" />

**Users**: Stores Google Profile data (Email, Name) and Role (Admin/User). Note: Passwords are not stored locally, complying with modern security standards.

**Reports**: Links Users to Issues. Contains fields for Location, Description, AI_Category, Status, and Timestamp.

**Audit_Logs**: A separate entity (stored as CSV) capturing User_ID, Action_Type, IP_Address, and Timestamp for forensic analysis.

**Activity_Session**s: Tracks login tokens and expiration times to enforce session timeouts.

## Emerging Tech Explanation

### Technologies Used

- **Python 3.11+**- The core programming language used for backend logic, AI modeling, and UI definition.

- **Flet 0.28.3** - A server-driven UI framework that allows building real-time web, mobile, and desktop apps in Python. It is an "emerging tech" because it bridges the gap between backend developers and frontend UI without requiring JavaScript/Flutter knowledge.

- **Scikit-Learn (AI)** - Used to implement the Multinomial Naive Bayes classifier for Natural Language Processing (NLP).

- **Google Identity Services (OAuth 2.0)**- A standard for "Federated Identity," allowing the app to offload credential security to Google.

- **Git & GitHub**- Version control and collaboration.

- **VS Code** - Integrated development environment.

### Development Environment

- **Virtual Environment**

- **Python Packages**: flet==0.28.3, google-auth, pandas, scikit-learn

- **Platform**: Windows / macOS / Linux (Cross-Platform compatibility via Flet)

### Prerequisites

1. Python 3.8+ installed

2. Virtual environment activated: cccs106_env\Scripts\activate

3. Flet installed: pip install flet==0.28.3

4. Google Cloud Credentials configured in .env file.

## Set Up and Run Instruction

### User Manuals

Access the systems' setup and run manual through: https://mdeditor.net/docs/272797ea54e7cc8e458a146e27ba3bf5

Access the Admin User vs Regular User Capabilities through: 
https://mdeditor.net/docs/bbda85b7264f7e5e2d626ad181b20afd

## Testing Summary

Acces the Testing Summary through: https://mdeditor.net/docs/594669ea8f4b32c37355ee637d8da8fc

## Team Roles & Contribution



## Risk, Constraint Notes, & Future Enhancements

#### Constraints

- Must utilize Google OAuth that users are required to have valid CSPC emails.
- The app must run on desktop and mobile devices.
- Reports and user information must be stored securely in the database.
- The application requires an active internet connection for Google Authentication.
- Development must be completed using the Flet framework.
- The system must categorize submitted issues using NLP and the trained model.

#### Future Enhancements

- **Model improvements**: Replace or augment Naive Bayes with a small, fine-tuned Transformer or embed semantic search (embedding + kNN) for better categorization, plus a safe retraining pipeline.
- **Offline Mode** : Implement local caching for report drafting and a background sync worker.
- **Production authentication**: Replace hard-coded admin credentials with server-managed accounts (hashed passwords), and SSO enforcement with a managed identity provider.
- **Push notifications**: Real-time updates to users when status changes (via FCM/APNs).
- **Role management**: Fine-grained RBAC for multiple admin/maintenance roles (triage staff, technicians).
- **Reporting & analytics**: Exportable reports, maintenance KPIs, SLA tracking, and workload balancing.
- **Stronger local data encryption**: Protect offline cache with device-backed encryption keys.
- **Automated testing & CI/CD**: Add unit/integration tests, pipeline for model validation, and continuous deployment.


### Individual Reflection
