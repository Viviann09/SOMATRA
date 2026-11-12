import html
from io import BytesIO

import streamlit as st
from PIL import Image

from shared import (
    FORMAT_DIIZINKAN,
    MAKS_UKURAN_MB,
    kembali_ke_beranda,
    prediksi_gambar,
    reset_klasifikasi,
    tampilkan_gambar_serupa,
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

        with st.container(key="wadah_hasil"):
            kiri, kanan = st.columns(
                [1, 2.6], gap="large", vertical_alignment="center"
            )

            with kiri:
                if image_bytes:
                    st.image(
                        Image.open(BytesIO(image_bytes)).convert("RGB"),
                        caption="Gambar yang diklasifikasikan",
                        width=240,
                    )

            with kanan:
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

            with st.container(key="aksi_hasil"):
                st.button(
                    "Kembali ke Beranda",
                    key="btn_beranda",
                    on_click=kembali_ke_beranda,
                )
                st.button(
                    "Klasifikasi Ulang",
                    key="btn_ulang",
                    on_click=reset_klasifikasi,
                )

        tampilkan_gambar_serupa(hasil["nama_kunci"], info["nama"])