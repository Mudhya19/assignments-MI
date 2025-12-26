"""
Database Module untuk Koneksi dan Query BPJS
"""

import MySQLdb
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os


class DatabaseManager:
    """Kelas untuk mengelola koneksi dan operasi database"""
    
    def __init__(self):
        """Inisialisasi konfigurasi database"""
        self.config = {
            'host': os.getenv("DB_HOST", "192.168.11.5"),
            'user': os.getenv("DB_USER", "rsds_db"),
            'passwd': os.getenv("DB_PASS", "rsdsD4t4b4s3"),
            'db': os.getenv("DB_NAME", "rsds_db"),
            'port': int(os.getenv("DB_PORT", 3306))
        }
    
    def get_connection(self) -> Optional[MySQLdb.Connection]:
        """Membuat dan mengembalikan koneksi MySQL database"""
        try:
            connection = MySQLdb.connect(**self.config)
            return connection
        except MySQLdb.Error as err:
            st.error(f"Error Koneksi Database: {err}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[pd.DataFrame]:
        """Eksekusi query SQL dan mengembalikan hasil sebagai DataFrame"""
        connection = self.get_connection()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor(MySQLdb.cursors.DictCursor)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return pd.DataFrame(data) if data else pd.DataFrame()
            
        except MySQLdb.Error as err:
            st.error(f"Error Query Database: {err}")
            if connection:
                connection.close()
            return None


class BPJSQueryManager(DatabaseManager):
    """Kelas khusus untuk query BPJS yang mewarisi DatabaseManager"""
    
    def format_jam_reg(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format kolom jam_reg menjadi format HH:MM:SS"""
        if 'jam_reg' in data.columns:
            def format_time(value):
                if isinstance(value, str):
                    try:
                        if len(value) <= 5:
                            return datetime.strptime(value, '%H:%M').strftime('%H:%M:%S')
                        elif len(value) == 8:
                            return value
                    except ValueError:
                        return value
                elif isinstance(value, timedelta):
                    total_seconds = int(value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    return f"{hours:02}:{minutes:02}:{seconds:02}"
                return value
            
            data['jam_reg'] = data['jam_reg'].apply(format_time)
        return data
    
    @st.cache_data(show_spinner=True)
    def load_patient_data(_self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Memuat data pasien BPJS dari database"""
        query = """
        SELECT
            rp.no_rawat,
            rp.tgl_registrasi,
            rp.jam_reg,
            rp.kd_dokter,
            d.nm_dokter,
            rp.no_rkm_medis,
            pas.nm_pasien,
            rp.kd_poli,
            p.nm_poli,
            rp.status_lanjut,
            rp.kd_pj,
            pj.png_jawab,
            mar.tanggal_periksa,
            mar.nomor_kartu,
            mar.nomor_referensi,
            mar.kodebooking,
            mar.jenis_kunjungan,
            mar.status_kirim,
            mar.keterangan,
            bs.USER 
        FROM
            reg_periksa rp
            JOIN mlite_antrian_referensi mar ON rp.no_rkm_medis = mar.no_rkm_medis
            JOIN poliklinik p ON rp.kd_poli = p.kd_poli
            JOIN dokter d ON rp.kd_dokter = d.kd_dokter
            JOIN penjab pj ON rp.kd_pj = pj.kd_pj
            JOIN pasien pas ON rp.no_rkm_medis = pas.no_rkm_medis
            JOIN bridging_sep bs ON rp.no_rawat = bs.no_rawat 
        WHERE
            rp.tgl_registrasi BETWEEN %s AND %s
            AND mar.tanggal_periksa BETWEEN %s AND %s
            AND rp.kd_poli NOT IN ('IGDK', 'HDL', 'BBL', 'IRM', '006', 'U0016')
            AND rp.status_lanjut NOT IN ('Ranap')
        ORDER BY
            rp.no_rawat;
        """
        
        params = (start_date, end_date, start_date, end_date)
        df = _self.execute_query(query, params)
        
        if df is not None and not df.empty:
            return _self.format_jam_reg(df)
        return df

    def load_patient_data_with_fallback(self, start_date: str, end_date: str, fallback: str = 'ask', csv_path: str = None) -> Optional[pd.DataFrame]:
        """Try to load patient data from database, otherwise optionally fallback to CSV.

        fallback: one of 'ask' (default, do not auto-read CSV), 'csv' or 'auto' (auto-read CSV)
        csv_path: optional explicit path to CSV file; if None uses bundled 'bpjs antrol.csv' in this folder
        """
        df = self.load_patient_data(start_date, end_date)

        if df is not None and not df.empty:
            return df

        # If DB returned None or empty and fallback requested, try CSV
        if fallback in ('csv', 'auto'):
            csv_file = csv_path or os.path.join(os.path.dirname(__file__), 'bpjs antrol.csv')
            if os.path.exists(csv_file):
                try:
                    df_csv = pd.read_csv(csv_file)

                    # Try to normalize and filter by dates if possible
                    for col in ['tgl_registrasi', 'tanggal_periksa']:
                        if col in df_csv.columns:
                            df_csv[col] = pd.to_datetime(df_csv[col], errors='coerce')

                    try:
                        start_dt = pd.to_datetime(start_date).date()
                        end_dt = pd.to_datetime(end_date).date()
                        if 'tgl_registrasi' in df_csv.columns:
                            mask = (df_csv['tgl_registrasi'].dt.date >= start_dt) & (df_csv['tgl_registrasi'].dt.date <= end_dt)
                            df_csv = df_csv.loc[mask]
                        elif 'tanggal_periksa' in df_csv.columns:
                            mask = (df_csv['tanggal_periksa'].dt.date >= start_dt) & (df_csv['tanggal_periksa'].dt.date <= end_dt)
                            df_csv = df_csv.loc[mask]
                    except Exception:
                        # If date filtering fails, continue with full CSV
                        pass

                    if not df_csv.empty:
                        return self.format_jam_reg(df_csv)
                    return df_csv
                except Exception as e:
                    st.error(f"Error membaca CSV fallback: {e}")
            else:
                st.warning(f"File CSV fallback tidak ditemukan: {csv_file}")

        # No fallback or fallback failed
        return df
    
    @st.cache_data(show_spinner=True)
    def load_service_logs(_self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Memuat data service logs dari database"""
        query = """
        SELECT 
            *
        FROM 
            mlite_query_logs 
        WHERE 
            DATE(created_at) BETWEEN %s AND %s
        ORDER BY 
            created_at DESC;
        """
        
        params = (start_date, end_date)
        return _self.execute_query(query, params)

    def load_service_logs_with_fallback(self, start_date: str, end_date: str, fallback: str = 'ask', csv_path: str = None) -> Optional[pd.DataFrame]:
        """Try to load service logs from DB, otherwise optionally fallback to CSV (same CSV file may contain logs).
        """
        df = self.load_service_logs(start_date, end_date)

        if df is not None and not df.empty:
            return df

        if fallback in ('csv', 'auto'):
            csv_file = csv_path or os.path.join(os.path.dirname(__file__), 'bpjs antrol.csv')
            if os.path.exists(csv_file):
                try:
                    df_csv = pd.read_csv(csv_file)
                    # If the CSV contains a 'created_at' or similar, try to filter
                    for col in ['created_at', 'tanggal_periksa', 'tgl_registrasi']:
                        if col in df_csv.columns:
                            try:
                                df_csv[col] = pd.to_datetime(df_csv[col], errors='coerce')
                            except Exception:
                                pass

                    try:
                        start_dt = pd.to_datetime(start_date).date()
                        end_dt = pd.to_datetime(end_date).date()
                        for date_col in ['created_at', 'tanggal_periksa', 'tgl_registrasi']:
                            if date_col in df_csv.columns:
                                mask = (df_csv[date_col].dt.date >= start_dt) & (df_csv[date_col].dt.date <= end_dt)
                                df_csv = df_csv.loc[mask]
                                break
                    except Exception:
                        pass

                    return df_csv
                except Exception as e:
                    st.error(f"Error membaca CSV fallback untuk service logs: {e}")
            else:
                st.warning(f"File CSV fallback tidak ditemukan: {csv_file}")

        return df
    
    def get_patient_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Mendapatkan statistik pasien dalam rentang tanggal tertentu"""
        query = """
        SELECT 
            COUNT(*) as total_kunjungan,
            COUNT(DISTINCT rp.no_rkm_medis) as total_pasien_unik,
            COUNT(DISTINCT rp.kd_poli) as total_poliklinik,
            COUNT(DISTINCT rp.kd_dokter) as total_dokter
        FROM reg_periksa rp
        WHERE rp.tgl_registrasi BETWEEN %s AND %s
        """
        
        params = (start_date, end_date)
        result = self.execute_query(query, params)
        
        if result is not None and not result.empty:
            return result.iloc[0].to_dict()
        return {}
    
    def get_top_poliklinik(self, start_date: str, end_date: str, limit: int = 10) -> Optional[pd.DataFrame]:
        """Mendapatkan top poliklinik berdasarkan jumlah kunjungan"""
        query = """
        SELECT 
            p.nm_poli,
            COUNT(*) as jumlah_kunjungan
        FROM reg_periksa rp
        JOIN poliklinik p ON rp.kd_poli = p.kd_poli
        WHERE rp.tgl_registrasi BETWEEN %s AND %s
        GROUP BY rp.kd_poli, p.nm_poli
        ORDER BY jumlah_kunjungan DESC
        LIMIT %s
        """
        
        params = (start_date, end_date, limit)
        return self.execute_query(query, params)
    
    def get_hourly_distribution(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Mendapatkan distribusi kunjungan per jam"""
        query = """
        SELECT 
            HOUR(rp.jam_reg) as jam,
            COUNT(*) as jumlah_kunjungan
        FROM reg_periksa rp
        WHERE rp.tgl_registrasi BETWEEN %s AND %s
        GROUP BY HOUR(rp.jam_reg)
        ORDER BY jam
        """
        
        params = (start_date, end_date)
        return self.execute_query(query, params)