# <center>Installation and Setup Guide Manual

## <center> FIXIT (Faculty Issue eXchange and Information Tracker)

### Step 1 : Clone or Extract the Repository

Open your terminal or command prompt and navigate to the project folder.

#### Project Complete File Directory

This is the completed application requirements before running the application.


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
├── .env.example
├──.gitignore
├── README.MD
├── audit_logs_20251208_055858.csv
├── integrate_audit_logging.py
├── main.py
├── requirements.txt
└── verify_db.py

```

#### The .gitignore File

This is to check what are the hidden inclusions in the project deliverables.


```.gitignore

# Virtual environment
venv/

# Python cache files
__pycache__/
*.pyc

# Environment variables / secrets
.env
client_secret.json

# Database files
*.db
*.sqlite3
```

### Step 2: Prerequisites 
Flet is a Python framework, so the only strict requirement is having Python installed on your computer.

#### Check for Python

Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux) and type:

```bash
python --version
```

If you see a version number (e.g., Python 3.10.x): You are good to go! Ensure it is Python 3.8 or newer.

If you get an error: You need to install Python.

#### Install Python (If needed)

Go to python.org/downloads.

Download the installer for your operating system.

Important: During installation, check the box that says "Add Python to PATH". This ensures you can run Python commands from any terminal window.

#### Installing Flet

Once Python is set up, installing Flet is simple using pip, Python's package manager.

Open your terminal or command prompt.

Run the following command:


```bash
pip install flet
```

Note: If you are on macOS or Linux and the command fails, try using pip3 install flet instead.

Wait for the installation to complete. You should see a generic "Successfully installed" message at the end.


### Step 3: Create a Virtual Environment (Recommended) 
It is best practice to isolate project dependencies.


```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```
### Step 4: Install Dependencies 

Install the required Flet and Python libraries using the provided requirements file.

```bash
pip install -r requirements.txt
```

### Step 5: Environment Configuration 

The application requires Google credentials to function.

Locate the file named .env.example in the root directory. Rename it to .env. Open .env in a text editor (Notepad, VS Code) and add your credentials:

```.env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
SECRET_KEY=your_random_secret_string
```
### Step 5: Initialize the Database & Audit Logs 

Ensure the local CSV files exist.


```bash
# This script (if you have one, or run main once) initializes the necessary files
python verify_db.py
```

## Running the Application

To start the Flet application in desktop mode (or web view depending on configuration):


```bash
# Standard run command
python main.py
```
Alternatively, if running in Flet development mode with hot-reload:

```bash
flet run main.py
# or
flet run

```



