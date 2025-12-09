

# <center>FIXIT User Manual

**Faculty Issue eXchange and Information Tracker**

**Team CodeCrew³**

---


FIXIT is a centralized platform designed to streamline the reporting and tracking of campus facility issues. This manual guides users through the process of logging in, submitting reports, and managing facility issues based on their assigned role.

---

## **Part I: Student & Faculty Guide (Regular User)**

### **1.1 Getting Started**
**System Requirements:**
- A device (Laptop/Smartphone) with an active internet connection.
- A valid **Institutional Google Account** (e.g., `@cspc.edu.ph`).

### **1.2 Logging In**

1. Launch the FIXIT application.
2. Click the **"Get Started"** button to proceed.
3. On the Log in Page, chose from the user roles and click the **"Login with Google"** button.
 
    > **Note:** The user can manually add email and password if their accounts are registered in the system.
4. A browser window will open. Enter your CSPC Google credentials.
5. Upon successful verification, the application will redirect you to the **User Dashboard**.

> **Note:** If you use a non-institutional email, access will be denied.

### **1.3 The User Dashboard**
The Dashboard is your home screen. It displays:
* **Navigation Menu:** (Top Left) Access to Profile and Settings.
* **Report History:** A list of all maintenance requests you have submitted.
* **Status Tabs:** Switch between **Pending**, **On-Going**, and **Completed** to filter your reports.
* **Create Button:** A floating **(+)** button (or "New Report" button) to start a new submission.

### **1.4 Submitting a Maintenance Report**
1.  Click the **(+)** button or select **"Report Issue"** from the menu.
2.  **Location:** Enter the specific room number, building, or landmark (e.g., *"CCS Computer Lab 2"*).
3.  **Description:** Briefly describe the problem (e.g., *"The air conditioner is leaking water"*).
    > *Note: You do NOT need to select a category. The system’s AI will automatically classify it (e.g., as "Plumbing") based on your description.*
4.  Click **Submit**.
5.  A confirmation message will appear, and you will be returned to your Dashboard.

### **1.5 Tracking Your Reports**
* **Pending:** The report has been sent but not yet acknowledged by Admin.
* **On-Going:** Admin has assigned a maintenance crew to the issue.
* **Fixed:** The issue has been resolved.
* **Rejected:** The report was marked as invalid (check comments for details).

---

## **Part II: Administrator Guide**

### **2.1 Admin Access**
* Log in using the same **"Login with Google"** button as regular users.
* The system automatically detects your **Admin privileges** and routes you to the **Admin Console** instead of the User Dashboard.

### **2.2 Admin Dashboard Overview**
The Admin Console provides a high-level view of campus maintenance:
* **Statistics Cards:** Real-time counts of Total Reports, Pending Issues, and Completed Repairs.
* **Master List:** A searchable list of all reports submitted by all students and faculty.
* **Filter Tools:** Sort reports by **Category** (Electrical, Plumbing, IT) or **Status**.

### **2.3 Managing Reports**
To update the status of an issue:
1.  Locate the report in the Master List.
2.  Click the **"Update Status"** (Pencil Icon) button next to the report.
3.  Select the new status:
    * **Mark as On-Going:** When maintenance staff have been deployed.
    * **Mark as Fixed:** When the repair is verified as complete.
    * **Reject:** If the report is a duplicate or invalid.
4.  The change is saved immediately and reflects on the Student's dashboard.

### **2.4 User Activity Monitoring**
For security oversight, navigate to the **Activity Monitor** tab:
* **Active Users:** View who is currently logged into the system.
* **Recent Actions:** See a timeline of recent login attempts and report submissions.
* **Session Control:** (If implemented) Manually revoke a user's session if suspicious activity is detected.

### **2.5 Viewing Audit Logs**
To perform a security audit:
1.  Open the sidebar and select **"Audit Logs"**.
2.  The system will display a table of logged events (stored in CSV).
3.  Columns include:
    * **Timestamp:** Exact date and time.
    * **User:** Email of the actor.
    * **Action:** (e.g., `LOGIN_SUCCESS`, `STATUS_UPDATE`, `REPORT_CREATED`).
    * **IP Address:** Origin of the request.

---

## **3. Troubleshooting**

| **Issue** | **Possible Cause** | **Solution** |
| :--- | :--- | :--- |
| **"Login Failed"** | Using personal Gmail. | Retry using your official School Email. |
| **"Network Error"** | No Internet connection. | Connect to Wi-Fi/Data. The app requires internet for Google Auth. |
| **"Session Expired"** | Inactivity timeout. | The system auto-logs out after 5 mins of idleness. Please log in again. |
| **"Wrong Category"** | AI misclassification. | The AI interprets your text. Admins can manually correct the category in the dashboard. |

---

## **4. Safety & Privacy**
* **Automatic Logout:** Do not leave your device unattended. The system will auto-lock after 5 minutes.
* **Data Usage:** Your profile name and email are used solely for identification. No personal files are accessed.