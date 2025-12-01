# HugHigh Login Backend

下妻第一高校 非認知能力可視化アプリ - ログイン機能（バックエンド）

## 概要

RFP準拠のログイン機能を提供するFastAPIアプリケーション。

### 主要機能
- ✅ Google OAuth 2.0 認証（完全事前登録制）
- ✅ 3ロール権限管理（生徒0/教員1/管理者2）
- ✅ 管理者用ユーザー管理機能
- ✅ 認証ログ記録（セキュリティ監査）

## 技術スタック

- **Python**: 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Async)
- **Database**: Azure MySQL Flexible Server
- **Authentication**: Google OAuth 2.0 + JWT
- **Package Manager**: uv

## セットアップ

### 1. 依存関係のインストール

```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 依存関係のインストール
uv sync
```

### 2. 環境変数の設定

`.env`ファイルを作成（`.env.example`を参考に）：

```bash
cp .env.example .env
```

必要な環境変数：
- `DB_NAME=hughigh_askrfp` ← HugHighアプリ用DB
- `GOOGLE_CLIENT_ID`: Google Cloud Consoleで取得
- `GOOGLE_CLIENT_SECRET`: Google Cloud Consoleで取得

### 3. SSL証明書のダウンロード

```bash
curl -o DigiCertGlobalRootG2.crt.pem https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem
```

### 4. データベースマイグレーション

```bash
# マイグレーション実行
uv run alembic upgrade head
```

### 5. アプリケーション起動

```bash
# 開発モード
uv run fastapi dev main.py

# 本番モード
uv run fastapi run main.py
```

## API仕様

起動後、以下のURLでSwagger UIを確認：
- http://localhost:8000/docs

### エンドポイント一覧

#### 認証
- `GET /auth/google/login` - Google認証URL取得
- `GET /auth/google/callback` - Google認証コールバック
- `POST /auth/logout` - ログアウト
- `GET /auth/me` - 現在のユーザー情報取得

#### 管理者機能（role=2のみ）
- `GET /admin/users` - ユーザー一覧
- `POST /admin/users` - ユーザー作成
- `GET /admin/users/{user_id}` - ユーザー詳細
- `PUT /admin/users/{user_id}` - ユーザー更新
- `DELETE /admin/users/{user_id}` - ユーザー削除

#### 生徒機能（role=0のみ）
- `GET /students/dashboard` - 生徒用ダッシュボード

#### 教員機能（role=1,2のみ）
- `GET /teachers/dashboard` - 教員用ダッシュボード

## データベーススキーマ

### users テーブル
| カラム | 型 | 説明 |
|--------|-----|------|
| id | CHAR(32) | UUID（主キー） |
| email | VARCHAR(255) | Googleメールアドレス（UK） |
| role | INTEGER | 0:生徒, 1:教員, 2:管理者 |
| google_sub | VARCHAR(255) | Google固有ID |
| name | VARCHAR(255) | 氏名（任意） |
| student_id | VARCHAR(50) | 学生番号（任意） |
| class_name | VARCHAR(50) | クラス（任意） |

### auth_logs テーブル
| カラム | 型 | 説明 |
|--------|-----|------|
| id | CHAR(32) | UUID（主キー） |
| user_id | CHAR(32) | ユーザーID（FK、NULL可） |
| timestamp | DATETIME | イベント発生日時 |
| event_type | VARCHAR(50) | イベント種別 |
| ip_address | VARCHAR(45) | IPアドレス |
| user_agent | TEXT | User-Agent |
| error_code | VARCHAR(50) | エラーコード |

## 開発

### テスト実行

```bash
uv run pytest
```

### コードフォーマット

```bash
uv run black .
uv run ruff check .
```

## デプロイ

（デプロイ手順は要追加）

## ライセンス

非公開プロジェクト
