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
        '<div class="tentang-band">'
        '<div class="tentang-heading">Mengenal Kain Songket Sumatra</div>'
        '<p class="tentang-intro">'
        'Songket adalah kain tenun yang dihiasi benang emas atau perak, '
        'sehingga motifnya tampak timbul dan berkilau. Kain ini bisa kita '
        'temui di banyak daerah di Nusantara, seperti Bali, Lombok, '
        'Kalimantan, dan Sulawesi. Namun songket Sumatra punya cerita dan '
        'ciri khasnya sendiri, dan di sinilah kamu bisa mengenalnya lebih '
        'dekat.'
        '</p>'
        '<div class="tentang-grid">'
        '<div class="tentang-card">'
        '<div class="tentang-no">01</div>'
        '<div class="tentang-judul">Tenun Buatan Tangan</div>'
        '<p>Setiap motif dibuat dengan menyisipkan benang tambahan ke kain '
        'dasar, helai demi helai, seluruhnya dengan tangan. Karena itu, '
        'selembar songket bisa memakan waktu berminggu-minggu untuk '
        'selesai.</p>'
        '</div>'
        '<div class="tentang-card">'
        '<div class="tentang-no">02</div>'
        '<div class="tentang-judul">Motif yang Bermakna</div>'
        '<p>Di Sumatra, songket hadir di momen penting seperti pernikahan, '
        'penyambutan tamu, dan upacara adat. Motifnya bukan sekadar hiasan, '
        'tetapi membawa pesan tentang kesetiaan, kebersamaan, dan '
        'kerendahan hati.</p>'
        '</div>'
        '<div class="tentang-card">'
        '<div class="tentang-no">03</div>'
        '<div class="tentang-judul">Setiap Daerah Berbeda</div>'
        '<p>Aceh, Jambi, Minangkabau, Palembang, dan Riau masing-masing '
        'punya motif dan warna khas, banyak yang terinspirasi dari bunga, '
        'hewan, dan alam sekitar. Di daerah lain seperti Bali dan Lombok, '
        'songket punya corak dan fungsi yang berbeda sesuai adat '
        'setempat.</p>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading" style="text-align:center;">'
        'Galeri Motif Songket</div>',
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
    
    pdf_path = path_gambar_motif("assets/panduan/manual_book.pdf")

    with st.container(key="panduan_band"):
        kiri, kanan = st.columns(
            [2.5, 1], gap="large", vertical_alignment="center"
        )

        with kiri:
            st.markdown(
                '<div class="panduan-judul">Panduan Penggunaan</div>'
                '<p class="panduan-teks">'
                'Unduh buku panduan untuk mempelajari cara menggunakan '
                'website ini.'
                '</p>',
                unsafe_allow_html=True,
            )

        with kanan:
            if pdf_path:
                st.download_button(
                    label="Unduh Panduan (PDF)",
                    data=pdf_path.read_bytes(),
                    file_name="Panduan_SOMATRA.pdf",
                    mime="application/pdf",
                    key="unduh_panduan",
                )
            else:
                st.caption("Buku panduan belum tersedia.")