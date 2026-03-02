# OOP PYTHON - Data Penjualan Furnitur dari Excel
# Mata Kuliah: Object Oriented Programming (OOP)

import pandas as pd
import json
import os
from datetime import datetime

# ============================================= 
# CLASS 1: Produk
# Menyimpan data 1 baris dari Excel
# =============================================
class Produk:
    """
    Representasi satu baris data produk furnitur.
    Setiap objek = 1 entri penjualan dari Excel.
    """

    def __init__(self, jenis, ukuran, harga_per_item, stok_awal,
                 stok_akhir, jumlah_terjual, tanggal_terjual, brand,
                 hpp, profit_per_item, total_profit):
        self.jenis = jenis
        self.ukuran = ukuran
        self.harga_per_item = harga_per_item
        self.stok_awal = stok_awal
        self.stok_akhir = stok_akhir
        self.jumlah_terjual = jumlah_terjual
        # Konversi tanggal ke string agar bisa di-JSON-kan
        if isinstance(tanggal_terjual, datetime):
            self.tanggal_terjual = tanggal_terjual.strftime("%Y-%m-%d")
        else:
            self.tanggal_terjual = str(tanggal_terjual)
        self.brand = brand
        self.hpp = hpp
        self.profit_per_item = profit_per_item
        self.total_profit = total_profit

    def info(self):
        """Tampilkan informasi ringkas produk."""
        return (f"[{self.brand}] Jenis: {self.jenis} | "
                f"Ukuran: {self.ukuran} | "
                f"Harga: Rp{self.harga_per_item:,.0f} | "
                f"Terjual: {self.jumlah_terjual} pcs | "
                f"Profit: Rp{self.total_profit:,.2f}")

    def to_dict(self):
        """Konversi objek ke dictionary (dibutuhkan untuk JSON export)."""
        return {
            "jenis": self.jenis,
            "ukuran": self.ukuran,
            "harga_per_item": self.harga_per_item,
            "stok_awal": self.stok_awal,
            "stok_akhir": self.stok_akhir,
            "jumlah_terjual": self.jumlah_terjual,
            "tanggal_terjual": self.tanggal_terjual,
            "brand": self.brand,
            "hpp": round(self.hpp, 2),
            "profit_per_item": round(self.profit_per_item, 2),
            "total_profit": round(self.total_profit, 2)
        }

    def __repr__(self):
        return f"Produk({self.jenis}, {self.brand}, Ukuran={self.ukuran})"


