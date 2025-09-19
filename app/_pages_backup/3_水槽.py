import streamlit as st
from sqlmodel import select
from PIL import Image, ImageDraw
from lib.db import get_session
from lib.models import Fish

st.title("3. 水槽（簡易）")

# キャンバス画像を生成（透明度=health、サイズ=weight）
W, H = 900, 500
img = Image.new("RGBA", (W, H), (230, 244, 255, 255))
draw = ImageDraw.Draw(img)

with get_session() as ses:
    fishes = ses.exec(select(Fish)).all()

n = max(1, len(fishes))
gap = W // (n+1)
x = gap
y = H//2
for f in fishes:
    radius = max(10, min(80, f.weight_g // 3))
    alpha = max(30, min(255, int(255 * (f.health/100))))
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(255, 99, 71, alpha), outline=(0,0,0,100))
    x += gap

st.image(img, caption="healthが低いほど薄く、weightが小さくなる（弱る）", use_container_width=True)
