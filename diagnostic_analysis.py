"""
Diagnostic Analytics Module for BPJS Registration Failures
Analisis Penyebab Kegagalan Pendaftaran Pasien BPJS Melalui APM (Anjungan Pendaftaran Mandiri)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from database.database import BPJSQueryManager
from typing import Optional, Dict, Any, List, Tuple
import re
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os


class DiagnosticAnalyzer:
    """Kelas untuk menganalisis penyebab kegagalan pendaftaran pasien BPJS"""
    
    def __init__(self):
        """Inisialisasi analyzer"""
        # Default behavior: do not auto-fallback to CSV. Callers may set analyzer.fallback_mode
        self.db_manager = BPJSQueryManager()
        self.fallback_mode = 'ask'  # options: 'ask' (default), 'csv', 'auto'
        self.fallback_csv_path: Optional[str] = None
        
    def load_registration_logs(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Memuat data log pendaftaran pasien dari database
        Kolom yang diharapkan: status_kirim, waktu, keterangan error, asal_pendaftaran
        """
        # Load patient data yang berisi informasi pendaftaran (with optional fallback)
        if self.fallback_csv_path is not None:
            patient_data = self.db_manager.load_patient_data_with_fallback(start_date, end_date, fallback=self.fallback_mode, csv_path=self.fallback_csv_path)
        else:
            patient_data = self.db_manager.load_patient_data_with_fallback(start_date, end_date, fallback=self.fallback_mode)

        # Load service logs untuk informasi error lebih detail (with optional fallback)
        if self.fallback_csv_path is not None:
            service_logs = self.db_manager.load_service_logs_with_fallback(start_date, end_date, fallback=self.fallback_mode, csv_path=self.fallback_csv_path)
        else:
            service_logs = self.db_manager.load_service_logs_with_fallback(start_date, end_date, fallback=self.fallback_mode)

        if patient_data is not None and not patient_data.empty:
            # Rename kolom agar sesuai dengan kebutuhan analisis
            patient_data = patient_data.rename(columns={
                'tgl_registrasi': 'waktu',
                'status_kirim': 'status_kirim',
                'keterangan': 'keterangan_error',
                'USER': 'asal_pendaftaran'
            })

            # Filter kolom yang relevan untuk analisis
            relevant_cols = [
                'waktu', 'status_kirim', 'keterangan_error', 'asal_pendaftaran',
                'no_rawat', 'no_rkm_medis', 'nm_pasien', 'nm_poli', 'nm_dokter'
            ]

            available_cols = [col for col in relevant_cols if col in patient_data.columns]
            patient_data = patient_data[available_cols]

            # Konversi waktu ke datetime jika belum
            if 'waktu' in patient_data.columns:
                patient_data['waktu'] = pd.to_datetime(patient_data['waktu'])

            return patient_data
        else:
            return pd.DataFrame()
    
    def load_data_from_csv(self, csv_path: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Memuat data dari file CSV dengan path spesifik
        """
        try:
            # Check if file exists
            if not os.path.exists(csv_path):
                st.error(f"File CSV tidak ditemukan: {csv_path}")
                return pd.DataFrame()
            
            # Load CSV file with multiple encoding attempts
            df = None
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    st.info(f"Berhasil memuat {len(df)} baris data dari {csv_path} dengan encoding {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    continue
            
            if df is None:
                st.error(f"Gagal membaca file CSV dengan berbagai encoding: {csv_path}")
                return pd.DataFrame()
            
            # Convert date columns if they exist
            date_columns = ['waktu', 'tgl_registrasi', 'tanggal', 'date', 'created_at', 'updated_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    break  # hanya konversi kolom tanggal pertama yang ditemukan
            
            # Filter berdasarkan rentang tanggal jika kolom tanggal ditemukan
            for col in date_columns:
                if col in df.columns:
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Include end date
                    df = df[(df[col] >= start_dt) & (df[col] < end_dt)]
                    break
            
            # Rename columns if needed to match expected format
            column_mapping = {
                'tgl_registrasi': 'waktu',
                'status_kirim': 'status_kirim',
                'keterangan': 'keterangan_error',
                'USER': 'asal_pendaftaran',
                'asal_pendaftaran': 'asal_pendaftaran',
                'nm_pasien': 'nm_pasien',
                'nm_poli': 'nm_poli',
                'nm_dokter': 'nm_dokter',
                'no_rawat': 'no_rawat',
                'no_rkm_medis': 'no_rkm_medis'
            }
            
            # Rename columns based on mapping
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # Ensure required columns exist, create empty ones if missing
            required_columns = ['waktu', 'status_kirim', 'keterangan_error', 'asal_pendaftaran']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''  # Create empty column if missing
            
            # Add any additional columns that might be useful for analysis
            additional_columns = ['no_rawat', 'no_rkm_medis', 'nm_pasien', 'nm_poli', 'nm_dokter']
            for col in additional_columns:
                if col not in df.columns:
                    df[col] = ''
            
            return df
            
        except pd.errors.EmptyDataError:
            st.error("File CSV kosong")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Gagal membaca file CSV: {str(e)}")
            return pd.DataFrame()
    
    def load_bpjs_antrol_csv(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fungsi khusus untuk memuat data dari file bpjs antrol.csv di direktori database
        """
        csv_path = "database/bpjs antrol.csv"
        return self.load_data_from_csv(csv_path, start_date, end_date)
    
    def analyze_registration_failures(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Melakukan analisis awal terhadap kegagalan pendaftaran"""
        if df.empty:
            return {}
        
        # Hitung total kegagalan dan keberhasilan
        total_registrations = len(df)
        successful_registrations = len(df[df['status_kirim'] == 'Sudah Dikirim'])
        failed_registrations = total_registrations - successful_registrations
        
        # Klasifikasi error
        error_types = df['keterangan_error'].value_counts().to_dict()
        
        # Analisis berdasarkan asal pendaftaran
        source_analysis = df.groupby('asal_pendaftaran').agg({
            'status_kirim': ['count', lambda x: (x == 'Sudah Dikirim').sum(), lambda x: (x != 'Sudah Dikirim').sum()]
        }).round(2)
        
        # Rename kolom untuk kemudahan pembacaan
        if not source_analysis.empty:
            source_analysis.columns = ['total', 'berhasil', 'gagal']
            source_analysis['persentase_berhasil'] = (source_analysis['berhasil'] / source_analysis['total'] * 100).round(2)
            source_analysis['persentase_gagal'] = (source_analysis['gagal'] / source_analysis['total'] * 100).round(2)
        
        return {
            'total_registrations': total_registrations,
            'successful_registrations': successful_registrations,
            'failed_registrations': failed_registrations,
            'success_rate': (successful_registrations / total_registrations * 100) if total_registrations > 0 else 0,
            'failure_rate': (failed_registrations / total_registrations * 100) if total_registrations > 0 else 0,
            'error_types': error_types,
            'source_analysis': source_analysis
        }
    
    def cluster_error_messages(self, df: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
        """Melakukan clustering pesan error untuk mengidentifikasi pola kegagalan"""
        if df.empty or 'keterangan_error' not in df.columns:
            return {}
        
        # Hapus baris dengan keterangan error kosong
        df_error = df[df['keterangan_error'].notna() & (df['keterangan_error'] != '')].copy()
        
        if df_error.empty:
            return {}
        
        # Ekstrak pesan error unik
        error_messages = df_error['keterangan_error'].astype(str).tolist()
        
        # Gunakan TF-IDF untuk mengonversi teks ke vektor
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100,
            ngram_range=(1, 2),
            lowercase=True
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(error_messages)
            
            # Terapkan K-means clustering
            n_clusters = min(n_clusters, len(error_messages))
            if n_clusters < 2:
                n_clusters = 1
                
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Tambahkan cluster ke dataframe
            df_error = df_error.copy()
            df_error['cluster'] = clusters
            
            # Analisis setiap cluster
            cluster_analysis = {}
            for cluster_id in range(n_clusters):
                cluster_data = df_error[df_error['cluster'] == cluster_id]
                cluster_messages = cluster_data['keterangan_error'].tolist()
                
                # Temukan kata kunci paling umum dalam cluster
                all_text = ' '.join(cluster_messages).lower()
                words = re.findall(r'\b\w+\b', all_text)
                common_words = Counter(words).most_common(10)
                
                cluster_analysis[f'cluster_{cluster_id}'] = {
                    'size': len(cluster_data),
                    'common_messages': cluster_data['keterangan_error'].value_counts().head(5).to_dict(),
                    'common_words': common_words,
                    'asal_pendaftaran': cluster_data['asal_pendaftaran'].value_counts().to_dict(),
                    'status_distribusi': cluster_data['status_kirim'].value_counts().to_dict()
                }
            
            return {
                'clusters': cluster_analysis,
                'cluster_labels': clusters,
                'vectorizer': vectorizer,
                'kmeans_model': kmeans
            }
        except Exception as e:
            st.error(f"Error dalam clustering error messages: {str(e)}")
            return {}

    def visualize_cluster_analysis(self, df: pd.DataFrame):
        """Visualisasi cluster berdasarkan asal pendaftaran dan status kegagalan"""
        if df.empty:
            st.warning("Tidak ada data untuk divisualisasikan")
            return
        
        # Lakukan clustering
        clusters = self.cluster_error_messages(df)
        
        if not clusters:
            st.warning("Tidak ada cluster yang dihasilkan")
            return
        
        # Buat visualisasi cluster
        st.subheader("Visualisasi Cluster Kegagalan Berdasarkan Asal Pendaftaran")
        
        # Membuat dataframe untuk visualisasi
        cluster_data = []
        for cluster_id, cluster_info in clusters['clusters'].items():
            for asal, count in cluster_info['asal_pendaftaran'].items():
                # Menentukan status cluster berdasarkan status distribusi
                status_cluster = "Berhasil" if "Sudah Dikirim" in cluster_info['status_distribusi'] else "Gagal"
                
                cluster_data.append({
                    'Cluster': cluster_id,
                    'Asal Pendaftaran': asal,
                    'Jumlah': count,
                    'Status': status_cluster
                })
        
        if cluster_data:
            cluster_df = pd.DataFrame(cluster_data)
            
            # Membuat visualisasi dengan Plotly
            fig = px.scatter(cluster_df,
                           x='Asal Pendaftaran',
                           y='Cluster',
                           size='Jumlah',
                           color='Status',
                           hover_data=['Jumlah'],
                           title='Distribusi Cluster Kegagalan Berdasarkan Asal Pendaftaran',
                           color_discrete_map={'Berhasil': 'green', 'Gagal': 'red'})
            
            fig.update_layout(
                xaxis_title="Asal Pendaftaran",
                yaxis_title="Cluster",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Visualisasi tambahan: Bar chart distribusi asal pendaftaran per cluster
            st.subheader("Distribusi Asal Pendaftaran dalam Setiap Cluster")
            
            # Membuat pivot table untuk distribusi
            pivot_data = []
            for cluster_id, cluster_info in clusters['clusters'].items():
                for asal, count in cluster_info['asal_pendaftaran'].items():
                    pivot_data.append({
                        'Cluster': cluster_id,
                        'Asal Pendaftaran': asal,
                        'Jumlah': count
                    })
            
            if pivot_data:
                pivot_df = pd.DataFrame(pivot_data)
                
                # Membuat bar chart
                fig2 = px.bar(pivot_df,
                             x='Cluster',
                             y='Jumlah',
                             color='Asal Pendaftaran',
                             title='Distribusi Asal Pendaftaran dalam Setiap Cluster',
                             barmode='group')
                
                fig2.update_layout(
                    xaxis_title="Cluster",
                    yaxis_title="Jumlah Kegagalan",
                    showlegend=True
                )
                
                st.plotly_chart(fig2, use_container_width=True)
    
    def cross_tab_status_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Membuat cross-tabulasi status_kirim vs waktu"""
        if df.empty:
            return {}
        
        # Tambahkan kolom waktu dalam format yang lebih detail
        df_copy = df.copy()
        
        if 'waktu' in df_copy.columns:
            df_copy['waktu'] = pd.to_datetime(df_copy['waktu'])
            df_copy['tanggal'] = df_copy['waktu'].dt.date
            df_copy['jam'] = df_copy['waktu'].dt.hour
            df_copy['hari'] = df_copy['waktu'].dt.day_name()
            df_copy['bulan'] = df_copy['waktu'].dt.month_name()
        
        # Cross-tabulasi berdasarkan tanggal
        if 'tanggal' in df_copy.columns and 'status_kirim' in df_copy.columns:
            date_crosstab = pd.crosstab(df_copy['tanggal'], df_copy['status_kirim'], margins=True)
            
            # Cross-tabulasi berdasarkan jam
            hour_crosstab = pd.crosstab(df_copy['jam'], df_copy['status_kirim'], margins=True) if 'jam' in df_copy.columns else pd.DataFrame()
            
            # Cross-tabulasi berdasarkan hari
            day_crosstab = pd.crosstab(df_copy['hari'], df_copy['status_kirim'], margins=True) if 'hari' in df_copy.columns else pd.DataFrame()
            # Fix the column name - it should be 'All' not 'All' with a typo
            
            return {
                'date_crosstab': date_crosstab,
                'hour_crosstab': hour_crosstab,
                'day_crosstab': day_crosstab
            }
        else:
            return {}
    
    def identify_root_causes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identifikasi akar penyebab kegagalan pendaftaran"""
        if df.empty:
            return {}
        
        # Analisis berdasarkan berbagai faktor
        root_causes = {}
        
        # 1. Analisis berdasarkan asal pendaftaran
        if 'asal_pendaftaran' in df.columns:
            source_failures = df[df['status_kirim'] != 'Sudah Dikirim'].groupby('asal_pendaftaran').size()
            total_by_source = df.groupby('asal_pendaftaran').size()
            failure_rate_by_source = (source_failures / total_by_source * 100).fillna(0)
            root_causes['failure_rate_by_source'] = failure_rate_by_source.sort_values(ascending=False)
        
        # 2. Analisis berdasarkan poliklinik
        if 'nm_poli' in df.columns:
            poli_failures = df[df['status_kirim'] != 'Sudah Dikirim'].groupby('nm_poli').size()
            total_by_poli = df.groupby('nm_poli').size()
            failure_rate_by_poli = (poli_failures / total_by_poli * 100).fillna(0)
            root_causes['failure_rate_by_poli'] = failure_rate_by_poli.sort_values(ascending=False)
        
        # 3. Analisis berdasarkan jam
        if 'waktu' in df.columns:
            df_copy = df.copy()
            df_copy['jam'] = pd.to_datetime(df_copy['waktu']).dt.hour
            hour_failures = df_copy[df_copy['status_kirim'] != 'Sudah Dikirim'].groupby('jam').size()
            total_by_hour = df_copy.groupby('jam').size()
            failure_rate_by_hour = (hour_failures / total_by_hour * 100).fillna(0)
            root_causes['failure_rate_by_hour'] = failure_rate_by_hour.sort_values(ascending=False)
        
        # 4. Analisis error messages umum
        if 'keterangan_error' in df.columns:
            error_counts = df['keterangan_error'].value_counts()
            root_causes['common_errors'] = error_counts.head(10)
        
        return root_causes
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insight berdasarkan analisis data"""
        insights = []
        
        if df.empty:
            return insights
        
        # Hitung statistik dasar
        total_registrations = len(df)
        successful = len(df[df['status_kirim'] == 'Sudah Dikirim'])
        failed = total_registrations - successful
        success_rate = (successful / total_registrations * 100) if total_registrations > 0 else 0
        
        insights.append(f"Total pendaftaran: {total_registrations}")
        insights.append(f"Kegagalan pendaftaran: {failed} ({failed/total_registrations*100:.2f}%)")
        insights.append(f"Tingkat keberhasilan: {success_rate:.2f}%")
        
        # Tambahkan insight berdasarkan error paling umum
        if 'keterangan_error' in df.columns:
            common_errors = df['keterangan_error'].value_counts().head(3)
            if not common_errors.empty:
                insights.append("3 error paling umum:")
                for error, count in common_errors.items():
                    insights.append(f"  - {error}: {count} kali")
        
        # Insight berdasarkan asal pendaftaran
        if 'asal_pendaftaran' in df.columns:
            source_failures = df[df['status_kirim'] != 'Sudah Dikirim'].groupby('asal_pendaftaran').size()
            if not source_failures.empty:
                worst_source = source_failures.idxmax()
                worst_count = source_failures.max()
                insights.append(f"Asal pendaftaran dengan kegagalan terbanyak: {worst_source} ({worst_count} kegagalan)")
        
        return insights
    
    def create_comprehensive_visualization(self, df: pd.DataFrame):
        """Create a comprehensive visualization with multiple plots in a single frame"""
        
        if df.empty:
            st.warning("Tidak ada data untuk divisualisasikan")
            return
        
        # Create subplots with multiple visualization types
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribusi Status Kirim', 'Tren Harian Pendaftaran',
                           'Kegagalan Berdasarkan Asal Pendaftaran', 'Distribusi Pendaftaran per Jam'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 1. Pie chart: Distribusi Status Kirim
        if 'status_kirim' in df.columns:
            status_counts = df['status_kirim'].value_counts()
            fig.add_trace(
                go.Pie(labels=status_counts.index, values=status_counts.values, name="Status Kirim", showlegend=True),
                row=1, col=1
            )
        
        # 2. Daily trend: Group by date
        if 'waktu' in df.columns and 'status_kirim' in df.columns:
            df_plot = df.copy()
            df_plot['tanggal'] = pd.to_datetime(df_plot['waktu']).dt.date
            daily_trend = df_plot.groupby(['tanggal', 'status_kirim']).size().unstack(fill_value=0)
            
            for i, col in enumerate(daily_trend.columns):
                fig.add_trace(
                    go.Scatter(x=daily_trend.index, y=daily_trend[col],
                              mode='lines+markers', name=f'{col}', showlegend=True),
                    row=1, col=2
                )
        
        # 3. Bar chart: Failure rate by source
        if 'asal_pendaftaran' in df.columns and 'status_kirim' in df.columns:
            # Calculate failure rate by source
            df_plot = df.copy()
            df_plot['is_failure'] = df_plot['status_kirim'] != 'Sudah Dikirim'
            failure_rate = df_plot.groupby('asal_pendaftaran')['is_failure'].mean() * 100
            failure_rate = failure_rate.sort_values(ascending=True)  # Sort ascending for better visualization
            
            fig.add_trace(
                go.Bar(x=failure_rate.values, y=failure_rate.index,
                       orientation='h', name='Tingkat Kegagalan', showlegend=True),
                row=2, col=1
            )
        
        # 4. Hourly distribution
        if 'waktu' in df.columns and 'status_kirim' in df.columns:
            df_plot = df.copy()
            df_plot['jam'] = pd.to_datetime(df_plot['waktu']).dt.hour
            hourly_dist = df_plot.groupby(['jam', 'status_kirim']).size().unstack(fill_value=0)
            
            for i, col in enumerate(hourly_dist.columns):
                fig.add_trace(
                    go.Bar(x=hourly_dist.index, y=hourly_dist[col],
                           name=f'{col}', showlegend=True),
                    row=2, col=2
                )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Diagnostic Analytics: Analisis Penyebab Kegagalan Pendaftaran Pasien BPJS",
            title_x=0.5,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.1
            )
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Status", row=1, col=1)
        fig.update_xaxes(title_text="Tanggal", row=1, col=2)
        fig.update_yaxes(title_text="Tingkat Kegagalan (%)", row=2, col=1)
        fig.update_xaxes(title_text="Jam", row=2, col=2)
        fig.update_yaxes(title_text="Jumlah", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)


class PredictiveAnalyzer:
    """Kelas untuk melakukan prediksi kegagalan pendaftaran pasien BPJS"""
    
    def __init__(self):
        """Inisialisasi analyzer prediktif"""
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(kernel='rbf', random_state=42, probability=True)
        }
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.best_model = None
        self.best_model_name = None
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str], LabelEncoder, Optional[LabelEncoder]]:
        """Menyiapkan fitur untuk prediksi kegagalan pendaftaran"""
        if df.empty:
            # Return empty structures with correct types
            return pd.DataFrame(), pd.Series(dtype=int), [], LabelEncoder(), None
        
        # Buat salinan dataframe
        df_features = df.copy()
        
        # Konversi waktu ke format yang bisa digunakan untuk ekstraksi fitur
        if 'waktu' in df_features.columns:
            df_features['waktu'] = pd.to_datetime(df_features['waktu'], errors='coerce')
            df_features['jam'] = df_features['waktu'].dt.hour
            df_features['hari'] = df_features['waktu'].dt.dayofweek  # 0=Monday, 6=Sunday
            df_features['bulan'] = df_features['waktu'].dt.month
            df_features['kuartal'] = df_features['waktu'].dt.quarter
            
        # Buat label target (1 untuk gagal, 0 untuk berhasil)
        df_features['target'] = (df_features['status_kirim'] != 'Sudah Dikirim').astype(int)
        
        # Encode asal_pendaftaran
        le_source = LabelEncoder()
        if 'asal_pendaftaran' in df_features.columns:
            df_features['asal_pendaftaran_encoded'] = le_source.fit_transform(df_features['asal_pendaftaran'].astype(str))
        else:
            df_features['asal_pendaftaran_encoded'] = 0  # Default value if column doesn't exist
            
        # Encode nm_poli jika tersedia
        le_poli = None
        if 'nm_poli' in df_features.columns:
            le_poli = LabelEncoder()
            df_features['nm_poli_encoded'] = le_poli.fit_transform(df_features['nm_poli'].astype(str))
        else:
            df_features['nm_poli_encoded'] = 0  # Default value if column doesn't exist
            
        # Pilih fitur yang akan digunakan untuk prediksi
        feature_columns = []
        if 'jam' in df_features.columns:
            feature_columns.extend(['jam'])
        if 'hari' in df_features.columns:
            feature_columns.extend(['hari'])
        if 'bulan' in df_features.columns:
            feature_columns.extend(['bulan'])
        if 'kuartal' in df_features.columns:
            feature_columns.extend(['kuartal'])
        if 'asal_pendaftaran_encoded' in df_features.columns:
            feature_columns.extend(['asal_pendaftaran_encoded'])
        if 'nm_poli_encoded' in df_features.columns:
            feature_columns.extend(['nm_poli_encoded'])
            
        # Tambahkan fitur-fitur numerik tambahan jika tersedia
        numeric_columns = df_features.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_columns:
            if col not in feature_columns and col != 'target':
                feature_columns.append(col)
                
        # Ambil hanya fitur yang tersedia
        available_features = [col for col in feature_columns if col in df_features.columns]
        X = df_features[available_features]
        y = df_features['target']
        
        return X, y, available_features, le_source, le_poli
        
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Melatih model-model untuk prediksi kegagalan pendaftaran"""
        if df.empty:
            return {}
            
        # Siapkan fitur
        X, y, feature_names, le_source, le_poli = self.prepare_features(df)
        
        if X.empty or len(X) == 0:
            st.warning("Dataset tidak memiliki fitur yang cukup untuk pelatihan.")
            return {}
            
        # Cek apakah hanya ada satu kelas unik dalam y
        unique_classes = y.unique()
        if len(unique_classes) <= 1:
            st.warning(f"Dataset hanya memiliki satu kelas: {unique_classes}. Tidak bisa melatih model klasifikasi. Silakan gunakan data yang memiliki kegagalan dan keberhasilan pendaftaran.")
            # Kembalikan informasi dasar meskipun tidak bisa melatih model
            return {
                'feature_names': feature_names,
                'X_test': pd.DataFrame(),
                'y_test': pd.Series(),
                'X_train': pd.DataFrame(),
                'y_train': pd.Series(),
                'le_source': le_source,
                'le_poli': le_poli,
                'models': {},
                'best_model_name': None,
                'error': 'single_class_dataset'
            }
            
        # Split data menjadi training dan testing (80:20)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Normalisasi fitur
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {
            'feature_names': feature_names,
            'X_test': X_test,
            'y_test': y_test,
            'X_train': X_train,
            'y_train': y_train,
            'le_source': le_source,
            'le_poli': le_poli
        }
        
        model_results = {}
        best_score = 0
        
        # Latih dan evaluasi setiap model
        for model_name, model in self.models.items():
            try:
                # Train model
                if model_name == 'random_forest':
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    # Simpan feature importance untuk Random Forest
                    self.feature_importance = model.feature_importances_
                else: # SVM
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    
                # Evaluasi model
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                
                # Hitung skor rata-rata untuk menentukan model terbaik
                avg_score = (accuracy + precision + recall) / 3
                
                model_results[model_name] = {
                    'model': model,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'y_pred': y_pred,
                    'classification_report': classification_report(y_test, y_pred, output_dict=True),
                    'confusion_matrix': confusion_matrix(y_test, y_pred)
                }
                
                # Simpan model terbaik
                if avg_score > best_score:
                    best_score = avg_score
                    self.best_model = model
                    self.best_model_name = model_name
            except ValueError as e:
                st.warning(f"Model {model_name} gagal dilatih: {str(e)}")
                continue
                
        results['models'] = model_results
        results['best_model_name'] = self.best_model_name
        
        return results
        
    def predict_failure_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Memprediksi risiko kegagalan pendaftaran untuk data baru"""
        if df.empty or self.best_model is None:
            return df
            
        # Siapkan fitur dari data
        X, _, feature_names, _, _ = self.prepare_features(df)
        available_features = [col for col in feature_names if col in X.columns]
        X = X[available_features]
        
        # Lakukan prediksi
        if self.best_model_name == 'random_forest':
            predictions = self.best_model.predict(X)
            probabilities = self.best_model.predict_proba(X)
        else:  # SVM
            X_scaled = self.scaler.transform(X)
            predictions = self.best_model.predict(X_scaled)
            probabilities = self.best_model.predict_proba(X_scaled)
            
        # Tambahkan hasil prediksi ke dataframe
        df = df.copy()
        df['prediksi_kegagalan'] = predictions
        df['probabilitas_kegagalan'] = probabilities[:, 1] if len(probabilities[0]) > 1 else predictions  # Probabilitas kelas positif (gagal)
        df['risiko'] = df['probabilitas_kegagalan'].apply(lambda x: 'Tinggi' if x > 0.7 else 'Sedang' if x > 0.3 else 'Rendah')
        
        return df
        
    def get_feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        """Mendapatkan pentingnya fitur dalam model"""
        if self.feature_importance is not None and len(feature_names) == len(self.feature_importance):
            importance_df = pd.DataFrame({
                'fitur': feature_names,
                'importance': self.feature_importance
            }).sort_values(by='importance', ascending=False)
            return importance_df
        else:
            return pd.DataFrame()


