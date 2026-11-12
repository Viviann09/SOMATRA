import html
import streamlit as st

from motif_data import MOTIF_DATA
from shared import (
    JUMLAH_TAMPIL,
    format_nama,
    geser_motif,
    gambar_ke_data_uri,
    gambar_utama,
    path_gambar_motif,
    pindah_halaman,
    reset_klasifikasi,
)


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
            image_path = gambar_utama(key)

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