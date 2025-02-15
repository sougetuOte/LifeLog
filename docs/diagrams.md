# LifeLog - Design Diagrams

## Version History
- 2024/12/01: Initial release 0.01
- 2024/12/08: Model structure improvements and test configuration additions
- 2024/12/09: Database structure and migration specification additions
- 2024/12/10: Test coverage updates, component diagram improvements, and environment setup changes
- 2025/01/08: Pagination feature implementation

## 1. Screen Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> HomePage
    
    state "Non-logged-in" as Guest {
        HomePage --> Login
        HomePage --> Register
        Login --> HomePage: Login Success
        Register --> Login: Registration Success
    }

    state "Logged-in User" as User {
        state "Regular User Functions" as Normal {
            HomePage --> UserSettings
            UserSettings --> HomePage
            UserSettings --> Login: Account Deactivated
        }
    }

    state "Administrator" as Admin {
        state "Admin Functions" as AdminFunc {
            HomePage --> UserManagement
            UserManagement --> HomePage
        }
    }

    HomePage --> [*]: Logout
```

## 2. Class Diagram

```mermaid
classDiagram
    class Base {
        <<abstract>>
        +DeclarativeBase
    }

    class User {
        +int id
        +string userid
        +string name
        +string password
        +bool is_admin
        +bool is_locked
        +bool is_visible
        +int login_attempts
        +datetime last_login_attempt
        +datetime created_at
        +List[Entry] entries
        +check_password()
        +validate_password()
        +check_lock_status()
    }

    class Entry {
        +int id
        +int user_id
        +string title
        +string content
        +string notes
        +datetime created_at
        +datetime updated_at
        +User user
        +List[DiaryItem] items
        +update()
    }

    class DiaryItem {
        +int id
        +int entry_id
        +string item_name
        +string item_content
        +datetime created_at
        +Entry entry
    }

    class UserManager {
        +get_visible_users()
        +get_all_users()
        +lock_user()
        +unlock_user()
        +toggle_admin()
    }

    Base <|-- User
    Base <|-- Entry
    Base <|-- DiaryItem
    User "1" -- "*" Entry : creates >
    Entry "1" -- "*" DiaryItem : contains >
    UserManager -- User : manages
```

## 3. Sequence Diagrams

### Login Process

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Enter login credentials
    Frontend->>Backend: POST /api/login
    Backend->>Database: Search user (is_visible=1)
    Database-->>Backend: User information
    
    alt User exists and is visible
        alt Password is correct
            Backend->>Database: Reset login attempts
            Backend-->>Frontend: Success response
            Frontend->>Frontend: Redirect to homepage
        else Password is incorrect
            Backend->>Database: Increment login attempts
            alt attempts >= 3
                Backend->>Database: Lock account
                Backend-->>Frontend: Lock error
            else attempts < 3
                Backend-->>Frontend: Authentication error
            end
        end
    else User doesn't exist or is deactivated
        Backend-->>Frontend: Authentication error
    end
```

### Account Deactivation Process

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Click deactivate button
    Frontend->>Frontend: Show confirmation modal
    User->>Frontend: Enter password
    Frontend->>Backend: POST /api/user/deactivate
    Backend->>Database: Verify password
    
    alt Password is correct
        alt Not an admin
            Backend->>Database: Update is_visible=0
            Backend-->>Frontend: Success response
            Frontend->>Frontend: Redirect to login
        else Is admin
            Backend-->>Frontend: Error: Admin cannot be deactivated
        end
    else Password is incorrect
        Backend-->>Frontend: Authentication error
    end
```

### Pagination Process

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Select page number
    Frontend->>Backend: GET /entries?page={page}
    Backend->>Database: Get total entries count
    Database-->>Backend: Total entries count
    Backend->>Database: Get paginated entries
    Database-->>Backend: Entry data
    Backend-->>Frontend: Entry list and page info
    Frontend->>Frontend: Update view and adjust scroll position
```

### Diary Entry Process

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Enter title, content, notes
    Frontend->>Backend: POST /entries
    Backend->>Database: Check user visibility
    Database-->>Backend: User information
    
    alt User is visible
        Backend->>Database: Save entry
        Backend-->>Frontend: Success response
        Frontend->>Frontend: Clear form
        Frontend->>Backend: GET /entries
        Backend->>Database: Fetch entries
        Database-->>Backend: Entry data
        Backend-->>Frontend: Entry list
        Frontend->>Frontend: Update list
    else User is deactivated
        Backend-->>Frontend: Error: Account invalid
    end
