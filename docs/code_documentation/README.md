# <center>FIXIT: Faculty Issue eXchange and Information Tracker

**Team:** CodeCrew³

FIXIT is a web-based maintenance reporting application built with **Flet (Python)**. It streamlines campus facility management by allowing students and faculty to report issues which are automatically categorized by AI, while providing administrators with real-time dashboards and security monitoring.

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Console Credentials (Client ID & Secret)

### Installation

1.  **Clone the Repository**

    ```bash
    git clone [https://github.com/your-repo/CCCS_106_FINAL_PROJECT.git](https://github.com/your-repo/CCCS_106_FINAL_PROJECT.git)
    cd CCCS_106_FINAL_PROJECT
    ```

2.  **Set Up Virtual Environment**

    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Rename `.env.example` to `.env` and add your keys:

    ```ini
    GOOGLE_CLIENT_ID=your_client_id
    GOOGLE_CLIENT_SECRET=your_client_secret
    SECRET_KEY=your_flask_secret_key
    ```

5.  **Run the App**
    ```bash
    flet run main.py
    ```

---

## Features List

### Core Functionality

- **Role-Based Access:** Distinct interfaces for **Admins** (Management) and **Users** (Reporting).
- **Google OAuth 2.0:** Secure, password-less login using institutional Google accounts.
- **Maintenance Reporting:** Intuitive form for submitting issues with location data.
- **Real-time Dashboards:** Visual status tracking (Pending, On-going, Fixed).

### Chosen Enhancements (Advanced Features)

- **AI-Powered Categorization:**
  - Uses a supervised learning model (Naive Bayes) to analyze report descriptions.
  - Automatically tags issues (e.g., "Leaky faucet" → _Plumbing_) to reduce admin workload.
- **Automated Audit Logging:**
  - Tracks all critical actions (Logins, Updates, Submissions) in immutable CSV logs (`audit_logs_YYYY.csv`).
- **Session Security:**
  - Includes an **Activity Monitor** that tracks user interaction.
  - Auto-locks sessions after inactivity to protect data on shared devices.
- **User Activity Monitoring:**
  - Admin view to see active users and recent system interactions.

---

## Project Structure

```bash
CCCS_106_FINAL_PROJECT/
├── app/
|   ├── services
|   |   ├──activity/
|   |   |  ├──__init.py_
|   |   |  └──activity_monitor.py
|   |   ├──ai/
|   |   |  ├──ai_services.py
|   |   |  └──dataset.csv
|   |   ├──audit/
|   |   |  └──audit_logger.py
|   |   ├──auth/
|   |   |  └──admin_account.py
|   |   ├──database/
|   |   |  └──database.py
|   |   ├──google/
|   |   |  └──google_auth.py
|   |   └──session/
|   |      ├──__init__.py
|   |      └──session_manager.py
|   └──views/
|      ├──components/
|      |  ├──__init__.py
|      |  └──session_timeout_ui.py
|      ├──dashboard/
|      |  ├──admin
|      |  |  ├──admin_all_categories.py
|      |  |  ├──admin_all_reports.py
|      |  |  ├──admin_category_reports.py
|      |  |  ├──admin_dashboard.py
|      |  |  ├──admin_dashboard_ui.py
|      |  |  ├──dashboard_controller.py
|      |  |  ├──audit_logs_viewer.py
|      |  |  ├──dashboard_data_manager.py
|      |  |  └──user_activity_monitoring.py
|      |  ├──account_page.py
|      |  ├──dashboard_ui.py
|      |  ├──navigation_drawer.py
|      |  ├──report_card.py
|      |  ├──report_issue_page.py
|      |  ├──report_statistics.py
|      |  ├──session_manager.py
|      |  └──user_dashboard.py
|      ├──report_issue_page.py
|      ├──report_statistics.py
|      ├──session_manager.py
|      └──user_dashboard.py
├── assets/
|   ├──fonts/
|   |  ├──Poppins-Bold.ttf
|   |  ├──Poppins-Light.ttf
|   |  ├──Poppins-Medium.ttf
|   |  ├──Poppins-Regular.ttf
|   |  └──Poppins-SemiBold.ttf
|   └──cspc_logo.png
├──docs/
├── .env.example
├──.gitignore
├── README.MD
├── audit_logs_20251208_055858.csv
├── integrate_audit_logging.py
├── main.py
├── requirements.txt
└── verify_db.py

```