def main():
    """Fungsi utama untuk menampilkan analisis di Streamlit"""
    st.title("Diagnostic Analytics: Analisis Penyebab Kegagalan Pendaftaran Pasien BPJS")
    
    # Inisialisasi session state jika belum ada
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DiagnosticAnalyzer()
    if 'predictive_analyzer' not in st.session_state:
        st.session_state.predictive_analyzer = None
    if 'training_results' not in st.session_state:
        st.session_state.training_results = None
    
    # Tambahkan tabs untuk memisahkan analisis diagnostik dan prediktif
    tab1, tab2 = st.tabs(["Diagnostic Analysis", "Predictive Analysis"])
    
    with tab1:
        # Sidebar untuk input tanggal
        st.sidebar.header("Parameter Analisis")
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        
        start_date = st.sidebar.date_input("Tanggal Mulai", value=yesterday)
        end_date = st.sidebar.date_input("Tanggal Akhir", value=today)
        
        # Konversi ke datetime.date jika perlu dan pastikan tidak None
        if isinstance(start_date, tuple):
            start_date = start_date[0] if start_date else today
        if isinstance(end_date, tuple):
            end_date = end_date[-1] if end_date else today
        
        # Handle None values explicitly
        if start_date is None:
            start_date = today
        if end_date is None:
            end_date = today
        
        if start_date > end_date:
            st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir")
            return
        
        # Pilihan fallback ketika gagal koneksi database
        st.sidebar.subheader("Opsi fallback jika DB gagal")
        fallback_choice = st.sidebar.selectbox(
            "Jika gagal koneksi DB:",
            ["Jangan gunakan fallback (tampilkan error)", "Gunakan CSV fallback (database/bpjs antrol.csv)"]
        )
        csv_input = st.sidebar.text_input("Path CSV fallback (kosong = default 'database/bpjs antrol.csv')", value="database/bpjs antrol.csv")

        # Inisialisasi analyzer dan set opsi fallback
        analyzer = st.session_state.analyzer
        analyzer.fallback_mode = 'csv' if fallback_choice.startswith('Gunakan') else 'ask'
        analyzer.fallback_csv_path = csv_input.strip() or None
        
        # Opsi untuk memilih sumber data
        data_source = st.sidebar.radio(
            "Sumber Data:",
            ("Database", "CSV File Langsung")
        )
        
        # Tombol untuk memuat data
        if st.sidebar.button("Muat Data"):
            with st.spinner("Memuat data..."):
                if data_source == "Database":
                    df = analyzer.load_registration_logs(str(start_date), str(end_date))
                else:  # CSV File Langsung
                    # Gunakan path CSV yang ditentukan
                    csv_path = csv_input.strip() or "database/bpjs antrol.csv"
                    df = analyzer.load_data_from_csv(csv_path, str(start_date), str(end_date))
                
                if df is not None and not df.empty:
                    st.success(f"Data berhasil dimuat: {len(df)} record ditemukan")
                    st.session_state.df = df  # Simpan ke session state
                    
                    # Tampilkan statistik dasar
                    stats = analyzer.analyze_registration_failures(df)
                    st.subheader("Statistik Pendaftaran")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Pendaftaran", stats['total_registrations'])
                    col2.metric("Berhasil", stats['successful_registrations'])
                    col3.metric("Gagal", stats['failed_registrations'])
                    
                    col4, col5 = st.columns(2)
                    col4.metric("Tingkat Keberhasilan", f"{stats['success_rate']:.2f}%")
                    col5.metric("Tingkat Kegagalan", f"{stats['failure_rate']:.2f}%")
                    
                    # Tampilkan data
                    st.subheader("Data Pendaftaran")
                    st.dataframe(df.head(20))
                    
                    # Analisis kegagalan
                    st.subheader("Analisis Kegagalan")
                    if stats['error_types']:
                        st.write("Jenis-jenis error terbanyak:")
                        error_df = pd.DataFrame(list(stats['error_types'].items()),
                                              columns=['Error', 'Jumlah'])
                        st.dataframe(error_df)
                    
                    # Analisis berdasarkan sumber pendaftaran
                    st.subheader("Analisis Berdasarkan Asal Pendaftaran")
                    if not stats['source_analysis'].empty:
                        st.dataframe(stats['source_analysis'])
                    
                    # Clustering error messages
                    st.subheader("Clustering Pesan Error")
                    with st.spinner("Melakukan clustering pesan error..."):
                        clusters = analyzer.cluster_error_messages(df)
                        if clusters:
                            for cluster_id, cluster_info in clusters['clusters'].items():
                                with st.expander(f"{cluster_id.replace('_', ' ').title()}"):
                                    st.write(f"Jumlah kegagalan: {cluster_info['size']}")
                                    st.write("Pesan error paling umum:")
                                    for msg, count in list(cluster_info['common_messages'].items())[:3]:
                                        st.write(f"- {msg} ({count} kali)")
                                    st.write("Asal pendaftaran dalam cluster ini:")
                                    for source, count in cluster_info['asal_pendaftaran'].items():
                                        st.write(f"- {source}: {count}")
                    
                    # Cross-tabulasi
                    st.subheader("Analisis Waktu vs Status Kirim")
                    crosstab_results = analyzer.cross_tab_status_time(df)
                    
                    # Tampilkan hasil crosstab dengan penanganan 'All' label
                    if crosstab_results['date_crosstab'] is not None and not crosstab_results['date_crosstab'].empty:
                        st.write("Berdasarkan Tanggal:")
                        # Hapus baris/kolom 'All' untuk menghindari konflik tipe data
                        date_crosstab = crosstab_results['date_crosstab'].copy()
                        if 'All' in date_crosstab.index:
                            date_crosstab = date_crosstab.drop('All')
                        if 'All' in date_crosstab.columns:
                            date_crosstab = date_crosstab.drop('All', axis=1)
                        st.dataframe(date_crosstab)
                    
                    if not crosstab_results['hour_crosstab'].empty:
                        st.write("Berdasarkan Jam:")
                        # Hapus baris/kolom 'All' untuk menghindari konflik tipe data
                        hour_crosstab = crosstab_results['hour_crosstab'].copy()
                        if 'All' in hour_crosstab.index:
                            hour_crosstab = hour_crosstab.drop('All')
                        if 'All' in hour_crosstab.columns:
                            hour_crosstab = hour_crosstab.drop('All', axis=1)
                        st.dataframe(hour_crosstab)
                    
                    if not crosstab_results['day_crosstab'].empty:
                        st.write("Berdasarkan Hari:")
                        # Hapus baris/kolom 'All' untuk menghindari konflik tipe data
                        day_crosstab = crosstab_results['day_crosstab'].copy()
                        if 'All' in day_crosstab.index:
                            day_crosstab = day_crosstab.drop('All')
                        if 'All' in day_crosstab.columns:
                            day_crosstab = day_crosstab.drop('All', axis=1)
                        st.dataframe(day_crosstab)
                    
                    # Identifikasi akar penyebab
                    st.subheader("Identifikasi Akar Penyebab")
                    root_causes = analyzer.identify_root_causes(df)
                    
                    if 'failure_rate_by_source' in root_causes:
                        st.write("Tingkat kegagalan berdasarkan asal pendaftaran:")
                        st.dataframe(root_causes['failure_rate_by_source'].to_frame('Tingkat Kegagalan (%)'))
                    
                    if 'failure_rate_by_poli' in root_causes:
                        st.write("Tingkat kegagalan berdasarkan poliklinik:")
                        st.dataframe(root_causes['failure_rate_by_poli'].to_frame('Tingkat Kegagalan (%)'))
                    
                    if 'failure_rate_by_hour' in root_causes:
                        st.write("Tingkat kegagalan berdasarkan jam:")
                        st.dataframe(root_causes['failure_rate_by_hour'].to_frame('Tingkat Kegagalan (%)'))
                    
                    # Generate insights
                    st.subheader("Insight")
                    insights = analyzer.generate_insights(df)
                    for insight in insights:
                        st.info(insight)
                    
                    # Create comprehensive visualization
                    st.subheader("Visualisasi Komprehensif Analisis Kegagalan Pendaftaran")
                    analyzer.create_comprehensive_visualization(df)
                    
                else:
                    st.warning("Tidak ada data yang ditemukan untuk rentang tanggal yang dipilih")
        else:
            st.info("Silakan klik 'Muat Data' untuk memulai analisis")
    
    with tab2:
        st.header("Predictive Analytics: Prediksi Kemungkinan Kegagalan Pendaftaran Pasien BPJS")
        st.write("""
        Analisis ini menggunakan machine learning untuk memprediksi apakah pendaftaran pasien BPJS akan gagal sebelum dikirim ke server BPJS.
        Model menggunakan fitur-fitur seperti jam pendaftaran, asal pendaftaran, dan poliklinik untuk membuat prediksi.
        """)
        
        # Tombol untuk memuat data dan melatih model prediktif
        if st.button("Latih Model Prediksi"):
            with st.spinner("Memuat data dan melatih model..."):
                # Muat data menggunakan parameter dari tab pertama
                predictive_analyzer = PredictiveAnalyzer()
                
                df = st.session_state.df  # Ambil dari session state
                if df is not None and not df.empty:
                    # Gunakan data yang sudah dimuat di tab1
                    training_results = predictive_analyzer.train_models(df)
                    
                    if training_results and 'models' in training_results and len(training_results['models']) > 0:
                        st.success("Model berhasil dilatih!")
                        
                        # Tampilkan metrik evaluasi untuk setiap model
                        st.subheader("Evaluasi Model")
                        models = training_results['models']
                        
                        for model_name, model_info in models.items():
                            st.write(f"**{model_name.upper()}**")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Akurasi", f"{model_info['accuracy']:.3f}")
                            col2.metric("Precision", f"{model_info['precision']:.3f}")
                            col3.metric("Recall", f"{model_info['recall']:.3f}")
                            
                            # Tampilkan classification report
                            st.text("Classification Report:")
                            st.text(classification_report(training_results['y_test'], model_info['y_pred']))
                            
                            # Tampilkan confusion matrix
                            st.text("Confusion Matrix:")
                            cm = model_info['confusion_matrix']
                            fig, ax = plt.subplots(figsize=(6, 4))
                            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
                            ax.set_xlabel('Prediksi')
                            ax.set_ylabel('Aktual')
                            ax.set_title(f'Confusion Matrix - {model_name}')
                            st.pyplot(fig)
                            plt.clf()
                            
                            st.markdown("---")
                        
                        # Tampilkan feature importance untuk model terbaik
                        if training_results['best_model_name'] == 'random_forest':
                            st.subheader("Feature Importance (Random Forest)")
                            importance_df = predictive_analyzer.get_feature_importance(training_results['feature_names'])
                            if not importance_df.empty:
                                st.dataframe(importance_df)
                                
                                # Visualisasi feature importance
                                fig, ax = plt.subplots(figsize=(10, 6))
                                sns.barplot(data=importance_df.head(10), x='importance', y='fitur', ax=ax)
                                ax.set_title('Top 10 Feature Importance')
                                st.pyplot(fig)
                                plt.clf()
                                
                                # Tambahkan informasi tentang faktor paling berpengaruh
                                st.subheader("Faktor Paling Berpengaruh terhadap Kegagalan Pendaftaran")
                                top_factors = importance_df.head(5)
                                for idx, row in top_factors.iterrows():
                                    st.write(f"- {row['fitur']}: {row['importance']:.4f}")
                        
                        # Tampilkan prediksi pada data uji
                        st.subheader("Prediksi pada Data Uji")
                        X_test = training_results['X_test']
                        y_test = training_results['y_test']
                        
                        # Tambahkan hasil prediksi ke data uji
                        test_df = X_test.copy()
                        test_df['aktual'] = y_test.values
                        test_df['prediksi'] = models[training_results['best_model_name']]['y_pred']
                        
                        # Decode asal_pendaftaran dan nm_poli jika tersedia
                        if 'asal_pendaftaran_encoded' in test_df.columns:
                            le_source = training_results['le_source']
                            test_df['asal_pendaftaran'] = le_source.inverse_transform(X_test['asal_pendaftaran_encoded'].astype(int))
                        
                        if 'nm_poli_encoded' in test_df.columns:
                            le_poli = training_results['le_poli']
                            if le_poli is not None:
                                test_df['nm_poli'] = le_poli.inverse_transform(X_test['nm_poli_encoded'].astype(int))
                        
                        st.dataframe(test_df.head(20))
                        
                        # Tambahkan informasi tentang model terbaik
                        st.success(f"Model terbaik: {training_results['best_model_name'].upper()}")
                        
                        # Simpan model analyzer ke session state untuk digunakan nanti
                        st.session_state.predictive_analyzer = predictive_analyzer
                        st.session_state.training_results = training_results
                    elif 'error' in training_results and training_results['error'] == 'single_class_dataset':
                        # Kasus khusus: dataset hanya memiliki satu kelas
                        st.warning("Dataset hanya memiliki satu kelas. Tidak bisa melatih model klasifikasi.")
                        st.info("Silakan gunakan dataset yang memiliki kombinasi kegagalan dan keberhasilan pendaftaran untuk melatih model prediktif.")
                    else:
                        st.error("Gagal melatih model. Pastikan data memiliki kolom yang diperlukan.")
                else:
                    st.error("Silakan muat data terlebih dahulu di tab Diagnostic Analysis")
        
        # Bagian untuk prediksi data baru jika model sudah dilatih
        if st.session_state.predictive_analyzer is not None and st.session_state.training_results is not None:
            st.subheader("Prediksi untuk Data Baru")
            st.write("Model akan membuat prediksi berdasarkan data yang dimuat sebelumnya.")
            
            if st.button("Lakukan Prediksi"):
                with st.spinner("Melakukan prediksi..."):
                    # Gunakan data asli untuk prediksi
                    df = st.session_state.df  # Ambil dari session state
                    if df is not None and not df.empty:
                        predicted_df = st.session_state.predictive_analyzer.predict_failure_risk(df)
                        
                        # Tampilkan hasil prediksi
                        st.success("Prediksi selesai!")
                        
                        # Tampilkan ringkasan prediksi
                        st.write("Ringkasan Prediksi:")
                        prediction_summary = predicted_df['risiko'].value_counts()
                        st.bar_chart(prediction_summary)
                        
                        # Tampilkan beberapa contoh hasil prediksi
                        st.write("Contoh hasil prediksi:")
                        prediction_cols = ['waktu', 'asal_pendaftaran', 'nm_poli', 'status_kirim', 'prediksi_kegagalan', 'probabilitas_kegagalan', 'risiko']
                        available_cols = [col for col in prediction_cols if col in predicted_df.columns]
                        st.dataframe(predicted_df[available_cols].head(20))
                        
                        # Tampilkan distribusi prediksi vs aktual
                        if 'prediksi_kegagalan' in predicted_df.columns and 'target' in predicted_df.columns:
                            st.write("Perbandingan Prediksi vs Aktual:")
                            comparison_df = predicted_df[['prediksi_kegagalan', 'target']].copy()
                            comparison_df.columns = ['Prediksi', 'Aktual']
                            st.dataframe(comparison_df.head(20))


if __name__ == "__main__":
    main()