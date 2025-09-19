# Learning Fish Tank (Prototype)

## 1) セットアップ
```bash
cd learning-fish-tank
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

ルートに `.env` を作成（`.env.example` をコピー）して **YouTube Data API Key** を設定：
```env
YOUTUBE_API_KEY=YOUR_YOUTUBE_DATA_API_KEY
```

## 2) 起動
```bash
streamlit run app/main.py
```

## 3) できること
- URL登録 → タイトル/サムネ自動取得 → 疑似サマリ付与 → DB保存（SQLite）
- 視聴ボタンで回数カウント & 忘却曲線による金魚の health/weight 更新
- 視聴一覧（期限超過フィルタあり）
- 水槽（円の濃さ=health、サイズ=weight）
