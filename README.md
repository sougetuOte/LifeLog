# About LifeLog

A simple diary posting and management system with user authentication, featuring role-based access control for regular users and administrators.

## Important Notice
- This application is under development and may have security and performance issues.

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test additions

## Key Features

- User Management (Registration, Authentication, Access Control)
- Diary Entry Management (Create, Edit, Delete)
- Administrative Functions (User Management, Content Management)
- Simple and User-Friendly Interface

## Technology Stack

- Python 3.11.9
- Flask 3.1.0
- SQLite3
- HTML/CSS/JavaScript

## Setup Instructions

1. Prepare Python Environment
```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Initialize Database and Start Application
```bash
python -c "from app import init_db; init_db()"
python app.py
```

After starting the application, access http://127.0.0.1:5000 in your browser.

## Running Tests

1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

2. Run Tests
```bash
pytest
```

The tests cover the following areas:
- User Authentication and Registration (90%+ coverage)
- Diary Entry Creation, Editing, and Deletion (90%+ coverage)
- User Management (90%+ coverage)
- Access Control
- Database Operations

## Default Account

Administrator Account:
- User ID: admin
- Password: Admin3210

## Current Limitations

The current development version has the following limitations:
- No file upload functionality
- No pagination support
- No password reset feature
- No account deletion reversal

## License
- [MIT License](LICENSE)

## Detailed Specifications

For detailed application specifications, please refer to the following documents:
- [Specification (English)](docs/specification.md)
- [Design Diagrams (English)](docs/diagrams.md)

## Project Structure

```
/
├── app.py              # Main Application
├── database.py         # Database Operations
├── models/            # Model Definitions
│   ├── __init__.py    # Model Package Initialization
│   ├── base.py        # Base Class Definition
│   ├── user.py        # User Model
│   ├── entry.py       # Diary Entry Model
│   ├── diary_item.py  # Diary Item Model
│   ├── user_manager.py # User Management
│   └── init_data.py   # Initial Data Creation
├── static/            # Static Files
│   ├── style.css      # Common Styles
│   ├── admin.css      # Admin Panel Styles
│   ├── user.css       # User Settings Styles
│   ├── main.css       # Main Styles
│   └── script.js      # Client-side Scripts
├── templates/         # HTML Templates
├── tests/            # Test Files
│   ├── conftest.py   # Test Configuration
│   ├── test_user.py  # User Tests
│   ├── test_entry.py # Entry Tests
│   └── test_user_manager.py # User Manager Tests
└── docs/             # Documentation
