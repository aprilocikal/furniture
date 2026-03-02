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
    
    # === OPERASI: CREATE ===
    if crud_mode == "Tambah Produk Baru":
        st.subheader("Tambah Data Baru")
        with st.form("form_tambah"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_jenis = st.text_input("Jenis (mis. Meja)")
                t_brand = st.text_input("Brand (mis. IKEA)")
                t_ukuran = st.selectbox("Ukuran", ["S", "M", "L", "XL"])
            with col_t2:
                t_harga = st.number_input("Harga per item", min_value=0, step=1000)
                t_terjual = st.number_input("Jumlah Terjual (pcs)", min_value=0, step=1)
                t_stokawal = st.number_input("Stok Awal Asumsi", value=10, min_value=0, step=1)
            
            submit_add = st.form_submit_button("Simpan Data")
            if submit_add:
                if not t_jenis.strip() or not t_brand.strip():
                    st.error("Jenis dan Brand tidak boleh kosong!")
                else:
                    # Logic kalkulasi hpp
                    hpp = t_harga * 0.6
                    profit_per_item = t_harga - hpp
                    total_profit = profit_per_item * t_terjual
                    tanggal_sekarang = datetime.now().strftime("%Y-%m-%d")
                    
                    new_item = {
                        "jenis": t_jenis,
                        "ukuran": t_ukuran,
                        "harga_per_item": t_harga,
                        "stok_awal": t_stokawal,
                        "stok_akhir": t_stokawal - t_terjual,
                        "jumlah_terjual": t_terjual,
                        "tanggal_terjual": tanggal_sekarang,
                        "brand": t_brand,
                        "hpp": hpp,
                        "profit_per_item": profit_per_item,
                        "total_profit": total_profit
                    }
                    data_produk.append(new_item)
                    save_data(data_produk)
                    st.success(f"Berhasil! Produk '{t_jenis}' - '{t_brand}' telah ditambahkan.")
                    st.rerun() # Refresh halaman secara instan

    # === OPERASI: UPDATE ===
    elif crud_mode == "Update Data Produk":
        st.subheader("Sunting Item Data")
        if len(data_produk) == 0:
            st.info("Dataset JSON Anda masih kosong!")
        else:
            options_upd = [f"[{i+1}] [{p['brand']}] Jenis: {p['jenis']} | Ukuran {p['ukuran']} | Terjual: {p['jumlah_terjual']}" for i, p in enumerate(data_produk)]
            selected_upd = st.selectbox("Pilih produk yang ingin diperbarui:", options_upd)
            idx = options_upd.index(selected_upd)
            curr = data_produk[idx] # referensi data lama
            
            with st.form("form_update"):
                st.markdown("Ubah field informasi di bawah:")
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    u_jenis = st.text_input("Jenis", value=curr['jenis'])
                    u_brand = st.text_input("Brand", value=curr['brand'])
                    ukuran_ops = ["S", "M", "L", "XL"]
                    idx_uk = ukuran_ops.index(curr['ukuran']) if curr['ukuran'] in ukuran_ops else 0
                    u_ukuran = st.selectbox("Ukuran", ukuran_ops, index=idx_uk)
                with col_u2:
                    u_harga = st.number_input("Harga per item", value=int(curr['harga_per_item']), step=1000)
                    u_terjual = st.number_input("Jumlah Terjual (pcs)", value=int(curr['jumlah_terjual']), step=1)
                    u_stokawal = st.number_input("Stok Awal Asumsi", value=int(curr.get('stok_awal', 10)), step=1)
                
                submit_update = st.form_submit_button("Terapkan Spesifikasi")
                if submit_update:
                    if not u_jenis.strip() or not u_brand.strip():
                        st.error("Jenis dan Brand tidak boleh kosong!")
                    else:
                        hpp = u_harga * 0.6
                        profit_per_item = u_harga - hpp
                        total_profit = profit_per_item * u_terjual
                        
                        # Timpa data index spesifik di list
                        data_produk[idx].update({
                            "jenis": u_jenis,
                            "brand": u_brand,
                            "ukuran": u_ukuran,
                            "harga_per_item": u_harga,
                            "stok_awal": u_stokawal,
                            "stok_akhir": u_stokawal - u_terjual,
                            "jumlah_terjual": u_terjual,
                            "hpp": hpp,
                            "profit_per_item": profit_per_item,
                            "total_profit": total_profit
                        })
                        save_data(data_produk)
                        st.success("Perubahan pada instansi data berhasil tersimpan!")
                        st.rerun()

    # === OPERASI: DELETE ===
    elif crud_mode == "Hapus Produk":
        st.subheader("Hapus Data Registri")
        if len(data_produk) == 0:
            st.info("Dataset JSON Anda masih kosong!")
        else:
            list_hapus = [f"[{i+1}] [{p['brand']}] Jenis: {p['jenis']} | Ukuran {p['ukuran']} | Terjual: {p['jumlah_terjual']}" for i, p in enumerate(data_produk)]
            dipilih_hapus = st.selectbox("Pilih produk historis yang ingin dihapus:", list_hapus)
            idx_del = list_hapus.index(dipilih_hapus)
            
            st.warning(f"Apakah Anda setuju ingin menghapus data **[{data_produk[idx_del]['brand']}] {data_produk[idx_del]['jenis']}** secara permanen dari sistem?")
            
            if st.button("Ya, Hapus Terpilih", type="primary"):
                nama_barang = data_produk[idx_del]['brand']
                data_produk.pop(idx_del)
                save_data(data_produk)
                st.success(f"Logik data '{nama_barang}' telah dijauhkan dari master file (Hapus berhasil).")
                st.rerun()
