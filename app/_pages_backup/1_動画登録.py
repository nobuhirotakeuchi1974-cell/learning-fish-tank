import streamlit as st
from sqlmodel import select
from datetime import datetime
from lib.db import get_session
from lib.models import Video, Fish
from lib.youtube import fetch_meta
from lib.summary import simple_summary
from lib.forgetting import update_fish_state

st.title("1. 動画登録")

url = st.text_input("YouTube URL を入力")
if st.button("登録"):
    if not url:
        st.error("URLを入れてください")
        st.stop()

    with st.spinner("取得中..."):
        meta = fetch_meta(url)

    with get_session() as ses:
        v = Video(url=url, video_id=meta["video_id"], title=meta["title"],
                  description=meta["description"], thumbnail_url=meta["thumbnail_url"])
        ses.add(v); ses.commit(); ses.refresh(v)

        # 疑似サマリ：descriptionに追記（簡易）
        summ, kws = simple_summary(v.title, v.description or "")
        v.description = f"{summ}\nKeywords: {kws}"
        ses.add(v)

        # 金魚作成（初期値）
        f = Fish(video_id=v.id)
        update_fish_state(f, datetime.utcnow(), reviewed_today=False)
        ses.add(f)

        ses.commit()
        st.success("登録しました！")
