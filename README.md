# About LifeLog

A simple diary posting and management system with user authentication, featuring role-based access control for regular users and administrators.

## Important Notice
- This application is under development and may have security and performance issues.

## Version History
- 2024/12/01: Initial release 0.01

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

For detailed application specifications, please refer to the [specification document](docs/specification.md).
