import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from sqlmodel import select
from PIL import Image, ImageDraw

from lib.db import init_db, get_session
from lib.models import Video, View, Fish
from lib.youtube import fetch_meta
from lib.summary import simple_summary
from lib.forgetting import update_fish_state

# ====== 初期化 & テーマ/スタイル ======
load_dotenv()
st.set_page_config(page_title="Learning Fish Tank", page_icon="🐟", layout="wide")
init_db()

# ---- 赤グラデCSS（お好みで） ----
RED_CSS = """
<style>
.stApp { background: linear-gradient(135deg, #B30000 0%, #FF6B6B 40%, #FFE3E3 100%); }
.block-container { padding-top: 1.2rem; }
section[data-testid="stSidebar"] > div {
  background: rgba(255,255,255,0.88); backdrop-filter: blur(4px);
}
img, .stImage, .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div>div {
  border-radius: 14px !important; box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}
h1, h2 { color: #FFF; text-shadow: 0 2px 8px rgba(0,0,0,0.25); }
</style>
"""
st.markdown(RED_CSS, unsafe_allow_html=True)

# ====== ヘッダ ======
st.title("🐟 Learning Fish Tank")
st.caption("URL登録 → 要約 → 忘却曲線 → 金魚で可視化｜1ページ版")

# ====== タブ構成 ======
tab_reg, tab_list, tab_tank = st.tabs(["① 動画登録", "② 視聴一覧", "③ 水槽"])

# ====== ① 動画登録 ======
with tab_reg:
    st.subheader("YouTube URL を登録")
    url = st.text_input("YouTube URL")
    colA, colB = st.columns([1, 3])
    with colA:
        register = st.button("登録する", type="primary")
    with colB:
        st.caption("タイトル/サムネはAPI→oEmbed→静的URLの順で自動取得します。")

    if register:
        if not url:
            st.error("URLを入れてください")
            st.stop()
        with st.spinner("メタ情報を取得中..."):
            meta = fetch_meta(url)

        with get_session() as ses:
            v = Video(url=url, video_id=meta["video_id"], title=meta["title"],
                      description=meta["description"], thumbnail_url=meta["thumbnail_url"])
            ses.add(v); ses.commit(); ses.refresh(v)

            # 疑似サマリをdescriptionへ追記
            summ, kws = simple_summary(v.title, v.description or "")
            v.description = f"{summ}\nKeywords: {kws}"
            ses.add(v)

            # 金魚初期化（未視聴で自然減衰を一度通す）
            f = Fish(video_id=v.id)
            update_fish_state(f, datetime.utcnow(), reviewed_today=False)
            ses.add(f)

            ses.commit()
        st.success("登録しました！")

# ====== ② 視聴一覧 ======
with tab_list:
    st.subheader("動画カード一覧")
    col1, col2 = st.columns([1, 3])
    with col1:
        show_overdue = st.toggle("期限超過のみ", value=False, help="next_due を過ぎたものだけ表示")
    with col2:
        st.caption("カードの『視聴した！』で回数+1 & 金魚が太ります。")

    with get_session() as ses:
        vids = ses.exec(select(Video).order_by(Video.created_at.desc())).all()

    for v in vids:
        with get_session() as ses:
            fish = ses.exec(select(Fish).where(Fish.video_id==v.id)).first()
            views = ses.exec(select(View).where(View.video_id==v.id)).all()
            views_count = len(views)

        # フィルタ
        if show_overdue:
            if not fish or not fish.next_due or fish.next_due >= datetime.utcnow():
                continue

        # カードUI
        c1, c2 = st.columns([1, 2])
        with c1:
            if v.thumbnail_url:
                st.image(v.thumbnail_url, use_container_width=True)
        with c2:
            st.markdown(f"### {v.title}")
            st.caption(v.url)
            if v.description:
                st.write(v.description[:220] + ("..." if len(v.description) > 220 else ""))
            st.write(f"**視聴回数:** {views_count}")
            if fish:
                meta = []
                meta.append(f"health: {fish.health}")
                meta.append(f"weight: {fish.weight_g}g")
                meta.append(f"状態: {fish.status}")
                if fish.next_due:
                    meta.append(f"次回復習: {fish.next_due.strftime('%Y-%m-%d')}")
                st.write(" / ".join(meta))

            # 視聴ボタン
            btn_key = f"view_{v.id}"
            if st.button("視聴した！", key=btn_key):
                with get_session() as s2:
                    s2.add(View(video_id=v.id))
                    f2 = s2.exec(select(Fish).where(Fish.video_id==v.id)).first()
                    update_fish_state(f2, datetime.utcnow(), reviewed_today=True)
                    s2.add(f2); s2.commit()
                st.experimental_rerun()

        st.divider()

# ====== ③ 水槽（簡易） ======
with tab_tank:
    st.subheader("金魚の水槽（health=透明度 / weight=サイズ）")

    # パッシブ減衰（今日は未視聴扱い）を、タンク表示前に一括適用してもOK
    if st.button("水槽表示前に“今日の自然減衰”を適用", help="全ての金魚の状態を現時点に更新します"):
        with get_session() as ses:
            fishes = ses.exec(select(Fish)).all()
            for f in fishes:
                update_fish_state(f, datetime.utcnow(), reviewed_today=False)
                ses.add(f)
            ses.commit()
        st.success("適用しました。")

    W, H = 1000, 520
    img = Image.new("RGBA", (W, H), (255, 245, 245, 255))  # 薄ピンクの水槽
    draw = ImageDraw.Draw(img)

    with get_session() as ses:
        fishes = ses.exec(select(Fish)).all()

    n = max(1, len(fishes))
    gap = W // (n+1)
    x = gap
    y = H//2
    for f in fishes:
        radius = max(12, min(90, f.weight_g // 3))
        alpha = max(30, min(255, int(255 * (f.health/100))))
        # 楕円で“金魚っぽさ”を少し出す
        draw.ellipse((x-radius-6, y-radius, x+radius+6, y+radius), fill=(255, 90, 90, alpha), outline=(50,0,0,120))
        x += gap

    st.image(img, use_container_width=True, caption="弱ると薄く/小さく表示。太ると大きく濃く表示。")
