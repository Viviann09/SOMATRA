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

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model/model_mobilenetv1.keras"
CSS_PATH = BASE_DIR / "style.css"

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

FOLDER_MOTIF = BASE_DIR / "assets" / "motif"
JUMLAH_SERUPA = 4
EKSTENSI_GAMBAR = {".jpg", ".jpeg", ".png"}

def slug_motif(kunci):
    """kain_songket_jambi_angsa_duo -> angsa_duo"""
    bagian = kunci.split("_", 3)
    return bagian[3] if len(bagian) == 4 else kunci

def cari_gambar_motif(kunci):
    """Kembalikan (gambar_utama, [gambar_1 .. gambar_9])."""
    slug = slug_motif(kunci)
    folder = FOLDER_MOTIF / slug
    if not folder.is_dir():
        return None, []

    utama = None
    tambahan = []
    for p in folder.iterdir():
        if p.suffix.lower() not in EKSTENSI_GAMBAR:
            continue
        stem = p.stem.lower()
        if stem == slug:
            utama = p
        elif stem.startswith(slug + "_") and stem[len(slug) + 1:].isdigit():
            tambahan.append((int(stem[len(slug) + 1:]), p))

    tambahan.sort(key=lambda x: x[0])
    return utama, [p for _, p in tambahan]

def gambar_utama(kunci):
    return cari_gambar_motif(kunci)[0]

@st.cache_data
def gambar_ke_data_uri(path_str, lebar_maks=800):
    img = Image.open(path_str).convert("RGB")
    img.thumbnail((lebar_maks, lebar_maks))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{data}"

def grid_gambar_html(files, alt, kelas):
    alt = html.escape(alt)
    item = []
    for p in files:
        uri = gambar_ke_data_uri(str(p), 500)
        item.append(
            f'<div class="serupa-item"><img src="{uri}" alt="{alt}"></div>'
        )
    return f'<div class="{kelas}">' + "".join(item) + "</div>"

def tampilkan_gambar_serupa(kunci, nama):
    _, tambahan = cari_gambar_motif(kunci)
    if not tambahan:
        return
    
    pilihan = st.session_state.get("serupa_pilihan")
    if pilihan is None or pilihan.get("kunci") != kunci:
        terpilih = random.sample(tambahan, min(JUMLAH_SERUPA, len(tambahan)))
        pilihan = {"kunci": kunci, "files": [str(p) for p in terpilih]}
        st.session_state["serupa_pilihan"] = pilihan

    files = [Path(p) for p in pilihan["files"]]
    st.markdown(
        '<div class="section-heading" style="text-align:center;">'
        'Motif Serupa dengan Hasil Klasifikasi</div>'
        + grid_gambar_html(files, nama, "serupa-grid"),
        unsafe_allow_html=True,
    )

def tampilkan_galeri(kunci, nama):
    _, tambahan = cari_gambar_motif(kunci)

    @st.dialog(f"Motif {nama}", width="small")
    def _dialog():
        st.markdown(
            grid_gambar_html(tambahan, nama, "galeri-grid"),
            unsafe_allow_html=True,
        )

    _dialog()

PAGES = {}

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
    st.session_state["serupa_pilihan"] = None
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