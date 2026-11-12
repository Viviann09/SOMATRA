import random
import streamlit as st

# Konfigurasi
st.set_page_config(
    page_title="Klasifikasi Motif Kain Songket",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from motif_data import MOTIF_DATA
from shared import CSS_PATH, PAGES, tampilkan_footer
from pages_app.beranda import halaman_beranda
from pages_app.klasifikasi import halaman_klasifikasi
from pages_app.informasi import halaman_informasi

with open(CSS_PATH, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

if "hasil_klasifikasi" not in st.session_state:
    st.session_state["hasil_klasifikasi"] = None

if "gambar_asli_bytes" not in st.session_state:
    st.session_state["gambar_asli_bytes"] = None

if "beranda_urutan" not in st.session_state:
    urutan = list(MOTIF_DATA.keys())
    random.shuffle(urutan)
    st.session_state["beranda_urutan"] = urutan

if "beranda_idx" not in st.session_state:
    st.session_state["beranda_idx"] = 0

if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = 0

# Navigasi
PAGES.update({
    "Beranda": st.Page(
        halaman_beranda, title="Beranda", url_path="", default=True
    ),
    "Klasifikasi": st.Page(
        halaman_klasifikasi, title="Klasifikasi", url_path="klasifikasi"
    ),
    "Informasi": st.Page(
        halaman_informasi, title="Informasi", url_path="informasi"
    ),
})

pg = st.navigation(list(PAGES.values()), position="hidden")

with st.container(key="top_nav"):
    nav_col, menu_col = st.columns([8, 2])

    with nav_col:
        st.markdown(
            '<div class="brand">⚜️ SOMATRA</div>',
            unsafe_allow_html=True,
        )

    with menu_col:
        cols_menu = st.columns([1, 1, 1], gap=None)

    for col, item in zip(
        cols_menu, ["Beranda", "Klasifikasi", "Informasi"]
    ):
        with col:
            with st.container(key=f"nav_{item}"):
                st.page_link(PAGES[item], label=item)

st.markdown(
    f"""
    <style>
    .st-key-nav_{pg.title} a {{
        border-bottom: 2px solid #7A1F2B !important;
    }}
    .st-key-nav_{pg.title} a p {{
        color: #171717 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

pg.run()
tampilkan_footer()