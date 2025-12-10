# Team Roles & Contribution Matrix

**Document Tags & Metadata:**
- **Status:** Complete & Ready for Submission
- **Document Type:** Team Documentation
- **Version:** 1.0
- **Last Updated:** December 10, 2025

---

## Table of Contents
1. [Team Members & Roles](#team-members--roles)
3. [Detailed Responsibilities](#detailed-responsibilities)
4. [Contribution Matrix](#contribution-matrix)

---

## Team Overview

| **Team Member** | **GitHub Username** | **Primary Role** | **Title Stack** |
|---|---|---|---|
| **Arabella Bayta** | `arabte-src/arabyte-io` | Full-Stack Developer & Technical Lead | Full-Stack Developer, AI/ML Model Developer, Lead Developer & Architect, UI/UX Designer |
| **Olivares, Elyssa** | `elyssaolivares` | Project Manager & Database Engineer | Project Manager, Database Engineer, Documentation Lead, UI Designer, API Integration Specialist |
| **Biares, Francisca** | `Francisca1728` | Quality Assurance & Tester | Application Tester

---

## Team Members & Roles

### 1. Arabella Bayta
**Primary Role:** Full-Stack Developer & Technical Lead

**Title Stack:**
- Full-Stack Developer
- AI/ML Model Developer
- Lead Developer & Architect
- UI/UX Designer

**Key Competencies:**
- Backend architecture and design
- Full-stack implementation (Python, Flet)
- AI/ML integration
- Google OAuth/API integration
- Frontend development
- Automated testing
- Git workflow management


---

### 2. Olivares, Elyssa
**Primary Role:** Project Manager & Database Engineer

**Title Stack:**
- Project Manager
- Database Engineer
- Documentation Lead
- UI Designer
- API Integration Specialist

**Key Competencies:**
- Project scheduling and coordination
- Database design and optimization
- Documentation and technical writing
- Google OAuth/API integration
- UI/UX design
- Team coordination

---

### 3. Biares, Francisca
**Primary Role:** Quality Assurance & Tester

**Title Stack:**
- Application Tester
- Bug Tracker

**Key Competencies:**
- Manual testing and validation
- Quality assurance
---

## Detailed Responsibilities

### Arabella Bayta - Full-Stack Developer & Lead

#### Backend Development
- **Authentication System**
  - Implemented admin-only authentication
  - Google OAuth integration (in progress)
  - Session management with 15-minute timeout
  - Password hashing using SHA256

- **Database Services**
  - Designed report management CRUD operations
  - Implemented database schema normalization
  - Built user management system
  - Created audit logging system

- **API & Business Logic**
  - Report creation, retrieval, updating, deletion
  - Status normalization and validation
  - Category prediction using AI
  - User role management

#### Frontend Development
- **Page Implementation**
  - Homepage with session validation
  - Login page with role-based access
  - User dashboard with report listing
  - Report creation form
  - Admin dashboard with statistics

- **UI Components**
  - Navigation drawer with role-based menu items
  - Report card component with actions
  - Status badge styling
  - Theme toggle (dark/light mode)
  - Session timeout warning dialog

- **User Experience**
  - Form validation and error messages
  - Loading states and feedback
  - Snackbar notifications
  - Empty state handling

#### Testing & Quality
- **Automated Tests**
  - Unit tests for AI services
  - Database operation tests
  - Authentication tests
  - Audit logging tests
  - Session management tests

- **Test Coverage**
  - Pytest configuration
  - Coverage reporting (htmlcov)
  - 75%+ code coverage target
  - Continuous integration setup

#### Architecture & Design
- **System Architecture**
  - Three-tier application design (UI, Services, Database)
  - MVC pattern implementation
  - Service-oriented architecture
  - Database abstraction layer

- **Code Organization**
  - Modular package structure
  - Separation of concerns
  - Reusable component design
  - Configuration management

#### AI/ML Model Developer
- **Category Prediction System**
  - Developed AI-based category prediction model
  - Uses machine learning for intelligent categorization
  - Automatic category suggestion during report creation
  - Model training and optimization

- **Data Processing**
  - Dataset preparation and cleaning (dataset.csv)
  - Feature extraction from report descriptions
  - Model evaluation and accuracy metrics
  - Continuous model improvement

- **Integration**
  - Integrated AI model with report creation form
  - Real-time category prediction functionality
  - Fallback mechanisms for prediction failures
  - Performance optimization for model inference

#### Git & Version Control
- **Repository Management**
  - Main branch protection and policies
  - Feature branch creation and merging
  - Pull request reviews
  - Commit history management

- **Development Workflow**
  - Feature branches: `feature/*`
  - Development branch: `dev`
  - Main branch: `main` (production)

#### UI/UX Design
- **User Interface Design**
  - Page layout and composition
  - Component design and styling
  - Responsive layout adjustments
  - Visual hierarchy and spacing

- **User Experience**
  - User flow optimization
  - Interaction patterns
  - Feedback mechanisms (snackbars, dialogs)
  - Loading and error states

- **Design System**
  - Reusable component library
  - Consistent styling approach
  - Theme-aware color implementation
  - Accessibility considerations

- **Design Tools & Implementation**
  - Flet framework UI component utilization
  - Custom component development
  - Cross-platform compatibility

---

### Elyssa Olivares - Project Manager & Database Engineer

#### Project Management
- **Planning & Scheduling**
  - Sprint planning and task breakdown
  - Deadline tracking and milestone management
  - Team coordination and communication
  - Risk assessment and mitigation

- **Coordination**
  - Daily standups and progress tracking

#### Database Design & Management
- **Schema Design**
  - Reports table with normalized fields
  - Users table with profile support
  - Audit logs table with comprehensive tracking
  - Relational integrity and constraints

- **Database Operations**
  - Query optimization
  - Index management
  - Data integrity validation
  - Backup and recovery procedures

- **Data Management**
  - User creation and management
  - Report lifecycle management
  - Audit trail maintenance
  - Data consistency verification

#### API Integration
- **Google Authentication**
  - OAuth 2.0 implementation
  - Token management
  - User profile retrieval
  - Secure credential handling

- **API Endpoints**
  - Authentication endpoints
  - Report management endpoints
  - User management endpoints
  - Audit log retrieval endpoints

#### Documentation

- **Technical Documentation**
  - System architecture documentation
  - Database schema documentation(ERD)

- **User Documentation**
  - Installation and setup guide
  - User manual
  - Admin capabilities guide
  - UI Annotation

 - **Code Documentation**
   - README

- **Project Documentation**
   - SRS
   - Project report

#### UI/UX Design
- **User Flow Design**
  - Login flow optimization
  - Report creation workflow
  - Admin dashboard layout
  - Navigation structure

- **Design Consistency**
  - Color scheme definition
  - Typography standards

---

### Francisca Louise Biares - QA & Testing

#### Manual Testing
- **Feature Testing**
  - Login functionality validation
  - Report creation and submission
  - Report viewing and deletion
  - Admin dashboard operations
  - Navigation and menu functionality

- **User Acceptance Testing**
  - End-to-end workflow validation
  - User interface responsiveness
  - Form validation and error messages
  - Session management behavior

- **Regression Testing**
  - Testing after bug fixes
  - Verifying previous features still work
  - Cross-browser compatibility
  - Cross-platform testing (desktop/web)

#### UI/UX Testing
- **Interface Validation**
  - Button functionality and responsiveness
  - Form input validation
  - Navigation drawer behavior
  - Menu item accessibility

- **User Experience Validation**
  - Dialog and modal behavior
  - Notification (snackbar) clarity
  - Error message clarity and usefulness
  - Loading state visibility

- **Accessibility Testing**
  - Tab navigation between fields
  - Color contrast validation
  - Button size and click-ability
  - Form label associations

---

## Contribution Matrix

### By Project Area

| **Project Area** | **Arabella** | **Elyssa** | **Francisca** |
|---|:---:|:---:|:---:|
| **System Architecture** | 90% | 10% | — |
| **Backend Development** | 85% | 15% | — |
| **Frontend Development** | 90% | 10% | — |
| **AI/ML Integration** | 100% | — | — |
| **Database Design** | 20% | 80% | — |
| **Database Implementation** | 70% | 30% | — |
| **Google Auth/API** | 50% | 50% | — |
| **Documentation** | — | 100% | — |
| **Manual Testing** | 20% | 10% | 70% |
| **Automated Testing** | 85% | 5% | 10% |
| **Version Control/Git** | 60% | 30% | 10% |
| **Project Management** | 15% | 85% | — |
| **UI/UX Design** | 50% | 50% | — |
| **QA & Quality** | 20% | 10% | 70% |