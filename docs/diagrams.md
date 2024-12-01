# LifeLog - Design Diagrams

## Version History
- 2024/12/01: Initial release 0.01

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
        +validate_password()
        +check_lock_status()
        +deactivate_account()
    }

    class Entry {
        +int id
        +int user_id
        +string title
        +string content
        +string notes
        +datetime created_at
        +datetime updated_at
        +create()
        +update()
        +delete()
    }

    class UserManager {
        +lock_user()
        +unlock_user()
        +toggle_admin()
        +update_login_attempts()
        +get_visible_users()
        +get_all_users()
    }

    User "1" -- "*" Entry : creates
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
        int id PK
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
        int id PK
        int user_id FK "Author ID"
        string title "Title"
        text content "Content"
        text notes "Notes (weather, mood, health, etc.)"
        datetime created_at "Creation Time"
        datetime updated_at "Update Time"
    }

    users ||--o{ entries : "creates"
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
        D[script.js]
    end

    subgraph Templates
        E[index.html]
        F[login.html]
        G[register.html]
        H[settings.html]
        I[admin.html]
    end

    subgraph Backend
        J[app.py]
        K[models.py]
        L[database.py]
        M[schema.sql]
    end

    subgraph Database
        N[diary.db]
    end

    %% Frontend Dependencies
    E --> A
    F --> A
    G --> A
    H --> A
    H --> C
    I --> A
    I --> B

    %% Template Dependencies
    E --> D
    F --> D
    G --> D
    H --> D
    I --> D

    %% Backend Dependencies
    J --> K
    J --> L
    L --> M
    L --> N

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#bfb,stroke:#333,stroke-width:2px
    style K fill:#bfb,stroke:#333,stroke-width:2px
    style L fill:#bfb,stroke:#333,stroke-width:2px
    style N fill:#ff9,stroke:#333,stroke-width:2px
```

### Directory Structure

```
/
├── app.py              # Main Application
├── models.py           # Data Models
├── database.py         # Database Operations
├── schema.sql          # Database Schema
├── alembic.ini         # Alembic Configuration
├── requirements.txt    # Package Dependencies
├── static/            # Static Files
│   ├── style.css      # Common Styles
│   ├── admin.css      # Admin Panel Styles
│   ├── user.css       # User Settings Styles
│   └── script.js      # Client-side Scripts
├── templates/         # HTML Templates
│   ├── index.html     # Homepage
│   ├── login.html     # Login Page
│   ├── register.html  # Registration Page
│   ├── settings.html  # User Settings Page
│   └── admin.html     # Admin Panel
├── instance/          # Instance-specific Files
│   └── diary.db      # SQLite Database
├── migrations/        # Database Migrations
└── docs/             # Documentation
    └── specification.md  # Specifications
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
- `created_at`: NOT NULL

### entries Table
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key (users.id), NOT NULL
- `title`: NOT NULL
- `content`: NOT NULL
- `notes`: NOT NULL, default empty string
- `created_at`: NOT NULL
- `updated_at`: NULL allowed (set only on update)
