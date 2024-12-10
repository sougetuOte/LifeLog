# システム構成図

## データベースER図
```mermaid
erDiagram
    users ||--o{ entries : creates
    entries ||--o{ diary_items : contains
    
    users {
        integer id PK
        string userid
        string name
        string password
        boolean is_admin
        boolean is_locked
        boolean is_visible
        integer login_attempts
        datetime last_login_attempt
        datetime created_at
    }
    
    entries {
        integer id PK
        integer user_id FK
        string title
        string content
        string notes
        datetime created_at
        datetime updated_at
    }
    
    diary_items {
        integer id PK
        integer entry_id FK
        string item_name
        string item_content
        datetime created_at
    }
```

## クラス図
```mermaid
classDiagram
    class User {
        +int id
        +str userid
        +str name
        +str password
        +bool is_admin
        +bool is_locked
        +bool is_visible
        +int login_attempts
        +datetime last_login_attempt
        +datetime created_at
        +verify_password()
        +check_lock_status()
    }
    
    class Entry {
        +int id
        +int user_id
        +str title
        +str content
        +str notes
        +datetime created_at
        +datetime updated_at
        +update()
    }
    
    class DiaryItem {
        +int id
        +int entry_id
        +str item_name
        +str item_content
        +datetime created_at
    }
    
    User "1" --> "*" Entry
    Entry "1" --> "*" DiaryItem
```

## 更新履歴
- 2024/12/01: 0.01公開
- 2024/12/08: モデル構造の改善とテストの追加
- 2024/12/09: マイグレーション機能の追加
- 2024/12/10: 開発環境をcondaベースに変更
