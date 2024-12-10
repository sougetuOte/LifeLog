# LifeLog Specification

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test specification additions
- 2024/12/09: Database structure and migration specification additions
- 2024/12/10: Test coverage updates, security specification enhancements, and environment setup changes


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
    last_login_attempt DATETIME,
    created_at DATETIME NOT NULL
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
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

### 4.3 diary_items Table
```sql
CREATE TABLE diary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE
);
```

### 4.4 Migration Management
- Migration management using Alembic
- Migration files stored in `migrations/versions/`
- Migration configuration managed in `alembic.ini`

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
   - One-to-many relationship with Entries

2. Entry: Diary entry management
   - Basic attributes (ID, user ID, title, content, notes)
   - Timestamps (creation time, update time)
   - Update functionality
   - Relationships with User and DiaryItems
   - Cascade delete settings

3. DiaryItem: Diary item management
   - Basic attributes (ID, entry ID, item name, item content)
   - Timestamp (creation time)
   - Relationship with Entry
   - Cascade delete settings

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

models.py          # SQLAlchemy Model Definitions (Unified)
```

## 6. Security Specifications

### 6.1 Account Security

#### 6.1.1 Password Policy
- Length: 8-20 characters
- Required character types:
  - At least one uppercase letter (A-Z)
  - At least one lowercase letter (a-z)
  - At least one number (0-9)
- Prohibited characters:
  - Whitespace
  - Tab
  - Line break
  - Special characters (< > & ' ")
- Password history: Cannot reuse last 3 passwords
- Password expiration: 90 days

#### 6.1.2 Account Lock Mechanism
- Lock condition: 3 consecutive failed login attempts
- Lock duration: 24 hours (manual unlock by admin possible)
- Unlock conditions:
  - Manual unlock by administrator
  - Administrator approval after lock period
- Restrictions during lock:
  - Login attempts not allowed
  - Password reset not allowed

#### 6.1.3 Session Management
- Session timeout: 30 minutes
- Concurrent sessions: Only one session per user allowed
- Session invalidation conditions:
  - Logout
  - Timeout
  - Password change
  - Account lock
  - Forced logout by administrator

### 6.2 Access Control

#### 6.2.1 Authentication Method
- Form-based authentication
- Session-based state management
- No Remember-Me functionality
- Automatic logout (30 minutes)

#### 6.2.2 Authorization Management
- Role-Based Access Control (RBAC)
- Permission levels:
  1. Administrator (full access)
  2. Regular user (restricted access)
  3. Non-logged-in user (view only)
- Access control:
  - URL-based
  - Function-based
  - Data-based

#### 6.2.3 CSRF Protection
- Using Flask's built-in CSRF protection
- CSRF token required for all POST/PUT/DELETE requests
- Token expiration: Synchronized with session
- Double Submit Cookie protection

### 6.3 Data Protection

#### 6.3.1 Password Protection
- Hash algorithm: Argon2id
- Salt: Random per user (16 bytes)
- Stretching: 10,000 iterations
- Memory cost: 64MB

#### 6.3.2 Database Security
- Use of prepared statements
- SQL injection prevention
- Backups:
  - Daily full backup
  - Hourly differential backup
  - Encrypted backup

#### 6.3.3 Sensitive Data Protection
- Personal information encryption (AES-256-GCM)
- Audit log storage:
  - Login attempts
  - Critical operations
  - Errors
  - Security events

### 6.4 Communication Security

#### 6.4.1 HTTPS
- TLS 1.3 only
- Strong cipher suites
- HSTS (HTTP Strict Transport Security) enabled
- Certificate pinning

#### 6.4.2 Security Headers
- Content-Security-Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Feature-Policy

#### 6.4.3 API Security
- Rate limiting:
  - IP-based: 100 requests/minute
  - User-based: 50 requests/minute
- Request size limit: 10MB
- Timeout: 30 seconds

### 6.5 Monitoring and Logging

#### 6.5.1 Security Monitoring
- Real-time alerts:
  - Consecutive login failures
  - Abnormal access patterns
  - Privilege escalation attempts
- Regular security scans
- Vulnerability assessment

#### 6.5.2 Log Management
- Access logs
- Security event logs
- Error logs
- Audit logs
- Log retention period: 1 year
- Log encryption

## 7. Test Specifications

### 7.1 Test Configuration
- pytest.ini configuration
  - Test path: tests/
  - Test file naming convention: test_*.py
  - Coverage report settings
  - Minimum coverage requirement: 90%
- conftest.py test fixture definitions
  - Flask application configuration
  - Database configuration (in-memory SQLite)
  - Session management
  - Transaction control
- Individual test modules
  - test_user.py: User-related functionality tests (92% coverage)
  - test_entry.py: Diary entry functionality tests (96% coverage)
  - test_user_manager.py: User management functionality tests (90% coverage)

### 7.2 Test Coverage

#### 7.2.1 User Authentication and Registration
- User creation
  - Normal case: Creation with valid data
  - Error case: Creation attempt with invalid data
- Password verification
  - Normal case: Correct password
  - Error case: Incorrect password
- Lock functionality
  - Login attempt count management
  - Account lock occurrence
  - Lock release process

#### 7.2.2 Diary Entry Management
- Entry creation
  - Required field validation
  - Character limit validation
- Validation
  - Title and content required check
  - Optional notes input
- Update processing
  - Automatic creation timestamp
  - Automatic update timestamp
- Delete processing
  - Cascade delete confirmation
  - Related data integrity

#### 7.2.3 User Management
- User visibility control
  - Active user display
  - Deactivated user hiding
- Administrator privilege operations
  - Privilege grant testing
  - Privilege revocation testing
- Lock operations
  - Lock status changes
  - Lock release permission verification

### 7.3 Test Environment
- Test dependencies managed by requirements-test.txt
  - pytest 8.3.4
  - pytest-cov 6.0.0
  - coverage 7.6.9
- Test database
  - SQLite (in-memory)
  - Automatic creation and deletion
  - Transaction control
- Test fixtures
  - Session management
  - Database initialization
  - User data generation
  - Diary data generation

### 7.4 Coverage Statistics
- Model layer: 92%+ coverage
  - User: 92%
  - Entry: 96%
  - DiaryItem: 93%
  - UserManager: 90%
- Application layer: 85%
  - app.py: 87%
  - database.py: 85%
  - init_data.py: 83%
- Improvement plans
  - Application layer coverage enhancement
  - Error handling test strengthening
  - Boundary value testing addition

### 7.5 Development Environment
- Python 3.11 (conda environment)
- Core packages
  - Flask 3.1.0
  - SQLAlchemy 2.0.36
  - Flask-SQLAlchemy 3.1.1
  - Alembic 1.14.0
  - Flask-WTF 1.2.1
  - WTForms 3.1.2
  - pyppeteer 2.0.0
  - pyyaml 6.0.2

## 8. Important Notes

### 8.1 Development Environment Usage
- This application is for development environment use only
- The following measures are required for production deployment:
  - Secure session key configuration
  - Production-grade WSGI server implementation
  - Password hashing
  - Database backup strategy
  - Enhanced error handling
  - Log output configuration
  - Performance tuning

### 8.2 Limitations
- No file upload functionality
- No pagination support
- No password reset feature
- No account deletion reversal
- No bulk operation functionality
- No API documentation

