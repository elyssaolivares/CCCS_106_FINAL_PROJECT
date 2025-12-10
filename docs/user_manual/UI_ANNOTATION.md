# FIXIT Application - UI Annotation Guide

## Overview
This document provides detailed, accurate annotations of all UI components, screens, and workflows in the FIXIT application. Based on actual project implementation with Flet framework.

---

## Table of Contents
1. [Authentication Screens](#authentication-screens)
2. [User Dashboard](#user-dashboard)
3. [Report Management](#report-management)
4. [Admin Dashboard](#admin-dashboard)
5. [Audit & Monitoring](#audit--monitoring)
6. [Navigation Components](#navigation-components)
7. [Common UI Patterns](#common-ui-patterns)
8. [Color Scheme & Branding](#color-scheme--branding)

---

## Authentication Screens

### Homepage
**File:** `app/views/homepage.py`

**Purpose:** Landing page that redirects to login or dashboard based on session state

**Key Elements:**
- Logo (CSPC)
- Session validation before loading
- Automatic redirect to login if no active session
- Automatic redirect to dashboard if session exists

**User Flow:**
1. User opens application
2. Homepage checks session status
3. If authenticated → Navigate to User Dashboard
4. If not authenticated → Navigate to Login Page

---

### Login Page
**File:** `app/views/loginpage.py`

**Purpose:** User authentication with email and password

**Key Elements:**
- **Header Section**
  - Page title: "Login"
  
- **Form Section**
  - Email input field
  - Password input field
  - Login button
  - Error message display (red text if credentials invalid)
  - Login with CSPC Email
  
**User Flow:**
1. User enters email and password
2. System validates credentials against admin_account table
3. If valid → Create session, redirect to User Dashboard
4. If invalid → Display error message, remain on login page
5. Session timeout after 15 minutes of inactivity

---

## User Dashboard

### User Dashboard Main View
**File:** `app/views/userdashboard.py` & `app/views/dashboard/user_dashboard.py`

**Purpose:** Main interface for regular users to create and view reports

**Key Sections:**

#### Header
- Page title
- Menu button (right) → Opens Navigation Drawer
- Theme toggle button (optional)

#### Main Content Area

**1. Create Report Button**
- Large prominent button
- Text: "Create New Report"
- Color: Primary blue (#0A3A7A)
- Action: Navigate to Report Issue Page

**2. Reports List**
- **Report Card Component** (`report_card.py`)
  
  **Card Structure:**
  ```
  ┌─────────────────────────────────┐
  │ Location: [Location Name]       │
  │ Category: [Category]            │
  │ Status: [Status Badge]          │
  │ Created: [Date]                 │
  │ Description: [Brief text...]    │
  │                                 │
  │ [View Details]  [Delete Report] │
  └─────────────────────────────────┘
  ```
  
  **Report Card Features:**
  - Location displayed prominently
  - Category with colored badge
  - Status indicator (Pending/In Progress/Resolved)
  - Report creation date
  - Brief description preview
  - Action buttons:
    - **View Details** → Opens detailed report view
    - **Delete Report** → Shows confirmation dialog, deletes after confirmation
  - Hover effect: Subtle shadow increase
  
  **Status Badges:**
  - Pending: Yellow/Orange
  - In Progress: Blue
  - Resolved: Green
  - Rejected: Red

**3. Empty State**
- If no reports exist: Show message "No reports yet"
- Encourage user to create first report
- Display "Create New Report" button

#### Bottom Navigation/Drawer
- See [Navigation Components](#navigation-components)

---

### Report Issue Page (Create Report)
**File:** `app/views/dashboard/report_issue_page.py`

**Purpose:** Form for creating new incident reports

**Page Layout:**
```
┌─────────────────────────────────────┐
│ FIXIT    Menu Button               │
├─────────────────────────────────────┤
│                                     │
│ Create a Report                     │
│                                     │
│ [Form Section]                      │
│                                     │
└─────────────────────────────────────┘
```

**Form Fields:**

1. **Location Selection** (Required)
   - Dropdown menu
   - Populated from location database
   - Placeholder: "Select Location"
   - Default: None

2. **Category Selection** (Required)
   - Dropdown menu with categories
   - Options: Security, Maintenance, Health & Safety, etc.
   - Placeholder: "Select Category"
   - Validation: Required field

3. **Title/Subject** (Required)
   - Text input field
   - Placeholder: "Brief title of the issue"
   - Max length: 100 characters
   - Character counter display

4. **Description** (Required)
   - Multi-line text area
   - Placeholder: "Provide detailed description of the issue"
   - Max length: 500 characters
   - Character counter display

5. **Image Upload** (Optional)
   - File picker button: "Add Photo"
   - Supports: .jpg, .png, .gif
   - Max file size: 5MB
   - Preview thumbnail if image selected


**Action Buttons:**
- **Submit Report** (Primary)
  - Disabled until required fields filled
  - Shows loading indicator on click
  - Success: Toast notification + redirect to dashboard
  - Error: Display error message
  - Audit Log: Logs "Created a report"
  
- **Cancel** (Secondary)
  - Returns to User Dashboard without saving

**Validation:**
- All required fields must be filled
- Real-time validation feedback
- Error messages appear below respective fields

**Audit Logging:**
- Action Type: `report_create`
- Recorded: User email, name, report ID, location, category
- Timestamp: Automatic

---

## Admin Dashboard

### Admin Dashboard Home
**File:** `app/views/dashboard/admin/admin_dashboard.py`

**Purpose:** Overview and navigation hub for admin functions

**Page Layout:**
```
┌──────────────────────────────────────┐
│ FIXIT        Admin Dashboard  Menu   │
├──────────────────────────────────────┤
│                                      │
│ Welcome, [Admin Name]!               │
│                                      │
│ Quick Stats:                         │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│ │Total    │ │Pending  │ │Resolved │  │
│ │Reports  │ │Reports  │ │Reports  │  │
│ │  234    │ │   45    │ │   189   │  │
│ └─────────┘ └─────────┘ └─────────┘  │
│                                      │
│ [ Show All Reports Button ]          │
│                                      │
└──────────────────────────────────────┘
```

**Key Components:**

1. **Header**
   - Admin Dashboard title
   - Menu button (right)
   - Theme toggle (optional)

2. **Welcome Section**
   - Greeting: "Welcome, [Admin Name]!"
   - Quick summary text

3. **Statistics Cards**
   - **Total Reports Card**
     - Number of all reports in system
     - Color: Blue background
   
   - **Pending Reports Card**
     - Count of pending status reports
     - Color: Orange background
   
   - **Resolved Reports Card**
     - Count of resolved status reports
     - Color: Green background

4. **Action Area**
   - **Show All Reports Button**
     - Primary action
     - Navigates to "All Reports" view
     - Shows comprehensive report list with filters

5. **Navigation Drawer** (Accessed via Menu Button)
   - See [Navigation Components](#navigation-components)

---

### All Reports View
**File:** `app/views/dashboard/admin/admin_all_reports.py`

**Purpose:** Comprehensive view of all reports with filtering and management

**Page Layout:**
```
┌─────────────────────────────────┐
│ FIXIT    All Reports      Menu   │
├─────────────────────────────────┤
│ [Filters]                       │
│                                 │
│ ┌──────────────────────────────┐│
│ │ Report 1                      ││
│ ├──────────────────────────────┤│
│ │ Location | Category | Status ││
│ │ [Details]               [>]  ││
│ └──────────────────────────────┘│
│ ┌──────────────────────────────┐│
│ │ Report 2                      ││
│ │ ...                           ││
│ └──────────────────────────────┘│
│                                 │
└─────────────────────────────────┘
```

**Filter Options:**
- **Status Filter**: All / Pending / In Progress / Resolved / Rejected
- **Category Filter**: Dropdown with all categories
- **Date Range**: From date to date picker
- **Sort Options**: By date, by status, by category

**Report List Display:**
- **Report Item**
  - Location (bold)
  - Category badge
  - Status badge (color-coded)
  - Creation date
  - Click to expand details
  - Arrow icon indicates expandable

**Report Details (Expanded):**
- Full description
- Assigned to (if applicable)
- Created by (user name)
- Last updated date
- View full report link

---

### Category Reports View
**File:** `app/views/dashboard/admin/admin_category_reports.py`

**Purpose:** Filter and manage reports by specific category

**Page Layout:**
```
┌─────────────────────────────────┐
│ FIXIT    [Category Name]   Menu  │
├─────────────────────────────────┤
│                                 │
│ Category: Security              │
│ Total: 45 Reports               │
│ Pending: 12 | In Progress: 20   │
│                                 │
│ Status Filter: [Dropdown]       │
│                                 │
│ [Report Cards List]             │
│                                 │
└─────────────────────────────────┘
```

**Key Features:**

1. **Category Header**
   - Category name
   - Total reports in category
   - Status breakdown

2. **Status Filter**
   - Dropdown to filter by status
   - Options: All / Pending / In Progress / Resolved / Rejected

3. **Report List**
   - Report cards specific to category
   - Same structure as all reports view
   - Status badge with color coding

4. **Status Change**
   - Each report card includes status dropdown
   - Admin can change status directly from list
   - Options: Pending → In Progress → Resolved
   - Options: Any status → Rejected
   - Audit Log: Logs "Changed report status"
   - Confirmation: Shows current and new status

**Audit Logging for Status Changes:**
- Action Type: `report_status_change`
- Recorded: Admin email, name, report ID, new status
- Timestamp: Automatic
- Success notification displayed

---

### Audit Logs Viewer
**File:** `app/views/dashboard/admin/audit_logs_viewer.py`

**Purpose:** Complete audit trail of all system actions

**Page Layout:**
```
┌──────────────────────────────────┐
│ FIXIT    Audit Logs        Menu  │
├──────────────────────────────────┤
│                                  │
│ Filters:                         │
│ [Action Type] [User] [Date Range]│
│                                  │
│ ┌────────────────────────────────┐│
│ │ User: john@example.com         ││
│ │ Action: Logged in              ││
│ │ Date: Dec 9, 2025 10:30 AM    ││
│ │ Status: Success                ││
│ └────────────────────────────────┘│
│ ┌────────────────────────────────┐│
│ │ User: jane@example.com         ││
│ │ Action: Created a report       ││
│ │ Date: Dec 9, 2025 09:15 AM    ││
│ │ Report ID: RPT-2025-001        ││
│ │ Status: Success                ││
│ └────────────────────────────────┘│
│                                  │
└──────────────────────────────────┘
```

**Filter Options:**
- **Action Type**: All / Logged in / Logged out / Created a report / Deleted a report / Changed report status / etc.
- **User Email**: Search/filter by user
- **Date Range**: From date to date picker
- **Status**: Success / Failure

**Action Descriptions** (User-Friendly):
| Action Type | Display Description |
|---|---|
| `login` | Logged in |
| `logout` | Logged out |
| `report_create` | Created a report |
| `report_update` | Updated a report |
| `report_delete` | Deleted a report |
| `report_status_change` | Changed report status |
| `user_edit` | Edited user profile |
| `password_change` | Changed password |
| `admin_view` | Accessed admin dashboard |

**Log Entry Display:**
- **User Email**: john@example.com
- **Action**: Created a report (readable format)
- **Timestamp**: Dec 9, 2025 10:30 AM
- **Details**: Location, Report ID, Category (context-dependent)
- **Status**: Success / Failure (color-coded badge)

**Features:**
- Real-time log entries
- Scrollable list with pagination
- Click entry to see full details
- Export logs as CSV (optional)
- Menu button (right) for navigation drawer

---

### User Activity Monitoring
**File:** `app/views/dashboard/admin/user_activity_monitoring.py`

**Purpose:** Monitor active users and their sessions

**Page Layout:**
```
┌──────────────────────────────────┐
│ FIXIT    User Activity      Menu  │
├──────────────────────────────────┤
│                                  │
│ Active Users: 5                  │
│                                  │
│ ┌────────────────────────────────┐│
│ │ john@example.com               ││
│ │ Last Activity: 2 minutes ago   ││
│ │ Login Time: 10:30 AM           ││
│ │ IP Address: 192.168.1.100      ││
│ └────────────────────────────────┘│
│ ┌────────────────────────────────┐│
│ │ jane@example.com               ││
│ │ Last Activity: 5 minutes ago   ││
│ │ Login Time: 10:15 AM           ││
│ │ IP Address: 192.168.1.101      ││
│ └────────────────────────────────┘│
│                                  │
│ Inactive Users (Last 24h): 23    │
│                                  │
└──────────────────────────────────┘
```

**Key Sections:**

1. **Active Users Summary**
   - Count of currently active users
   - Auto-updates every 30 seconds

2. **Active User List**
   - **User Card**
     - Email address
     - Last activity time (relative: "2 minutes ago")
     - Login timestamp
     - IP address
     - Session duration
   - Ordered by most recent activity first

3. **Inactive Users Summary**
   - Count of users inactive in last 24 hours
   - Expandable section (optional)

4. **Session Management** (Optional)
   - Force logout button for each user
   - Confirmation dialog before logout
   - Audit log: "User [X] was logged out by admin"

5. **Menu Button** (Right)
   - Opens navigation drawer

---

## Navigation Components

### Navigation Drawer
**File:** `app/views/dashboard/navigation_drawer.py`

**Purpose:** Central navigation menu accessible from any admin/user page

**Drawer Structure:**
```
┌──────────────────────────────┐
│                              │
│ FIXIT                        │
│ ─────────────────────────────│
│                              │
│ Dashboard                    │
│ [Icon] User Dashboard        │
│ [Icon] Admin Dashboard       │
│                              │
│ ─────────────────────────────│
│ Reports                      │
│ [Icon] All Reports           │
│ [Icon] By Category           │
│                              │
│ ─────────────────────────────│
│ Management (Admin Only)      │
│ [Icon] Audit Logs            │
│ [Icon] User Activity         │
│                              │
│ ─────────────────────────────│
│ Account                      │
│ [Icon] Profile               │
│ [Icon] Settings              │
│ [Icon] Logout                │
│                              │
└──────────────────────────────┘
```

**Styling:**
- **Background Color**: Dark blue (#0A3A7A)
- **Text Color**: White
- **Icon Color**: White
- **Divider Color**: Semi-transparent white (opacity: 0.2)
- **Menu Item Spacing**: 12px padding, 8px margin
- **Hover Effect**: Rounded background highlight

**Menu Items:**

1. **Dashboard Section**
   - User Dashboard (All users)
   - Admin Dashboard (Admin only)

2. **Reports Section**
   - All Reports (Admin only)
   - By Category (Admin only)

3. **Management Section** (Admin Only)
   - Audit Logs
   - User Activity

4. **Account Section**
   - Profile
   - Settings
   - Logout

**Interaction:**
- Click menu item → Navigate to respective page
- Current page highlighted (brighter background)
- Smooth transitions between pages
- Drawer closes after selection (optional)

---

### Menu Button
**File:** Various dashboard pages

**Purpose:** Quick access to navigation drawer

**Button Style:**
- **Icon**: Hamburger menu (three horizontal lines)
- **Color**: Black
- **Position**: Top-right corner
- **Size**: 32x32 pixels
- **Hover**: Slight background color change

**Pages with Menu Button:**
- Audit Logs Viewer
- User Activity Monitoring
- All Reports
- Category Reports
- Account Page

---

### Session Timeout UI
**File:** `app/views/components/session_timeout_ui.py`

**Purpose:** Warn users of impending session expiration

**Dialog Structure:**
```
┌─────────────────────────────────┐
│ Session Timeout Warning         │
├─────────────────────────────────┤
│                                 │
│ Your session is expiring soon   │
│ due to inactivity.              │
│                                 │
│ Time remaining: 2 minutes       │
│                                 │
│ [ Continue Session ] [ Logout ] │
│                                 │
└─────────────────────────────────┘
```

**Features:**
- Auto-triggers at 14 minutes of inactivity (with 1 minute warning)
- Countdown timer updates every second
- **Continue Session Button**
  - Extends session by 15 minutes
  - Returns to previous page
  - Closes dialog
- **Logout Button**
  - Clears session immediately
  - Redirects to login page
  - Displays logout confirmation

**Timing:**
- Session timeout: 15 minutes
- Warning appears: 14 minutes
- Remaining time: 1 minute to take action

---

## Common UI Patterns

### Status Badges
**Used in:** Report cards, audit logs, user activity

**Status Colors:**
| Status | Color | Hex |
|---|---|---|
| Pending | Orange/Yellow | #FFA500 |
| In Progress | Blue | #0A3A7A |
| Resolved | Green | #4CAF50 |
| Rejected | Red | #F44336 |
| Success | Green | #4CAF50 |
| Failure | Red | #F44336 |

**Badge Style:**
- Rounded rectangle
- Text: Bold, white
- Padding: 4px 8px
- Font size: 12px

---

### Confirmation Dialogs
**Used in:** Delete report, logout, status change

**Dialog Structure:**
```
┌──────────────────────────────┐
│ Confirm Action               │
├──────────────────────────────┤
│                              │
│ Are you sure you want to     │
│ delete this report?          │
│                              │
│ This action cannot be undone.│
│                              │
│ [ Cancel ] [ Delete ]        │
│                              │
└──────────────────────────────┘
```

**Features:**
- Clear action description
- Warning message (if applicable)
- Two buttons: Cancel (secondary), Confirm (primary/destructive)
- Destructive action button in red
- Escape key or Cancel button closes without action

---

### Form Input Fields
**Used in:** Report creation, login, settings

**Text Input Style:**
- Border: Light gray (#E0E0E0)
- Background: White
- Padding: 10px 12px
- Border radius: 4px
- Focus: Blue border (#0A3A7A), shadow
- Error: Red border (#F44336)

**Label Style:**
- Color: Dark gray (#424242)
- Font weight: 500
- Font size: 14px
- Margin bottom: 6px

**Validation:**
- Real-time feedback
- Error message in red below field
- Character counter for text areas
- Required field indicator (asterisk: *)

---

### Loading States
**Used in:** Form submission, data loading

**Loading Indicator:**
- Circular progress spinner
- Primary blue color (#0A3A7A)
- Size: 24x24 or 32x32 pixels
- Animated rotation

**Button States:**
- **Normal**: Enabled, clickable, primary color
- **Loading**: Disabled, spinner visible, text hidden or grayed
- **Disabled**: Light gray, not clickable, no cursor change
- **Success**: Green checkmark (2 seconds), then restore
- **Error**: Red outline, error message below

---

### Toast Notifications
**Used in:** Success messages, error alerts

**Toast Style:**
- **Success**: Green background (#4CAF50), white text
- **Error**: Red background (#F44336), white text
- **Warning**: Orange background (#FFA500), white text
- **Info**: Blue background (#0A3A7A), white text

**Position**: Bottom-right corner
**Duration**: 3-5 seconds auto-dismiss
**Actions**: Manual dismiss button (X)

**Examples:**
- "Report created successfully"
- "Failed to update report. Please try again."
- "Session expires in 1 minute"
- "You have been logged out"

---

### Empty States
**Used in:** No reports, no logs, no users

**Empty State Display:**
```
┌─────────────────────────────┐
│                             │
│          📋                 │
│                             │
│  No reports found           │
│                             │
│  Start by creating a new    │
│  report using the button    │
│  below.                     │
│                             │
│  [ Create New Report ]      │
│                             │
└─────────────────────────────┘
```

**Components:**
- Icon (relevant to content)
- Heading: What's missing
- Description: Why it's empty
- Call-to-action button (if applicable)

---

## Color Scheme & Branding

### Primary Colors
| Color | Hex | Usage |
|---|---|---|
| Primary Blue | #0A3A7A | Buttons, headers, active states |
| Dark Gray | #424242 | Text, labels |
| Light Gray | #E0E0E0 | Borders, backgrounds |
| White | #FFFFFF | Page background, card background |

### Status Colors
| Status | Hex | Usage |
|---|---|---|
| Success/Green | #4CAF50 | Resolved status, success messages |
| Warning/Orange | #FFA500 | Pending status, warnings |
| Error/Red | #F44336 | Rejected status, errors, deletions |
| Info/Blue | #0A3A7A | In progress, info messages |

### Dark Mode Colors
| Element | Hex | Usage |
|---|---|---|
| Background | #1E1E1E | Page background |
| Card Background | #2D2D2D | Card backgrounds |
| Text | #FFFFFF | Primary text |
| Border | #3D3D3D | Card borders |
| Navigation Drawer | #0A3A7A | Menu background (same as light) |

---

### Typography
**Font Family**: Poppins (system fallback: Arial, sans-serif)

**Font Sizes:**
| Element | Size | Weight |
|---|---|---|
| Page Title | 24px | Bold |
| Section Title | 18px | SemiBold |
| Label | 14px | Medium |
| Body Text | 14px | Regular |
| Small Text | 12px | Regular |
| Button Text | 14px | Medium |

---

### Branding Elements

**Logo:**
- **File**: `assets/cspc_logo.png`
- **Usage**: Header, favicon, branding
- **Size**: 32x32 pixels (header), varies for other uses

**Favicon:**
- **File**: `assets/cspc_logo.png`
- **Position**: Browser tab
- **Platforms**: Web and Desktop

**App Title**: "FIXIT"
- Displayed in page title
- Displayed in header

---

## Responsive Design

**Breakpoints:**
- **Mobile**: < 600px
- **Tablet**: 600px - 1024px
- **Desktop**: > 1024px

**Layout Adjustments:**
- Navigation drawer becomes full-screen on mobile
- Cards stack vertically on mobile
- Font sizes reduce on smaller screens
- Button sizes remain accessible on all devices

---

## Accessibility

**WCAG 2.1 Compliance:**
- Color contrast ratios meet AA standards
- Button sizes minimum 44x44 pixels
- Form labels associated with inputs
- Error messages clearly linked to fields
- Loading states announced to screen readers
- Focus states visible for keyboard navigation

---

## Future Enhancements

- [ ] Dark mode toggle persistence
- [ ] Category icons in sidebar
- [ ] Advanced search and filtering
- [ ] Report attachment management
- [ ] Email notifications
- [ ] Report assignment workflow
- [ ] Analytics dashboard
- [ ] Bulk actions on reports

---

**Document Version**: 1.0
**Last Updated**: December 9, 2025
**Author**: FIXIT Development Team
