import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path
from io import BytesIO
import html
import base64
import random
from motif_data import MOTIF_DATA

# Konfigurasi
st.set_page_config(
    page_title="Klasifikasi Motif Kain Songket",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model/model_mobilenetv1.keras"
CSS_PATH = BASE_DIR / "style.css"
with open(CSS_PATH, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

CLASS_NAMES = [
    "kain_songket_aceh_bungong_keupula",
    "kain_songket_jambi_angsa_duo",
    "kain_songket_jambi_duren_pecah",
    "kain_songket_jambi_kaco_piring",
    "kain_songket_minangkabau_biku_biku",
    "kain_songket_minangkabau_itik_pulang_patang",
    "kain_songket_minangkabau_kaluak_paku",
    "kain_songket_minangkabau_saik_galamai",
    "kain_songket_minangkabau_salapah",
    "kain_songket_minangkabau_tampuak_manggih",
    "kain_songket_palembang_bintang_berante",
    "kain_songket_palembang_bunga_cina",
    "kain_songket_palembang_cantik_manis",
    "kain_songket_palembang_nampan_perak",
    "kain_songket_palembang_pulir",
    "kain_songket_riau_awan_larat",
    "kain_songket_riau_pucuk_rebung",
    "kain_songket_riau_siku_awan",
    "kain_songket_riau_siku_keluang",
]

# Model dan fungsi bantu
@st.cache_resource
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

def format_nama(nama):
    return nama.replace("kain_songket_", "").replace("_", " ").title()

def ambil_info(kunci):
    data = MOTIF_DATA.get(kunci, {})
    return {
        "nama": data.get("nama", format_nama(kunci)),
        "daerah": data.get("daerah", "Informasi belum tersedia"),
        "sejarah": data.get(
            "sejarah",
            "Informasi sejarah motif ini belum ditambahkan.",
        ),
        "gambar": data.get("gambar", ""),
    }

def path_gambar_motif(relatif):
    if not relatif:
        return None

    path = (BASE_DIR / relatif).resolve()
    try:
        path.relative_to(BASE_DIR.resolve())
    except ValueError:
        return None

    return path if path.is_file() else None

def tampilkan_footer():
    st.markdown(
        '<div class="footer">'
        '© 2026 SOMATRA'
        '</div>',
        unsafe_allow_html=True,
    )

JUMLAH_TAMPIL = 4
MAKS_UKURAN_MB = 5
FORMAT_DIIZINKAN = (".jpg", ".jpeg", ".png")

@st.cache_data
def gambar_ke_data_uri(path_str, lebar_maks=800):
    img = Image.open(path_str).convert("RGB")
    img.thumbnail((lebar_maks, lebar_maks))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{data}"

def geser_motif(arah):
    total = len(st.session_state["beranda_urutan"])
    st.session_state["beranda_idx"] = (
        st.session_state["beranda_idx"] + arah * JUMLAH_TAMPIL
    ) % total

def pindah_halaman(nama):
    st.switch_page(PAGES[nama])

def reset_klasifikasi():
    st.session_state["hasil_klasifikasi"] = None
    st.session_state["gambar_asli_bytes"] = None
    st.session_state["upload_key"] += 1

def kembali_ke_beranda():
    st.switch_page(PAGES["Beranda"])

def prediksi_gambar(raw_bytes):
    """Kembalikan dict hasil, atau string pesan error."""
    try:
        image = Image.open(BytesIO(raw_bytes)).convert("RGB")
    except Exception:
        return "Gambar tidak dapat dibaca. Silakan unggah gambar lain."

    model = load_model()
    output_count = int(model.output_shape[-1])
    if output_count != len(CLASS_NAMES):
        return (
            f"Model memiliki {output_count} output, tetapi daftar kelas "
            f"berisi {len(CLASS_NAMES)} kelas. Periksa kembali model dan "
            "urutan kelas training."
        )

    img = image.resize((224, 224), Image.Resampling.BILINEAR)
    arr = np.asarray(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)

    pred = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(pred))
    kunci = CLASS_NAMES[idx]

    return {
        "nama_kunci": kunci,
        "confidence": float(pred[idx]),
        "info": ambil_info(kunci),
    }

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

# Halaman beranda
def halaman_beranda():
    reset_klasifikasi()

    hero_path = path_gambar_motif("assets/image_1.png")
    if hero_path:
        uri = gambar_ke_data_uri(str(hero_path))
        hero_img = f'<img src="{uri}" alt="Kain songket">'
    else:
        hero_img = ""

    col_teks, col_img = st.columns(
        [1.2, 1], gap="large", vertical_alignment="center"
    )

    with col_teks:
        st.markdown(
            """
            <div class="hero-text">
                <h1>Klasifikasi Motif Kain Songket Sumatra</h1>
                <p class="muted">
                    Website untuk mengidentifikasi motif kain songket Sumatra berdasarkan gambar yang diunggah oleh pengguna. 
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            "Mulai Klasifikasi",
            key="home_classify",
            on_click=pindah_halaman,
            args=("Klasifikasi",),
        )

    with col_img:
        st.markdown(
            f'<div class="hero-img">{hero_img}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-heading">Galeri Motif Songket</div>',
        unsafe_allow_html=True,
    )

    urutan = st.session_state["beranda_urutan"]
    total = len(urutan)

    if total:
        tampil = min(JUMLAH_TAMPIL, total)
        idx = st.session_state["beranda_idx"]
        terlihat = [urutan[(idx + i) % total] for i in range(tampil)]
        ada_panah = total > JUMLAH_TAMPIL

        lebar = [0.4] + [3] * tampil + [0.4]
        cols = st.columns(lebar, gap="small", vertical_alignment="center")

        with cols[0]:
            if ada_panah:
                st.button(
                    "‹", key="prev_motif",
                    on_click=geser_motif, args=(-1,),
                )

        for col, key in zip(cols[1:-1], terlihat):
            data = MOTIF_DATA[key]
            nama = html.escape(data.get("nama", format_nama(key)))
            daerah = html.escape(data.get("daerah", "Daerah belum diisi"))
            image_path = path_gambar_motif(data.get("gambar", ""))

            if image_path:
                uri = gambar_ke_data_uri(str(image_path))
                img_html = f'<img src="{uri}" alt="{nama}">'
            else:
                img_html = '<div class="motif-noimg">Foto belum ada</div>'

            with col:
                st.markdown(
                    f'<div class="motif-card">'
                    f'<div class="motif-card-img">{img_html}</div>'
                    f'<div class="motif-card-body">'
                    f'<div class="card-title">{nama}</div>'
                    f'<div class="card-meta">{daerah}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        with cols[-1]:
            if ada_panah:
                st.button(
                    "›", key="next_motif",
                    on_click=geser_motif, args=(1,),
                )

    st.button(
        "Lihat Semua Informasi Motif",
        key="home_info",
        on_click=pindah_halaman,
        args=("Informasi",),
    )

# Halaman klasifikasi
def halaman_klasifikasi():
    hasil = st.session_state["hasil_klasifikasi"]
    if hasil is None:
        _, tengah, _ = st.columns([1.2, 2, 1.2])

        with tengah:
            with st.container(key="panel_upload"):
                st.markdown(
                    '<div class="panel-title">Upload Gambar Motif Kain Songket</div>'
                    '<p class="muted panel-sub">Upload motif kain songket di bawah '
                    'ini untuk memulai klasifikasi</p>',
                    unsafe_allow_html=True,
                )

                uploaded = st.file_uploader(
                    "Pilih gambar kain songket",
                    key=f"upload_motif_{st.session_state['upload_key']}",
                    label_visibility="collapsed",
                )

                pesan_error = None
                if uploaded is not None:
                    if not uploaded.name.lower().endswith(FORMAT_DIIZINKAN):
                        pesan_error = (
                            "Silakan upload gambar dalam format JPG atau PNG."
                        )
                    elif uploaded.size > MAKS_UKURAN_MB * 1024 * 1024:
                        pesan_error = (
                            f"Ukuran gambar terlalu besar. "
                            f"Maksimal {MAKS_UKURAN_MB} MB."
                        )

                if pesan_error:
                    st.error(pesan_error)

                klik = st.button("Mulai Klasifikasi", key="btn_prediksi")

                if klik:
                    if uploaded is None:
                        st.warning("Silakan pilih gambar terlebih dahulu.")
                    elif pesan_error is None:
                        raw_bytes = uploaded.getvalue()

                        with st.spinner("Sedang mengidentifikasi motif..."):
                            hasil_baru = prediksi_gambar(raw_bytes)

                        if isinstance(hasil_baru, str):
                            st.error(hasil_baru)
                        else:
                            st.session_state["hasil_klasifikasi"] = hasil_baru
                            st.session_state["gambar_asli_bytes"] = raw_bytes
                            st.rerun()
    else:
        st.markdown(
            '<div class="panel-title result-title">'
            'Hasil Klasifikasi Motif Kain Songket</div>',
            unsafe_allow_html=True,
        )

        info = hasil["info"]
        image_bytes = st.session_state["gambar_asli_bytes"]

        _, kiri, kanan, _ = st.columns(
            [0.5, 1, 1.6, 0.5], gap="small", vertical_alignment="center"
        )

        with kiri:
            if image_bytes:
                st.image(
                    Image.open(BytesIO(image_bytes)).convert("RGB"),
                    caption="Gambar yang diklasifikasikan",
                    width=260,
                )

        with kanan:
            with st.container(key="panel_hasil"):
                st.markdown(f"**Nama Motif:** {info['nama']}")
                st.markdown(f"**Asal Daerah:** {info['daerah']}")
                st.markdown(
                    f"**Tingkat Keyakinan:** {hasil['confidence'] * 100:.2f}%"
                )
                st.markdown("**Sejarah Singkat:**")
                st.markdown(
                    f'<div class="sejarah-teks">'
                    f'{html.escape(str(info["sejarah"]))}</div>',
                    unsafe_allow_html=True,
                )

        st.button(
            "Kembali ke Beranda",
            key="btn_beranda",
            on_click=kembali_ke_beranda,
        )

# Halaman Informasi
def halaman_informasi():
    reset_klasifikasi()

    st.markdown(
        '<div class="section-heading" style="text-align:center;'
        'font-size:30px;margin-top:0;margin-bottom:30px;">'
        'Daftar Motif Kain Songket Sumatra</div>',
        unsafe_allow_html=True,
    )

    items = list(MOTIF_DATA.items())

    if not items:
        st.info("Belum ada data motif yang tersedia.")
    else:
        kartu = []
        for key, data in items:
            nama = html.escape(data.get("nama", format_nama(key)))
            daerah = html.escape(data.get("daerah", "Informasi belum tersedia"))
            sejarah = html.escape(
                str(data.get("sejarah", "Informasi sejarah belum ditambahkan."))
            )
            image_path = path_gambar_motif(data.get("gambar", ""))

            if image_path:
                uri = gambar_ke_data_uri(str(image_path), 500)
                img_html = f'<img src="{uri}" alt="{nama}">'
            else:
                img_html = '<div class="motif-noimg">Foto belum ada</div>'

            kartu.append(
                '<div class="info-card">'
                f'<div class="info-img">{img_html}</div>'
                f'<div class="info-body">'
                f'<h3>{nama}</h3>'
                f'<p class="info-daerah"><b>Asal daerah:</b> {daerah}</p>'
                f'<p class="info-sejarah">{sejarah}</p>'
                f'</div></div>'
            )

        st.markdown(
            '<div class="info-list">' + "".join(kartu) + "</div>",
            unsafe_allow_html=True,
        )

# Navigasi
PAGES = {
    "Beranda": st.Page(
        halaman_beranda, title="Beranda", url_path="", default=True
    ),
    "Klasifikasi": st.Page(
        halaman_klasifikasi, title="Klasifikasi", url_path="klasifikasi"
    ),
    "Informasi": st.Page(
        halaman_informasi, title="Informasi", url_path="informasi"
    ),
}

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