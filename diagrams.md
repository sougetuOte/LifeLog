# シンプル日記アプリケーション - 設計図

## 1. 画面遷移図

```mermaid
stateDiagram-v2
    [*] --> トップページ
    
    state "未ログイン" as Guest {
        トップページ --> ログイン
        トップページ --> 新規登録
        ログイン --> トップページ: ログイン成功
        新規登録 --> ログイン: 登録成功
    }

    state "ログインユーザー" as User {
        state "一般ユーザー機能" as Normal {
            トップページ --> ユーザー設定
            ユーザー設定 --> トップページ
            ユーザー設定 --> ログイン: 退会完了
        }
    }

    state "管理者" as Admin {
        state "管理者機能" as AdminFunc {
            トップページ --> ユーザー管理
            ユーザー管理 --> トップページ
        }
    }

    トップページ --> [*]: ログアウト
```

## 2. クラス図

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

## 3. シーケンス図

### ログインプロセス

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: ログイン情報入力
    Frontend->>Backend: POST /api/login
    Backend->>Database: ユーザー検索（is_visible=1）
    Database-->>Backend: ユーザー情報
    
    alt ユーザーが存在し可視状態
        alt パスワードが正しい
            Backend->>Database: ログイン試行回数リセット
            Backend-->>Frontend: 成功レスポンス
            Frontend->>Frontend: トップページへリダイレクト
        else パスワードが間違っている
            Backend->>Database: ログイン試行回数増加
            alt 試行回数 >= 3
                Backend->>Database: アカウントをロック
                Backend-->>Frontend: ロックエラー
            else 試行回数 < 3
                Backend-->>Frontend: 認証エラー
            end
        end
    else ユーザーが存在しないまたは退会済み
        Backend-->>Frontend: 認証エラー
    end
```

### 退会プロセス

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: 退会ボタンクリック
    Frontend->>Frontend: 確認モーダル表示
    User->>Frontend: パスワード入力
    Frontend->>Backend: POST /api/user/deactivate
    Backend->>Database: パスワード検証
    
    alt パスワードが正しい
        alt 管理者でない
            Backend->>Database: is_visible=0に更新
            Backend-->>Frontend: 成功レスポンス
            Frontend->>Frontend: ログイン画面へリダイレクト
        else 管理者である
            Backend-->>Frontend: エラー: 管理者は退会不可
        end
    else パスワードが間違っている
        Backend-->>Frontend: 認証エラー
    end
```
### 日記投稿プロセス

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: タイトル・本文・メモを入力
    Frontend->>Backend: POST /entries
    Backend->>Database: ユーザーの可視性チェック
    Database-->>Backend: ユーザー情報
    
    alt ユーザーが可視状態
        Backend->>Database: 日記を保存
        Backend-->>Frontend: 成功レスポンス
        Frontend->>Frontend: フォームをクリア
        Frontend->>Backend: GET /entries
        Backend->>Database: 日記一覧取得
        Database-->>Backend: 日記データ
        Backend-->>Frontend: 日記一覧
        Frontend->>Frontend: 一覧を更新
    else ユーザーが退会済み
        Backend-->>Frontend: エラー: アカウントが無効
    end
```


## 4. ユースケース図

```mermaid
graph TB
    subgraph 未ログインユーザー
        A[日記一覧閲覧]
        B[ログイン]
        C[新規登録]
    end

    subgraph 一般ユーザー
        D[日記投稿]
        E[自分の日記編集]
        F[自分の日記削除]
        G[ユーザー設定変更]
        M[アカウント退会]
    end

    subgraph 管理者
        H[全ユーザーの日記編集]
        I[全ユーザーの日記削除]
        J[ユーザー管理]
        K[アカウントロック解除]
        L[管理者権限付与/削除]
        N[退会済みユーザーの日記管理]
    end

    一般ユーザー -->|継承| 未ログインユーザー
    管理者 -->|継承| 一般ユーザー
