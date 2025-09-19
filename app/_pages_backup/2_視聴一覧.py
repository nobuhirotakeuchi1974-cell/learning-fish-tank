import streamlit as st
from sqlmodel import select
from datetime import datetime
from lib.db import get_session
from lib.models import Video, View, Fish
from lib.forgetting import update_fish_state
from lib.ui import video_card

st.title("2. 視聴一覧")

# フィルタ
show_overdue = st.toggle("期限超過のみ表示（next_due 過ぎ）", value=False)

with get_session() as ses:
    vids = ses.exec(select(Video).order_by(Video.created_at.desc())).all()

for v in vids:
    with get_session() as ses:
        fish = ses.exec(select(Fish).where(Fish.video_id==v.id)).first()

        # overdue フィルタ
        if show_overdue and (not fish or not fish.next_due or fish.next_due >= datetime.utcnow()):
            continue

        views = ses.exec(select(View).where(View.video_id==v.id)).all()
        views_count = len(views)

    def on_view():
        with get_session() as s2:
            s2.add(View(video_id=v.id))
            f = s2.exec(select(Fish).where(Fish.video_id==v.id)).first()
            update_fish_state(f, datetime.utcnow(), reviewed_today=True)
            s2.add(f); s2.commit()
        st.rerun()

    video_card(v, fish, views_count, on_view)
    st.divider()
