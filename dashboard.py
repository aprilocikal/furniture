import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import os

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Penjualan Furnitur", layout="wide")

# Fungsi memuat dan menyimpan data
def load_data():
    if os.path.exists("output_produk.json"):
        with open("output_produk.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open("output_produk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # 2. Update File Rekap Statistik agar nilai matrik ikut berubah di 'output_rekap.json'
    try:
        df_temp = pd.DataFrame(data)
        if not df_temp.empty:
            stats = {
                "total_produk_entries": len(df_temp),
                "total_profit": float(df_temp['total_profit'].sum()),
                "rata_rata_profit": float(df_temp['total_profit'].sum() / len(df_temp)),
                "profit_tertinggi": float(df_temp['total_profit'].max()),
                "profit_terendah": float(df_temp['total_profit'].min()),
                "total_unit_terjual": int(df_temp['jumlah_terjual'].sum())
            }
            rekap_jenis = df_temp.groupby('jenis')['total_profit'].sum().to_dict()
            
            payload = {
                "meta": {
                    "dibuat_pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sumber": "Auto-update Web Dashboard"
                },
                "statistik": stats,
                "rekap_per_jenis": rekap_jenis
            }
            with open("output_rekap.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass
        
    # 3. Otomatis PUSH file ke GitHub secara diam-diam di background (Localhost Only)
    def push_to_git():
        import subprocess
        try:
            subprocess.run(["git", "add", "output_produk.json", "output_rekap.json"], capture_output=True)
            subprocess.run(["git", "commit", "-m", "Auto-update CRUD dari Web Dashboard"], capture_output=True)
            subprocess.run(["git", "push"], capture_output=True)
        except:
            pass
            
    import threading
    threading.Thread(target=push_to_git).start()

# Baca data setiap kali halaman dirender
data_produk = load_data()
df = pd.DataFrame(data_produk)

# Judul Utama
st.title("Sistem Analisis & Manajemen Penjualan Furnitur")

# Membuat dua tab utama (Fitur Baru untuk Memilah Dashboard & CRUD)
tab_dashboard, tab_crud = st.tabs(["Visualisasi Dashboard", "Kelola Data (CRUD)"])

# ================================
# TAB 1: VISUALISASI DASHBOARD
# ================================
with tab_dashboard:
    st.markdown("Visualisasi interaktif dari data sistem penjualan furnitur.")
    
    if df.empty:
        st.warning("Data tidak ditemukan! Silakan tambahkan data melalui tab **Kelola Data (CRUD)**.")
    else:
        # Menempatkan filter ke bagian atas agar lebih rapi saat pindah ke tab CRUD 
        st.subheader("Filter Data")
        
        jenis_options = ["Semua"] + list(df['jenis'].unique())
        selected_jenis = st.selectbox("Pilih Jenis Furnitur", jenis_options)
        
        if selected_jenis != "Semua":
            df_filtered = df[df['jenis'] == selected_jenis]
        else:
            df_filtered = df
            
        if st.button("Segarkan Data"):
            st.rerun()

        st.markdown("---")
        
        # --- KPI Metrics Bar ---
        st.subheader("Ringkasan Kinerja")
        col1, col2, col3, col4 = st.columns(4)
        
        total_profit = df_filtered['total_profit'].sum()
        total_terjual = df_filtered['jumlah_terjual'].sum()
        total_produk = len(df_filtered)
        avg_profit_per_item = df_filtered['profit_per_item'].mean() if not df_filtered.empty else 0
        
        col1.metric("Total Profit", f"Rp {total_profit:,.0f}")
        col2.metric("Total Unit Terjual", f"{total_terjual:,} pcs")
        col3.metric("Total Data Varian", f"{total_produk}")
        col4.metric("Rata-rata Profit/Item", f"Rp {avg_profit_per_item:,.0f}")
        
        st.markdown("---")
        
        # --- BAGIAN CHARTS ATAS ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            if selected_jenis == "Semua":
                profit_by_jenis = df_filtered.groupby('jenis')['total_profit'].sum().reset_index()
                fig_jenis = px.bar(profit_by_jenis, x='jenis', y='total_profit', 
                                   title="Total Profit per Jenis Produk",
                                   labels={'jenis': 'Jenis Furnitur', 'total_profit': 'Total Profit (Rp)'},
                                   color='jenis', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_jenis.update_traces(hovertemplate='Jenis: %{x}<br>Total Profit: Rp %{y:,.0f}<extra></extra>')
                st.plotly_chart(fig_jenis, use_container_width=True)
            else:
                profit_by_brand = df_filtered.groupby('brand')['total_profit'].sum().reset_index().sort_values(by='total_profit', ascending=False)
                fig_brand = px.bar(profit_by_brand, x='brand', y='total_profit', 
                                   title=f"Total Profit per Brand (Hanya '{selected_jenis}')",
                                   labels={'brand': 'Brand', 'total_profit': 'Total Profit (Rp)'},
                                   color='brand', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_brand.update_traces(hovertemplate='Brand: %{x}<br>Total Profit: Rp %{y:,.0f}<extra></extra>')
                st.plotly_chart(fig_brand, use_container_width=True)
                
        with col_chart2:
            profit_by_ukuran = df_filtered.groupby('ukuran')['total_profit'].sum().reset_index()
            fig_ukuran = px.pie(profit_by_ukuran, values='total_profit', names='ukuran', 
                                title="Distribusi Profit Berdasarkan Ukuran",
                                hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_ukuran.update_traces(hovertemplate='Ukuran: %{label}<br>Profit: Rp %{value:,.0f}<br>Persentase: %{percent}<extra></extra>')
            st.plotly_chart(fig_ukuran, use_container_width=True)
            
        st.markdown("---")
        
        # --- BAGIAN CHARTS BAWAH ---
        col_chart3, col_chart4 = st.columns(2)
        
        with col_chart3:
            top_brands = df_filtered.groupby('brand')['total_profit'].sum().reset_index().sort_values(by='total_profit', ascending=False).head(10)
            fig_top_brands = px.bar(top_brands, y='brand', x='total_profit', orientation='h',
                                    title="Top 10 Brand Berdasarkan Profit",
                                    labels={'brand': 'Brand', 'total_profit': 'Total Profit (Rp)'},
                                    color='total_profit', color_continuous_scale='Blues')
            fig_top_brands.update_layout(yaxis={'categoryorder':'total ascending'}) 
            fig_top_brands.update_traces(hovertemplate='Brand: %{y}<br>Total Profit: Rp %{x:,.0f}<extra></extra>')
            st.plotly_chart(fig_top_brands, use_container_width=True)
            
        with col_chart4:
            trend_data = df_filtered.groupby('tanggal_terjual')['jumlah_terjual'].sum().reset_index()
            trend_data = trend_data.sort_values('tanggal_terjual')
            
            fig_trend = px.line(trend_data, x='tanggal_terjual', y='jumlah_terjual', 
                                title="Tren Kuantitas Terjual Berdasarkan Tanggal",
                                labels={'tanggal_terjual': 'Tanggal Terjual', 'jumlah_terjual': 'Total Terjual (pcs)'},
                                markers=True)
            fig_trend.update_traces(hovertemplate='Tanggal: %{x}<br>Terjual: %{y} pcs<extra></extra>', line=dict(width=3))
            st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("---")
        
        # --- TABEL DATA RAW ---
        st.subheader("Tabel Detail Data Penjualan")
        st.markdown("Seluruh data laporan tertulis direpresentasikan pada tabel di bawah ini.")
        
        # Reorder kolom dataframe agar Brand muncul pertama, diikuti Jenis, Ukuran, dll.
        kolom_urutan = ['brand', 'jenis', 'ukuran', 'harga_per_item', 'stok_awal', 'stok_akhir', 
                        'jumlah_terjual', 'tanggal_terjual', 'hpp', 'profit_per_item', 'total_profit']
        # Pastikan kita hanya memilih kolom yang ada
        kolom_tersedia = [col for col in kolom_urutan if col in df_filtered.columns]
        df_reordered = df_filtered[kolom_tersedia]
        
        styled_df = df_reordered.style.format({
            'harga_per_item': 'Rp {:,.0f}',
            'hpp': 'Rp {:,.0f}',
            'profit_per_item': 'Rp {:,.0f}',
            'total_profit': 'Rp {:,.0f}'
        })
        st.dataframe(styled_df, use_container_width=True, hide_index=True)


# ================================
# TAB 2: CRUD DATA PADA WEB
# ================================
with tab_crud:
    st.header("Manajemen Data Produk")
    st.markdown("Kelola data penjualan langsung dalam form khusus di halaman ini yang akan otomatis memperbarui *output_produk.json*.")
    
    crud_mode = st.radio("Pilih Operasi Data:", ["Tambah Produk Baru", "Update Data Produk", "Hapus Produk"], horizontal=True)
    st.markdown("---")
    
    # === SWAL INJECTOR ===
    if 'swal_show' in st.session_state:
        swal_msg = st.session_state.pop('swal_show')
        import streamlit.components.v1 as components
        components.html(f"""
            <script>
            if (!window.parent.Swal) {{
                let script = window.parent.document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                window.parent.document.head.appendChild(script);
                script.onload = () => {{
                    window.parent.Swal.fire({{
                        title: '{swal_msg["title"]}',
                        text: '{swal_msg["text"]}',
                        icon: '{swal_msg["icon"]}',
                        confirmButtonColor: '#3085d6'
                    }});
                }}
            }} else {{
                window.parent.Swal.fire({{
                    title: '{swal_msg["title"]}',
                    text: '{swal_msg["text"]}',
                    icon: '{swal_msg["icon"]}',
                    confirmButtonColor: '#3085d6'
                }});
            }}
            </script>
        """, height=0, width=0)

    # === OPERASI: CREATE ===
    if crud_mode == "Tambah Produk Baru":
        st.subheader("Tambah Data Baru")
        
        ex_jenis = sorted(list(df['jenis'].unique())) if not df.empty else []
        ex_brand = sorted(list(df['brand'].unique())) if not df.empty else []
        ex_ukuran = sorted(list(df['ukuran'].unique())) if not df.empty else ["S", "M", "L", "XL"]
        op_tbh = "+ Tambah Baru..."
        op_def_jenis = "-- Pilih Jenis --"
        op_def_brand = "-- Pilih Brand --"
        op_def_ukuran = "-- Pilih Ukuran --"
        
        if 'form_reset_key' not in st.session_state:
            st.session_state['form_reset_key'] = 0
        r_key = st.session_state['form_reset_key']
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            sel_jenis = st.selectbox("Jenis", [op_def_jenis] + ex_jenis + [op_tbh], key=f't_sel_jenis_{r_key}')
            if sel_jenis == op_tbh:
                t_jenis = st.text_input("Ketik Jenis Baru", placeholder="Contoh: Meja Lipat", key=f't_txt_jenis_{r_key}')
            else:
                t_jenis = sel_jenis
                
            sel_brand = st.selectbox("Brand", [op_def_brand] + ex_brand + [op_tbh], key=f't_sel_brand_{r_key}')
            if sel_brand == op_tbh:
                t_brand = st.text_input("Ketik Brand Baru", placeholder="Contoh: IKEA, Informa", key=f't_txt_brand_{r_key}')
            else:
                t_brand = sel_brand
                
            sel_ukuran = st.selectbox("Ukuran", [op_def_ukuran] + ex_ukuran + [op_tbh], key=f't_sel_ukuran_{r_key}')
            if sel_ukuran == op_tbh:
                t_ukuran = st.text_input("Ketik Ukuran Baru", placeholder="Contoh: XXL, Custom", key=f't_txt_ukuran_{r_key}')
            else:
                t_ukuran = sel_ukuran
        
        with col_t2:
            t_harga = st.number_input("Harga per item", min_value=0, step=1000, value=None, placeholder="0", key=f't_harga_{r_key}')
            t_terjual = st.number_input("Jumlah Terjual (pcs)", min_value=0, step=1, value=None, placeholder="0", key=f't_terjual_{r_key}')
            t_stokawal = st.number_input("Stok Awal Asumsi", min_value=0, step=1, value=None, placeholder="0", key=f't_stokawal_{r_key}')
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_add = st.button("Simpan Data", type="primary", use_container_width=True)
        if submit_add:
            if t_jenis == op_def_jenis or t_brand == op_def_brand or t_ukuran == op_def_ukuran:
                st.error("Mohon pilih Jenis, Brand, dan Ukuran terlebih dahulu dari daftar kategori!")
            elif t_harga is None or t_terjual is None or t_stokawal is None:
                st.error("Semua field angka (Harga, Terjual, Stok Awal) harus diisi (Minimal 0)!")
            elif not t_jenis or not str(t_jenis).strip() or not t_brand or not str(t_brand).strip() or not t_ukuran or not str(t_ukuran).strip():
                st.error("Semua field teks tidak boleh kosong!")
            else:
                hpp = t_harga * 0.6
                profit_per_item = t_harga - hpp
                total_profit = profit_per_item * t_terjual
                
                new_item = {
                    "jenis": str(t_jenis).strip(),
                    "ukuran": str(t_ukuran).strip(),
                    "harga_per_item": t_harga,
                    "stok_awal": t_stokawal,
                    "stok_akhir": t_stokawal - t_terjual,
                    "jumlah_terjual": t_terjual,
                    "tanggal_terjual": datetime.now().strftime("%Y-%m-%d"),
                    "brand": str(t_brand).strip(),
                    "hpp": hpp,
                    "profit_per_item": profit_per_item,
                    "total_profit": total_profit
                }
                data_produk.append(new_item)
                save_data(data_produk)
                
                # Reset widget states with new key safely
                st.session_state['form_reset_key'] += 1
                    
                st.session_state['swal_show'] = {"title": "Tersimpan!", "text": f"Produk {str(t_jenis).strip()} - {str(t_brand).strip()} berhasil ditambahkan.", "icon": "success"}
                st.rerun()

    # === OPERASI: UPDATE ===
    elif crud_mode == "Update Data Produk":
        st.subheader("Sunting Item Data")
        if len(data_produk) == 0:
            st.info("Dataset JSON Anda masih kosong!")
        else:
            options_upd = [f"[{i+1}] [{p['brand']}] Jenis: {p['jenis']} | Ukuran {p['ukuran']} | Terjual: {p['jumlah_terjual']}" for i, p in enumerate(data_produk)]
            selected_upd = st.selectbox("Pilih produk yang ingin diperbarui:", options_upd, index=None, placeholder="-- Pilih Data Produk --")
            
            if selected_upd:
                idx = options_upd.index(selected_upd)
                curr = data_produk[idx] # referensi data lama
                ex_jenis = sorted(list(df['jenis'].unique())) if not df.empty else []
                ex_brand = sorted(list(df['brand'].unique())) if not df.empty else []
                ex_ukuran = sorted(list(df['ukuran'].unique())) if not df.empty else ["S", "M", "L", "XL"]
                op_tbh = "+ Tambah Baru..."
                
                st.markdown("Ubah field informasi di bawah:")
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    jen_idx = ex_jenis.index(curr['jenis']) if curr['jenis'] in ex_jenis else 0
                    sel_u_jenis = st.selectbox("Ubah Jenis", ex_jenis + [op_tbh], index=jen_idx)
                    if sel_u_jenis == op_tbh:
                        u_jenis = st.text_input("Ketik Jenis Baru", value=curr['jenis'])
                    else:
                        u_jenis = sel_u_jenis
                        
                    br_idx = ex_brand.index(curr['brand']) if curr['brand'] in ex_brand else 0
                    sel_u_brand = st.selectbox("Ubah Brand", ex_brand + [op_tbh], index=br_idx)
                    if sel_u_brand == op_tbh:
                        u_brand = st.text_input("Ketik Brand Baru", value=curr['brand'])
                    else:
                        u_brand = sel_u_brand
                    
                    uk_idx = ex_ukuran.index(curr['ukuran']) if curr['ukuran'] in ex_ukuran else 0
                    sel_u_ukuran = st.selectbox("Ubah Ukuran", ex_ukuran + [op_tbh], index=uk_idx)
                    if sel_u_ukuran == op_tbh:
                        u_ukuran = st.text_input("Ketik Ukuran Baru", value=curr['ukuran'])
                    else:
                        u_ukuran = sel_u_ukuran
                    
                with col_u2:
                    u_harga = st.number_input("Harga per item", value=int(curr['harga_per_item']), step=1000)
                    u_terjual = st.number_input("Jumlah Terjual (pcs)", value=int(curr['jumlah_terjual']), step=1)
                    u_stokawal = st.number_input("Stok Awal Asumsi", value=int(curr.get('stok_awal', 10)), step=1)
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_update = st.button("Terapkan Spesifikasi", use_container_width=True)
                if submit_update:
                    if not u_jenis.strip() or not u_brand.strip() or not u_ukuran.strip():
                        st.error("Jenis, Brand dan Ukuran tidak boleh kosong!")
                    else:
                        hpp = u_harga * 0.6
                        profit_per_item = u_harga - hpp
                        total_profit = profit_per_item * u_terjual
                        
                        data_produk[idx].update({
                            "jenis": str(u_jenis).strip(),
                            "brand": str(u_brand).strip(),
                            "ukuran": str(u_ukuran).strip(),
                            "harga_per_item": u_harga,
                            "stok_awal": u_stokawal,
                            "stok_akhir": u_stokawal - u_terjual,
                            "jumlah_terjual": u_terjual,
                            "hpp": hpp,
                            "profit_per_item": profit_per_item,
                            "total_profit": total_profit
                        })
                        save_data(data_produk)
                        st.session_state['swal_show'] = {"title": "Update Berhasil!", "text": "Perubahan pada data telah disinkronisasikan.", "icon": "info"}
                        st.rerun()

    # === OPERASI: DELETE ===
    elif crud_mode == "Hapus Produk":
        st.subheader("Hapus Data Registri")
        if len(data_produk) == 0:
            st.info("Dataset JSON Anda masih kosong!")
        else:
            list_hapus = [f"[{i+1}] [{p['brand']}] Jenis: {p['jenis']} | Ukuran {p['ukuran']} | Terjual: {p['jumlah_terjual']}" for i, p in enumerate(data_produk)]
            dipilih_hapus = st.selectbox("Pilih produk historis yang ingin dihapus:", list_hapus, index=None, placeholder="-- Pilih Data Produk --")
            
            if dipilih_hapus:
                idx_del = list_hapus.index(dipilih_hapus)
                
                st.warning(f"Apakah Anda setuju ingin menghapus data **[{data_produk[idx_del]['brand']}] {data_produk[idx_del]['jenis']}** secara permanen dari sistem?")
                
                if st.button("Ya, Hapus Terpilih", type="primary"):
                    nama_barang = data_produk[idx_del]['brand']
                    data_produk.pop(idx_del)
                    save_data(data_produk)
                    st.session_state['swal_show'] = {"title": "Terhapus", "text": f"Data '{nama_barang}' telah dienyahkan dari master.", "icon": "warning"}
                    st.rerun()