```

## 5. ERD（Entity Relationship Diagram）

```mermaid
erDiagram
    users {
        int id PK
        string userid UK "ユーザーID（4-20文字）"
        string name "表示名（3-20文字）"
        string password "パスワード（ハッシュ化）"
        boolean is_admin "管理者フラグ"
        boolean is_locked "ロックフラグ"
        boolean is_visible "アカウント状態"
        int login_attempts "ログイン試行回数"
        datetime last_login_attempt "最終ログイン試行日時"
        datetime created_at "作成日時"
    }

    entries {
        int id PK
        int user_id FK "作成者ID"
        string title "タイトル"
        text content "本文"
        text notes "メモ（天気・気分・体調など）"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }

    users ||--o{ entries : "creates"
```

## 6. アクティビティ図

### ログインプロセス

```mermaid
flowchart TD
    A[開始] --> B[ログインフォーム表示]
    B --> C[ユーザーID/パスワード入力]
    C --> D{ユーザーが存在し可視状態?}
    D -->|Yes| E{アカウントがロックされている?}
    D -->|No| F[エラー: ユーザーが見つかりません]
    F --> B
    
    E -->|Yes| G[エラー: アカウントがロックされています]
    G --> B
    E -->|No| H{パスワードが一致する?}
    
    H -->|Yes| I[ログイン試行回数をリセット]
    I --> J[セッション作成]
    J --> K[トップページへリダイレクト]
    K --> L[終了]
    
    H -->|No| M[ログイン試行回数を増加]
    M --> N{試行回数 >= 3?}
    N -->|Yes| O[アカウントをロック]
    O --> P[エラー: アカウントがロックされました]
    P --> B
    N -->|No| Q[エラー: パスワードが正しくありません]
    Q --> B
```

### 退会プロセス

```mermaid
flowchart TD
    A[開始] --> B[退会ボタンクリック]
    B --> C[確認モーダル表示]
    C --> D[パスワード入力]
    D --> E{管理者アカウント?}
    E -->|Yes| F[エラー: 管理者は退会不可]
    F --> C
    E -->|No| G{パスワードが正しい?}
    G -->|No| H[エラー: パスワードが正しくありません]
    H --> C
    G -->|Yes| I[アカウントを非表示に設定]
    I --> J[セッション削除]
    J --> K[ログイン画面へリダイレクト]
    K --> L[終了]
```

## 7. コンポーネント図

### システムアーキテクチャ

```mermaid
graph TB
    subgraph フロントエンド
        A[main.css]
        B[admin.css]
        C[user.css]
        D[script.js]
    end

    subgraph テンプレート
        E[index.html]
        F[login.html]
        G[register.html]
        H[settings.html]
        I[admin.html]
    end

    subgraph バックエンド
        J[app.py]
        K[schema.sql]
    end

    subgraph データベース
        L[diary.db]
    end

    %% フロントエンド依存関係
    E --> A
    F --> A
    G --> A
    H --> A
    H --> C
    I --> A
    I --> B

    %% テンプレート依存関係
    E --> D
    F --> D
    G --> D
    H --> D
    I --> D

    %% バックエンド依存関係
    J --> K
    J --> L

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#bfb,stroke:#333,stroke-width:2px
    style L fill:#ff9,stroke:#333,stroke-width:2px
```

### ディレクトリ構造

```
/
├── app.py              # メインアプリケーション
├── schema.sql          # データベーススキーマ
├── diary.db           # SQLiteデータベース
├── requirements.txt    # 依存パッケージリスト
├── static/            # 静的ファイル
│   ├── main.css       # 共通スタイル
│   ├── admin.css      # 管理画面スタイル
│   ├── user.css       # ユーザー設定スタイル
│   └── script.js      # クライアントサイドスクリプト
└── templates/         # HTMLテンプレート
    ├── index.html     # トップページ
    ├── login.html     # ログインページ
    ├── register.html  # ユーザー登録ページ
    ├── settings.html  # ユーザー設定ページ
    └── admin.html     # 管理者ページ
```


## 8. 補足：データベース制約

### usersテーブル
- `id`: 自動増分の主キー
- `userid`: 一意制約、半角英数字のみ（4-20文字）
- `name`: 文字種自由（3-20文字）
- `password`: 8-20文字（大文字・小文字・数字を含む）
- `is_admin`: デフォルトfalse
- `is_locked`: デフォルトfalse
- `is_visible`: デフォルトtrue（退会するとfalse）
- `login_attempts`: デフォルト0
- `created_at`: NOT NULL

### entriesテーブル
- `id`: 自動増分の主キー
- `user_id`: 外部キー（users.id）、NOT NULL
- `title`: NOT NULL
- `content`: NOT NULL
- `notes`: NOT NULL、デフォルト空文字列
- `created_at`: NOT NULL
- `updated_at`: NULL許容（更新時のみ設定）