```

## 4. Use Case Diagram

```mermaid
graph TB
    subgraph Non-logged-in User
        A[View Diary List]
        B[Login]
        C[Register]
    end

    subgraph Regular User
        D[Create Entry]
        E[Edit Own Entries]
        F[Delete Own Entries]
        G[Change Settings]
        M[Deactivate Account]
    end

    subgraph Administrator
        H[Edit All Entries]
        I[Delete All Entries]
        J[User Management]
        K[Unlock Accounts]
        L[Grant/Revoke Admin]
        N[Manage Deactivated Users' Entries]
    end

    Regular User -->|inherits| Non-logged-in User
    Administrator -->|inherits| Regular User
```

## 5. ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    users {
        int id PK "Auto-increment"
        string userid UK "User ID (4-20 chars)"
        string name "Display Name (3-20 chars)"
        string password "Password (hashed)"
        boolean is_admin "Admin Flag"
        boolean is_locked "Lock Flag"
        boolean is_visible "Account Status"
        int login_attempts "Login Attempt Count"
        datetime last_login_attempt "Last Login Attempt"
        datetime created_at "Creation Time"
    }

    entries {
        int id PK "Auto-increment"
        int user_id FK "Author ID"
        string title "Title"
        text content "Content"
        text notes "Notes (weather, mood, health, etc.)"
        datetime created_at "Creation Time"
        datetime updated_at "Update Time"
    }

    diary_items {
        int id PK "Auto-increment"
        int entry_id FK "Diary Entry ID"
        string item_name "Item Name"
        text item_content "Item Content"
        datetime created_at "Creation Time"
    }

    users ||--o{ entries : "creates"
    entries ||--o{ diary_items : "contains"
```

## 6. Activity Diagrams

### Login Process

```mermaid
flowchart TD
    A[Start] --> B[Display Login Form]
    B --> C[Enter User ID/Password]
    C --> D{User exists and visible?}
    D -->|Yes| E{Account locked?}
    D -->|No| F[Error: User not found]
    F --> B
    
    E -->|Yes| G[Error: Account is locked]
    G --> B
    E -->|No| H{Password matches?}
    
    H -->|Yes| I[Reset login attempts]
    I --> J[Create session]
    J --> K[Redirect to homepage]
    K --> L[End]
    
    H -->|No| M[Increment login attempts]
    M --> N{attempts >= 3?}
    N -->|Yes| O[Lock account]
    O --> P[Error: Account has been locked]
    P --> B
    N -->|No| Q[Error: Invalid password]
    Q --> B
```

### Account Deactivation Process

```mermaid
flowchart TD
    A[Start] --> B[Click Deactivate Button]
    B --> C[Show Confirmation Modal]
    C --> D[Enter Password]
    D --> E{Admin Account?}
    E -->|Yes| F[Error: Admin cannot be deactivated]
    F --> C
    E -->|No| G{Password correct?}
    G -->|No| H[Error: Invalid password]
    H --> C
    G -->|Yes| I[Set account to invisible]
    I --> J[Delete session]
    J --> K[Redirect to login]
    K --> L[End]
```

## 7. Component Diagram

### System Architecture

```mermaid
graph TB
    subgraph Frontend
        A[style.css]
        B[admin.css]
        C[user.css]
        D[main.css]
        E[script.js]
    end

    subgraph Templates
        F[index.html]
        G[login.html]
        H[register.html]
        I[settings.html]
        J[admin.html]
    end

    subgraph Backend
        K[app.py]
        subgraph Models
            L1[base.py]
            L2[user.py]
            L3[entry.py]
            L4[diary_item.py]
            L5[user_manager.py]
            L6[init_data.py]
            L7[models.py]
        end
        M[database.py]
        N[schema.sql]
        O[alembic.ini]
    end

    subgraph Database
        P[diary.db]
    end

    subgraph Migrations
        Q[versions/]
    end

    subgraph Tests
        R[pytest.ini]
        S[test_user.py]
        T[test_entry.py]
        U[test_user_manager.py]
        V[conftest.py]
    end

    %% Frontend Dependencies
    F --> A
    G --> A
    H --> A
    I --> A
    I --> C
    J --> A
    J --> B
    F --> D
    G --> D
    H --> D
    I --> D
    J --> D

    %% Template Dependencies
    F --> E
    G --> E
    H --> E
    I --> E
    J --> E

    %% Backend Dependencies
    K --> L1
    L2 --> L1
    L3 --> L1
    L4 --> L1
    L5 --> L2
    K --> M
    M --> N
    M --> P
    O --> Q

    %% Test Dependencies
    S --> L2
    T --> L3
    U --> L5
    V --> K

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style K fill:#bfb,stroke:#333,stroke-width:2px
    style L1 fill:#bfb,stroke:#333,stroke-width:2px
    style L2 fill:#bfb,stroke:#333,stroke-width:2px
    style L3 fill:#bfb,stroke:#333,stroke-width:2px
    style L4 fill:#bfb,stroke:#333,stroke-width:2px
    style L5 fill:#bfb,stroke:#333,stroke-width:2px
    style L6 fill:#bfb,stroke:#333,stroke-width:2px
    style L7 fill:#bfb,stroke:#333,stroke-width:2px
    style M fill:#bfb,stroke:#333,stroke-width:2px
    style O fill:#bfb,stroke:#333,stroke-width:2px
    style P fill:#ff9,stroke:#333,stroke-width:2px
    style S fill:#9f9,stroke:#333,stroke-width:2px
    style T fill:#9f9,stroke:#333,stroke-width:2px
    style U fill:#9f9,stroke:#333,stroke-width:2px
    style V fill:#9f9,stroke:#333,stroke-width:2px
```

### Development Environment Configuration

```mermaid
graph TB
    subgraph Python Environment
        A[conda]
        B[Python 3.11]
    end

    subgraph Core Packages
        C[Flask 3.1.0]
        D[SQLAlchemy 2.0.36]
        E[Flask-SQLAlchemy 3.1.1]
        F[Alembic 1.14.0]
        G[Flask-WTF 1.2.1]
        H[WTForms 3.1.2]
    end

    subgraph Testing Tools
        I[pytest 8.3.4]
        J[pytest-cov 6.0.0]
        K[coverage 7.6.9]
    end

    subgraph Utility Tools
        L[pyppeteer 2.0.0]
        M[pyyaml 6.0.2]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    B --> J
    B --> K
    B --> L
    B --> M

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style E fill:#bfb,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
    style H fill:#bfb,stroke:#333,stroke-width:2px
    style I fill:#9f9,stroke:#333,stroke-width:2px
    style J fill:#9f9,stroke:#333,stroke-width:2px
    style K fill:#9f9,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#bbf,stroke:#333,stroke-width:2px
```

### Directory Structure

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
└── tests/            # Test Files
│   ├── conftest.py   # Test Configuration
│   ├── test_user.py  # User Tests
│   ├── test_entry.py # Entry Tests
│   └── test_user_manager.py # User Manager Tests
└── docs/             # Documentation
    ├── specification.md     # Specifications (English)
    ├── specification_ja.md  # Specifications (Japanese)
    ├── diagrams.md         # Design Diagrams (English)
    └── diagrams_ja.md      # Design Diagrams (Japanese)
    ```

## 8. Additional Notes: Database Constraints

### users Table
- `id`: Auto-incrementing primary key
- `userid`: Unique constraint, alphanumeric only (4-20 characters)
- `name`: Any character type (3-20 characters)
- `password`: 8-20 characters (must include uppercase, lowercase, and numbers)
- `is_admin`: Default false
- `is_locked`: Default false
- `is_visible`: Default true (false when deactivated)
- `login_attempts`: Default 0
- `last_login_attempt`: NULL allowed
- `created_at`: NOT NULL

### entries Table
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key (users.id), NOT NULL, ON DELETE CASCADE
- `title`: NOT NULL
- `content`: NOT NULL
- `notes`: NOT NULL, default empty string
- `created_at`: NOT NULL
- `updated_at`: NULL allowed (set only on update)

### diary_items Table
- `id`: Auto-incrementing primary key
- `entry_id`: Foreign key (entries.id), NOT NULL, ON DELETE CASCADE
- `item_name`: NOT NULL
- `item_content`: NOT NULL
- `created_at`: NOT NULL