# =============================================
# CLASS 2: ExcelReader
# Bertugas membaca file .xlsx dan mengubahnya
# menjadi list objek Produk
# =============================================
class ExcelReader:
    """
    Membaca file Excel dan mengonversi tiap baris
    menjadi objek Produk.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self._df = None  # DataFrame mentah dari pandas

    def load(self, sheet_name="DATA"):
        """Memuat data dari sheet Excel ke DataFrame."""
        print(f"Membaca file : {self.filepath}")
        print(f"Sheet target : {sheet_name}")
        self._df = pd.read_excel(self.filepath, sheet_name=sheet_name)
        print(f"Berhasil! {len(self._df)} baris data dimuat.\n")
        return self  # Method chaining

    def to_produk_list(self):
        """
        Iterasi setiap baris DataFrame, buat objek Produk,
        kumpulkan ke dalam list dan kembalikan.
        """
        if self._df is None:
            raise RuntimeError("Panggil .load() terlebih dahulu!")

        produk_list = []
        for _, row in self._df.iterrows():
            p = Produk(
                jenis=row['Jenis'],
                ukuran=row['Ukuran'],
                harga_per_item=row['Harga per Item'],
                stok_awal=row['Stok Awal'],
                stok_akhir=row['Stok Akhir'],
                jumlah_terjual=row['Jumlah Terjual'],
                tanggal_terjual=row['Tanggal Terjual'],
                brand=row['Brand'],
                hpp=row['HPP'],
                profit_per_item=row['Profit Per Item'],
                total_profit=row['Total Profit']
            )
            produk_list.append(p)

        print(f"{len(produk_list)} objek Produk berhasil dibuat.\n")
        return produk_list


# =============================================
# CLASS 3: DataManager
# Menganalisis dan memfilter kumpulan Produk
# =============================================
class DataManager:
    """
    Menerima list objek Produk dan menyediakan
    fungsi filter, rekap, dan statistik.
    """

    def __init__(self, produk_list):
        self.data = produk_list

    # --- CRUD OPERATIONS ---
    def tambah_produk(self, produk_baru):
        """Create: Menambahkan produk baru ke dalam data."""
        self.data.append(produk_baru)
        print(f"Produk {produk_baru.jenis} ({produk_baru.brand}) berhasil ditambahkan.")

    def baca_produk(self, index=None):
        """Read: Menampilkan data produk tertentu atau semua jika index None."""
        if index is not None:
            if 0 <= index < len(self.data):
                return self.data[index]
            else:
                print("Index tidak ditemukan!")
                return None
        return self.data

    def update_produk(self, index, produk_update):
        """Update: Memperbarui data produk berdasarkan index."""
        if 0 <= index < len(self.data):
            self.data[index] = produk_update
            print(f"Produk di index {index} berhasil diperbarui.")
        else:
            print("Index tidak ditemukan!")

    def hapus_produk(self, index):
        """Delete: Menghapus data produk berdasarkan index."""
        if 0 <= index < len(self.data):
            produk_terhapus = self.data.pop(index)
            print(f"Produk {produk_terhapus.jenis} ({produk_terhapus.brand}) berhasil dihapus.")
            return produk_terhapus
        else:
            print("Index tidak ditemukan!")
            return None

    # --- FILTER ---
    def filter_by_jenis(self, jenis):
        """Filter berdasarkan jenis furnitur (mis: 'Kursi', 'Lemari')."""
        return [p for p in self.data if p.jenis.lower() == jenis.lower()]

    def filter_by_brand(self, brand):
        """Filter berdasarkan nama brand."""
        return [p for p in self.data if p.brand.lower() == brand.lower()]

    def filter_by_ukuran(self, ukuran):
        """Filter berdasarkan ukuran (S, M, L, XL)."""
        return [p for p in self.data if p.ukuran.upper() == ukuran.upper()]

    # --- REKAP ---
    def top_profit_by_jenis(self):
        """Total profit per jenis produk, diurutkan terbesar."""
        rekap = {}
        for p in self.data:
            rekap[p.jenis] = rekap.get(p.jenis, 0) + p.total_profit
        return dict(sorted(rekap.items(), key=lambda x: x[1], reverse=True))

    def top_brand(self, n=5):
        """Top N brand berdasarkan total profit."""
        rekap = {}
        for p in self.data:
            rekap[p.brand] = rekap.get(p.brand, 0) + p.total_profit
        return sorted(rekap.items(), key=lambda x: x[1], reverse=True)[:n]

    def rekap_per_ukuran(self):
        """Total profit per ukuran (S/M/L/XL)."""
        rekap = {}
        for p in self.data:
            rekap[p.ukuran] = rekap.get(p.ukuran, 0) + p.total_profit
        return dict(sorted(rekap.items(), key=lambda x: x[1], reverse=True))

    # --- STATISTIK ---
    def statistik(self):
        """Ringkasan statistik seluruh data."""
        if not self.data:
            return {
                "total_produk_entries": 0,
                "total_profit": 0,
                "rata_rata_profit": 0,
                "profit_tertinggi": 0,
                "profit_terendah": 0,
                "total_unit_terjual": 0
            }
        profits = [p.total_profit for p in self.data]
        return {
            "total_produk_entries": len(self.data),
            "total_profit": round(sum(profits), 2),
            "rata_rata_profit": round(sum(profits) / len(profits), 2),
            "profit_tertinggi": round(max(profits), 2),
            "profit_terendah": round(min(profits), 2),
            "total_unit_terjual": sum(p.jumlah_terjual for p in self.data)
        }

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"DataManager({len(self.data)} produk)"


# =============================================
# CLASS 4: JSONExporter
# Mengekspor data ke file JSON
# =============================================
class JSONExporter:
    """
    Mengambil list Produk dan mengekspor ke file .json
    yang bisa dibaca sistem lain atau front-end.
    """

    def __init__(self, produk_list):
        self.produk_list = produk_list

    def export_semua(self, output_path):
        """Export seluruh data produk ke JSON."""
        data = [p.to_dict() for p in self.produk_list]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[{len(data)} records] --> {output_path}")

    def export_rekap(self, statistik_dict, rekap_jenis, output_path):
        """Export rekap statistik ke JSON terpisah."""
        payload = {
            "meta": {
                "dibuat_pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sumber": "isas 1 smster 2.xlsx"
            },
            "statistik": statistik_dict,
            "rekap_per_jenis": rekap_jenis
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[Rekap] --> {output_path}")

        # Otomatis PUSH file sinkronisasi JSON ke Github tanpa output terminal (berjalan di background)
        import threading
        import subprocess
        def push_to_git():
            try:
                subprocess.run(["git", "add", "output_produk.json", "output_rekap.json"], capture_output=True)
                subprocess.run(["git", "commit", "-m", "Auto-update CRUD dari Terminal OOP"], capture_output=True)
                subprocess.run(["git", "push"], capture_output=True)
            except:
                pass
        threading.Thread(target=push_to_git).start()


# =============================================
# MAIN PROGRAM - Titik Masuk Aplikasi
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("   SISTEM ANALISIS PENJUALAN FURNITUR")
    print("   Object Oriented Programming ")
    print("=" * 60)

    # STEP 1: Baca Data dari JSON jika ada, jika tidak dari Excel
    if os.path.exists("output_produk.json"):
        print("[INIT] Memuat data dari output_produk.json ...")
        with open("output_produk.json", "r", encoding="utf-8") as f:
            data_json = json.load(f)
            
        semua_produk = []
        for row in data_json:
            p = Produk(
                jenis=row['jenis'],
                ukuran=row['ukuran'],
                harga_per_item=row['harga_per_item'],
                stok_awal=row['stok_awal'],
                stok_akhir=row['stok_akhir'],
                jumlah_terjual=row['jumlah_terjual'],
                tanggal_terjual=row['tanggal_terjual'],
                brand=row['brand'],
                hpp=row['hpp'],
                profit_per_item=row.get('profit_per_item', 0),
                total_profit=row.get('total_profit', 0)
            )
            semua_produk.append(p)
        print(f"Berhasil! {len(semua_produk)} objek produk dimuat dari JSON.\n")
    else:
        print("[INIT] Membaca dari data Excel asli...")
        reader = ExcelReader("isas 1 smster 2.xlsx")
        reader.load(sheet_name="DATA")
        semua_produk = reader.to_produk_list()

    # STEP 2: Buat DataManager
    dm = DataManager(semua_produk)

    # STEP 3: Statistik Umum
    print("STATISTIK UMUM")
    print("-" * 40)
    stats = dm.statistik()
    for k, v in stats.items():
        label = k.replace("_", " ").title()
        if isinstance(v, float):
            print(f"  {label:<30}: Rp{v:>20,.2f}")
        else:
            print(f"  {label:<30}: {v:>22,}")

    # STEP 4: Rekap per Jenis
    print("\nTOTAL PROFIT PER JENIS PRODUK")
    print("-" * 40)
    for jenis, profit in dm.top_profit_by_jenis().items():
        bar = " " * int(profit / 5_000_000)
        print(f"  {jenis:<15} Rp{profit:>20,.0f}  {bar}")

    # STEP 5: Top Brand
    print("\nTOP 5 BRAND BERDASARKAN PROFIT")
    print("-" * 40)
    for i, (brand, profit) in enumerate(dm.top_brand(5), 1):
        print(f"  {i}. {brand:<20} --> Rp{profit:>20,.2f}")

    # STEP 6: Rekap per Ukuran
    print("\nREKAP PROFIT PER UKURAN")
    print("-" * 40)
    for ukuran, profit in dm.rekap_per_ukuran().items():
        print(f"  Ukuran {ukuran:<5} --> Rp{profit:>20,.2f}")

    # STEP 8: Export ke JSON
    print("\nEXPORT KE JSON")
    print("-" * 40)
    exporter = JSONExporter(semua_produk)
    exporter.export_semua("output_produk.json")
    exporter.export_rekap(stats, dm.top_profit_by_jenis(), "output_rekap.json")

    # STEP 9: MENU INTERAKTIF CRUD
    while True:
        print("\n" + "="*40)
        print("         MENU CRUD INTERAKTIF")
        print("="*40)
        print("1. Tampilkan Semua Produk (READ)")
        print("2. Tambah Produk Baru (CREATE)")
        print("3. Update Produk (UPDATE)")
        print("4. Hapus Produk (DELETE)")
        print("5. Keluar")
        
        pilihan = input("Pilih menu (1-5): ")
        
        if pilihan == '1':
            print("\n--- DAFTAR PRODUK ---")
            for i, p in enumerate(dm.data, start=1):
                print(f"[{i}] {p.info()}")
                
        elif pilihan == '2':
            print("\n--- TAMBAH PRODUK ---")
            jenis = input("Jenis (contoh: Meja): ")
            brand = input("Brand (contoh: IKEA): ")
            ukuran = input("Ukuran (S/M/L/XL): ")
            try:
                harga = int(input("Harga per item: "))
                terjual = int(input("Jumlah Terjual: "))
            except ValueError:
                print("Harga dan jumlah terjual harus berupa angka!")
                continue
                
            # Asumsi perhitungan profit sederhana untuk produk baru
            hpp = harga * 0.6
            profit_per_item = harga - hpp
            total_profit = profit_per_item * terjual
            
            produk_baru = Produk(
                jenis=jenis, ukuran=ukuran, harga_per_item=harga, stok_awal=10,
                stok_akhir=10-terjual, jumlah_terjual=terjual, tanggal_terjual=datetime.now(),
                brand=brand, hpp=hpp, profit_per_item=profit_per_item, total_profit=total_profit
            )
            dm.tambah_produk(produk_baru)
            exporter.export_semua("output_produk.json")
            exporter.export_rekap(dm.statistik(), dm.top_profit_by_jenis(), "output_rekap.json")
            
        elif pilihan == '3':
            print("\n--- UPDATE PRODUK ---")
            try:
                idx = int(input(f"Masukkan index untuk diupdate (1 - {len(dm.data)}): "))
                index_array = idx - 1
            except ValueError:
                print("Index harus angka!")
                continue
                
            if 0 <= index_array < len(dm.data):
                print("Produk saat ini:", dm.baca_produk(index_array).info())
                jenis = input("Jenis Baru: ")
                brand = input("Brand Baru: ")
                ukuran = input("Ukuran Baru (S/M/L/XL): ")
                try:
                    harga = int(input("Harga Baru per item: "))
                    terjual = int(input("Jumlah Terjual Baru: "))
                except ValueError:
                    print("Harga dan jumlah terjual harus berupa angka!")
                    continue
                    
                hpp = harga * 0.6
                profit_per_item = harga - hpp
                total_profit = profit_per_item * terjual
                
                produk_update = Produk(
                    jenis=jenis, ukuran=ukuran, harga_per_item=harga, stok_awal=10,
                    stok_akhir=10-terjual, jumlah_terjual=terjual, tanggal_terjual=datetime.now(),
                    brand=brand, hpp=hpp, profit_per_item=profit_per_item, total_profit=total_profit
                )
                dm.update_produk(index_array, produk_update)
                exporter.export_semua("output_produk.json")
                exporter.export_rekap(dm.statistik(), dm.top_profit_by_jenis(), "output_rekap.json")
            else:
                print("Index tidak valid!")
                
        elif pilihan == '4':
            print("\n--- HAPUS PRODUK ---")
            try:
                idx = int(input(f"Masukkan index untuk dihapus (1 - {len(dm.data)}): "))
                index_array = idx - 1
            except ValueError:
                print("Index harus angka!")
                continue
            dm.hapus_produk(index_array)
            exporter.export_semua("output_produk.json")
            exporter.export_rekap(dm.statistik(), dm.top_profit_by_jenis(), "output_rekap.json")
            
        elif pilihan == '5':
            print("\nKeluar dari program...")
            break
            
        else:
            print("Pilihan tidak valid, coba lagi.")

    print("\nProgram selesai! File JSON tersedia.")
    print("=" * 60)