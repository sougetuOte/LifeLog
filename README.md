# LifeLog

## Overview
LifeLog is a diary management system that allows users to record and manage their daily activities.

## Features
- User authentication and management
- Diary entry creation and management
- Multi-language support (English/Japanese)

## Installation
```bash
# Create conda environment
conda create -n lifelog python=3.11.10
conda activate lifelog

# Install dependencies
pip install -r requirements.txt

# Initialize database
python create_data.py
```

## Usage
```bash
# Start development server
python app.py
```

Access http://localhost:5000 in your web browser.

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test additions
- 2024/12/09: Migration functionality added
- 2024/12/10: Development environment changed to conda-based
