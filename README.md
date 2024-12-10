# About LifeLog

A simple diary posting and management system with user authentication, featuring role-based access control for regular users and administrators.

## Important Notice
- This application is under development and may have security and performance issues.

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test additions
- 2024/12/09: Migration functionality added
- 2024/12/10: Test coverage improvements, documentation updates, and environment setup changes

## Key Features

- User Management (Registration, Authentication, Access Control)
- Diary Entry Management (Create, Edit, Delete)
- Administrative Functions (User Management, Content Management)
- Simple and User-Friendly Interface

## Technology Stack

- Python 3.11
- Flask 3.1.0
- SQLAlchemy 2.0.36
- Flask-SQLAlchemy 3.1.1
- Alembic 1.14.0
- Flask-WTF 1.2.1
- SQLite3
- HTML/CSS/JavaScript

## Setup Instructions

1. Prepare Python Environment
```bash
# Install Miniconda (if not already installed)
# Download from: https://docs.conda.io/en/latest/miniconda.html

# Create conda environment
conda create -n lifelog python=3.11
conda activate lifelog
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Database Setup
```bash
# Run migrations
alembic upgrade head

# Create initial data
python -c "from models import create_initial_data; create_initial_data()"
```

4. Start Application
```bash
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
- User Authentication and Registration (92% coverage)
- Diary Entry Creation, Editing, and Deletion (96% coverage)
- User Management (90%+ coverage)
- Access Control
- Database Operations

## Initial Accounts

Administrator Account:
- User ID: admin
- Password: Admin3210

Test Users:
- User ID: tetsu
- Password: Tetsu3210

- User ID: gento
- Password: Gento3210

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
├── models.py           # SQLAlchemy Model Definitions (Unified)
├── alembic.ini         # Migration Configuration
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
│   ├── index.html     # Homepage
│   ├── login.html     # Login Page
│   ├── register.html  # Registration Page
│   ├── settings.html  # User Settings Page
│   └── admin.html     # Admin Panel
├── migrations/        # Migration Files
│   └── versions/      # Version-controlled Migrations
├── instance/          # Instance-specific Files
│   └── diary.db      # SQLite Database
├── tests/            # Test Files
│   ├── conftest.py   # Test Configuration
│   ├── test_user.py  # User Tests
│   ├── test_entry.py # Entry Tests
│   └── test_user_manager.py # User Manager Tests
└── docs/             # Documentation
    ├── specification.md     # Specifications (English)
    ├── specification_ja.md  # Specifications (Japanese)
    ├── diagrams.md         # Design Diagrams (English)
    └── diagrams_ja.md      # Design Diagrams (Japanese)
