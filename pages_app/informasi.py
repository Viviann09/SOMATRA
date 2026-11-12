import html
import streamlit as st

from motif_data import MOTIF_DATA
from shared import (
    cari_gambar_motif,
    format_nama,
    gambar_ke_data_uri,
    gambar_utama,
    reset_klasifikasi,
    tampilkan_galeri,
)

SEMUA = "Semua"

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
        return

    daerah_list = []
    for _, data in items:
        d = data.get("daerah", "Informasi belum tersedia")
        if d not in daerah_list:
            daerah_list.append(d)
    pilihan_filter = [SEMUA] + daerah_list

    with st.container(key="filter_daerah"):
        if hasattr(st, "pills"):
            terpilih = st.pills(
                "Filter daerah",
                pilihan_filter,
                default=SEMUA,
                key="filter_daerah_pilihan",
                label_visibility="collapsed",
            )
        else:
            terpilih = st.radio(
                "Filter daerah",
                pilihan_filter,
                horizontal=True,
                key="filter_daerah_pilihan",
                label_visibility="collapsed",
            )

    if terpilih is None:
        terpilih = SEMUA

    if terpilih != SEMUA:
        items = [
            (k, d) for k, d in items
            if d.get("daerah", "Informasi belum tersedia") == terpilih
        ]

    if not items:
        st.info("Tidak ada motif untuk daerah ini.")
        return

    for key, data in items:
        nama_raw = data.get("nama", format_nama(key))
        nama = html.escape(nama_raw)
        daerah = html.escape(data.get("daerah", "Informasi belum tersedia"))
        sejarah = html.escape(
            str(data.get("sejarah", "Informasi sejarah belum ditambahkan."))
        )

        _, tambahan = cari_gambar_motif(key)
        utama = gambar_utama(key)

        if utama:
            uri = gambar_ke_data_uri(str(utama), 500)
            img_html = (
                f'<div class="info-img"><img src="{uri}" alt="{nama}"></div>'
            )
        else:
            img_html = '<div class="info-img motif-noimg">Foto belum ada</div>'

        with st.container(key=f"infokartu_{key}"):
            col_img, col_teks = st.columns(
                [1, 3], gap="medium", vertical_alignment="center"
            )

            with col_img:
                with st.container(key=f"infogambar_{key}"):
                    st.markdown(img_html, unsafe_allow_html=True)
                    if tambahan:
                        if st.button("⤢", key=f"galeri_{key}"):
                            tampilkan_galeri(key, nama_raw)

            with col_teks:
                st.markdown(
                    f'<div class="info-body">'
                    f'<h3>{nama}</h3>'
                    f'<p class="info-daerah"><b>Asal daerah:</b> {daerah}</p>'
                    f'<p class="info-sejarah">{sejarah}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )