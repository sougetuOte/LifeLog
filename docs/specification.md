# LifeLog Specification

## Version History
- 2024/12/01: Initial release 0.01

## Table of Contents
1. [User Management](#1-user-management)
2. [Diary Management](#2-diary-management)
3. [Screen Specifications](#3-screen-specifications)
4. [Database Design](#4-database-design)
5. [Security Specifications](#5-security-specifications)

## 1. User Management

### 1.1 User Registration
- User ID: 4-20 alphanumeric characters
- Name (Display Name): 3-20 characters (any character type)
- Password: 8-20 characters (must include at least one uppercase letter, lowercase letter, and number)

### 1.2 Login Function
- Authentication using User ID and Password
- Account lockout after 3 consecutive failed login attempts
- Only administrators can unlock accounts
- Deactivated users cannot log in (displays "Invalid User ID or Password")

### 1.3 Account Deactivation
- Password verification required for confirmation
- Deactivated accounts have the following restrictions:
  - Cannot log in
  - Diary entries only visible to administrators
- Administrator accounts cannot be deactivated
- Account deactivation is irreversible

### 1.4 User Roles
1. Administrator (admin)
   - View/edit/delete all users' diary entries (including deactivated users)
   - User management (unlock accounts, grant/revoke admin privileges)
   - Manage deactivated users' diary entries
   - Change own settings (cannot deactivate)

2. Regular User
   - View diary entries of active users
   - Create/edit/delete own diary entries
   - Change own settings (can deactivate account)

3. Non-logged-in User
   - View diary entries of active users only

### 2.2 Diary Management

#### 2.2.1 Diary Entry Creation
- Title (required)
- Content (required)
- Notes (optional, for weather, mood, health condition, etc.)
- Automatic creation timestamp
- Automatic update timestamp (when edited)

#### 2.2.2 Diary Display
- Displayed in reverse chronological order
- Shows author's name and user ID
- Displays creation and last update timestamps
- Edit/delete buttons only shown to authorized users
- Entries from deactivated users only visible to administrators

### 2.3 User Settings

#### 2.3.1 Configurable Items
- Change display name
- Change password (current password verification required)
- Account deactivation (password verification required)

### 2.4 Administrator Functions

#### 2.4.1 User Management
- User list display
  - Active users
  - Deactivated users (semi-transparent display)
- Account lock status check and unlock
- Grant/revoke admin privileges (active users only)
- Login attempt history review
- Manage deactivated users' diary entries

## 3. Screen Specifications

### 3.1 Common Header
Non-logged-in state:
- Home
- Login
- Register

Logged-in state:
- Home
- User Settings
- User Management (admin only)
- Logout
- Username display
- Admin badge (admin only)

### 3.2 Screens

#### 3.2.1 Home Screen (/)
- Diary entry list
- Entry form (logged-in users only)
  - Title input
  - Content input
  - Notes input (weather, mood, health condition, etc.)
- No pagination

#### 3.2.2 Login Screen (/login)
- User ID input
- Password input
- Login attempt counter display
- Error message display

#### 3.2.3 Registration Screen (/register)
- User ID input (with validation)
- Name input (with validation)
- Password input (with validation)
- Input rules display
- Error message display

#### 3.2.4 User Settings Screen (/settings)
- Display name change
- Password change
- Current settings display
- Account deactivation section
  - Deactivation button
  - Confirmation modal
  - Password verification

#### 3.2.5 Admin Screen (/admin)
- User list
  - Active/deactivated status display
  - Lock status display
  - Login attempt history
  - Admin privilege controls (active users only)
  - Unlock button

## 4. Database Design

### 4.1 users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    is_locked BOOLEAN NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT 1,
    login_attempts INTEGER NOT NULL DEFAULT 0,
    last_login_attempt TEXT,
    created_at TEXT NOT NULL
);
```

### 4.2 entries Table
```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 5. Security Specifications

### 5.1 Account Security
- Password complexity requirements
- Login attempt limits
- Account lockout functionality
- Password verification for account deactivation

### 5.2 Access Control
- Session-based authentication
- Role-based access control
- CSRF protection (Flask built-in feature)
- Deactivated users' entries accessible only to administrators

## 6. Important Notes

### 6.1 Development Environment Usage
- This application is for development environment use only
- The following measures are required for production deployment:
  - Secure session key configuration
  - Production-grade WSGI server implementation
  - Password hashing
  - Database backup strategy
  - Enhanced error handling

### 6.2 Limitations
- No file upload functionality
- No pagination support
- No password reset feature
- No account deactivation reversal
