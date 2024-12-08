# LifeLog Specification

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test specification additions

## Table of Contents
1. [User Management](#1-user-management)
2. [Diary Management](#2-diary-management)
3. [Screen Specifications](#3-screen-specifications)
4. [Database Design](#4-database-design)
5. [Model Structure](#5-model-structure)
6. [Security Specifications](#6-security-specifications)
7. [Test Specifications](#7-test-specifications)
8. [Important Notes](#8-important-notes)

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

## 5. Model Structure

### 5.1 Basic Structure
- Base: Base class for all models
  - Inherits from SQLAlchemy's DeclarativeBase

### 5.2 Model Classes
1. User: User information management
   - Basic attributes (ID, user ID, name, password)
   - Status flags (admin, lock, visibility)
   - Login attempt tracking (attempt count, last attempt time)
   - Password verification functionality
   - Lock status check functionality

2. Entry: Diary entry management
   - Basic attributes (ID, user ID, title, content, notes)
   - Timestamps (creation time, update time)
   - Update functionality

3. DiaryItem: Diary item management
   - Basic attributes (ID, entry ID, item name, item content)
   - Timestamp (creation time)

4. UserManager: User management functionality
   - User list retrieval (visible users/all users)
   - Account lock management
   - Administrator privilege management

### 5.3 Module Structure
```
models/
├── __init__.py    # Model package initialization
├── base.py        # Base class definition
├── user.py        # User model
├── entry.py       # Diary entry model
├── diary_item.py  # Diary item model
├── user_manager.py # User management
└── init_data.py   # Initial data creation
```

## 6. Security Specifications

[Security specifications remain unchanged]

## 7. Test Specifications

### 7.1 Test Configuration
- pytest.ini configuration
  - Test path: tests/
  - Test file naming convention: test_*.py
  - Coverage report settings
- conftest.py test fixture definitions
  - Flask application configuration
  - Database configuration
  - Session management
- Individual test modules
  - test_user.py: User-related functionality tests (100% coverage)
  - test_entry.py: Diary entry functionality tests (96% coverage)
  - test_user_manager.py: User management functionality tests (100% coverage)

### 7.2 Test Coverage
- User authentication and registration
  - User creation
  - Password verification
  - Lock functionality
- Diary entry management
  - Entry creation
  - Validation
  - Update processing
- User management
  - User visibility control
  - Administrator privilege operations
  - Lock operations

### 7.3 Test Environment
- Test dependencies managed by requirements-test.txt
  - pytest 7.4.0
  - pytest-cov 4.1.0
  - coverage 7.3.0
- Test database
  - SQLite (in-memory)
  - Automatic creation and deletion
- Test fixtures
  - Session management
  - Transaction control
  - Rollback functionality

### 7.4 Coverage Statistics
- Model layer: 90%+ coverage
  - User: 92%
  - Entry: 96%
  - DiaryItem: 93%
  - UserManager: 73%
- Areas needing improvement
  - Application layer (app.py)
  - Database operations (database.py)
  - Initial data creation (init_data.py)

## 8. Important Notes

### 8.1 Development Environment Usage
- This application is for development environment use only
- The following measures are required for production deployment:
  - Secure session key configuration
  - Production-grade WSGI server implementation
  - Password hashing
  - Database backup strategy
  - Enhanced error handling

### 8.2 Limitations
- No file upload functionality
- No pagination support
- No password reset feature
- No account deletion reversal
