-- ユーザーテーブル
DROP TABLE IF EXISTS users;
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

-- 日記テーブル
DROP TABLE IF EXISTS entries;
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

-- 活動項目テーブル
DROP TABLE IF EXISTS diary_items;
CREATE TABLE diary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE
);

-- 初期ユーザーデータの挿入
INSERT INTO users (userid, name, password, is_admin, is_visible, created_at) VALUES 
    ('admin', '管理人', 'Admin3210', 1, 1, DATETIME('now')),
    ('tetsu', 'devilman', 'Tetsu3210', 0, 1, DATETIME('now')),
    ('gento', 'gen chan', 'Gento3210', 0, 1, DATETIME('now'));

-- サンプル日記データの挿入
-- 管理人の日記（1件）
INSERT INTO entries (user_id, title, content, notes, created_at) VALUES 
    (1, 'LifeLogの運営開始について', 
    '本日よりLifeLogの運営を開始しました。\n\n皆様に快適にご利用いただけるよう、以下のルールを設けさせていただきます：\n\n1. 他者への誹謗中傷は禁止\n2. 個人情報の投稿は控えめに\n3. 楽しく前向きな記録を心がけましょう\n\nご協力よろしくお願いいたします。',
    '天気：晴れ\n気分：わくわく',
    DATETIME('now', '-2 days'));

-- tetsuの日記（3件）
INSERT INTO entries (user_id, title, content, notes, created_at) VALUES 
    (2, '試合に向けて本格始動', 
    '今日から本格的なトレーニング期間に入る。\n\n朝一番でランニングから始めて、午後はジムでの練習。\n\n来月の試合までに必ず仕上げる！',
    '体重：75kg\n体調：絶好調\n気温：20℃',
    DATETIME('now', '-5 days')),
    (2, 'トレーニング経過', 
    '減量は予定通り。体重も順調に落ちてきている。\nパワーも維持できているので、この調子で進めていく。',
    '体重：73kg\n体調：良好\n天気：曇り',
    DATETIME('now', '-3 days')),
    (2, '仕上げの段階', 
    '新しい技が決まるようになってきた。\n相手の動きを読んでからの技の出し方が特に良くなってきている。\n\n後は調整あるのみ。',
    '体重：72kg\n体調：快調\n気分：充実',
    DATETIME('now', '-1 days'));

-- gentoの日記（2件）
INSERT INTO entries (user_id, title, content, notes, created_at) VALUES 
    (3, '新プロジェクト始動', 
    'チーム開発の新プロジェクトが始動。\n\n担当はフロントエンド。\n技術スタックの選定から任されているので、しっかり調査する。',
    '天気：雨\n体調：普通\n気分：やる気満々',
    DATETIME('now', '-3 days')),
    (3, 'プロジェクト進行状況', 
    '基本設計が完了。\n明日からコーディング開始。\n\nTypeScriptとReactの組み合わせで行くことに決定。',
    '天気：晴れ\n集中度：高\n気分：充実',
    DATETIME('now', '-1 days'));

-- サンプル活動項目データの挿入
INSERT INTO diary_items (entry_id, item_name, item_content, created_at) VALUES
    -- tetsuの活動項目
    (2, '筋トレ', 'スクワット 30回×3セット\nベンチプレス 80kg×10回×3セット\n腹筋 50回×3セット', DATETIME('now', '-5 days')),
    (2, 'ランニング', '朝：10km（50分）\n夜：5km（25分）', DATETIME('now', '-5 days')),
    (2, '食事管理', '朝：プロテイン、バナナ\n昼：チキンサラダ、玄米\n夜：サーモン、ブロッコリー', DATETIME('now', '-5 days')),
    (3, '筋トレ', 'スクワット 30回×3セット\nデッドリフト 100kg×8回×3セット\n腹筋 50回×3セット', DATETIME('now', '-3 days')),
    (3, 'スパーリング', '5ラウンド×3人（各3分）\n新しいコンビネーションの練習', DATETIME('now', '-3 days')),
    (4, '練習メニュー', 'シャドーボクシング 30分\nミット打ち 10ラウンド\nスパーリング 5ラウンド', DATETIME('now', '-1 days')),
    -- gentoの活動項目
    (5, '技術調査', 'Next.js vs Remix\nTailwind vs CSS Modules\nテスト：Vitest vs Jest', DATETIME('now', '-3 days')),
    (5, 'ミーティング', '10:00- チーム全体MTG\n14:00- フロントエンドチームMTG\n16:00- 技術選定の相談', DATETIME('now', '-3 days')),
    (6, 'コーディング準備', 'プロジェクト初期設定\nESLint設定\nPrettier設定\nGitHubリポジトリ作成', DATETIME('now', '-1 days')),
    (6, '明日の作業予定', 'コンポーネント設計\n認証機能の実装\nCIパイプラインの構築', DATETIME('now', '-1 days'));
