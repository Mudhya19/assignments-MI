"""
Predictive Analytics Module for BPJS Registration Failures
Topik: Prediksi Kemungkinan Kegagalan Pendaftaran Pasien BPJS
Bisakah sistem memprediksi lebih awal apakah pendaftaran pasien BPJS akan gagal sebelum dikirim ke server BPJS?
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os

# Import database manager
from database.database import BPJSQueryManager

class BPJSPredictiveAnalyzer:
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
        self.label_encoders = {}
        
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Menyiapkan fitur untuk prediksi kegagalan pendaftaran"""
        if df.empty:
            return pd.DataFrame(), pd.Series(dtype=int), []
        
        # Buat salinan dataframe
        df_features = df.copy()
        
        # Konversi waktu ke format yang bisa digunakan untuk ekstraksi fitur
        if 'waktu' in df_features.columns:
            df_features['waktu'] = pd.to_datetime(df_features['waktu'], errors='coerce')
            df_features['jam'] = df_features['waktu'].dt.hour
            df_features['hari'] = df_features['waktu'].dt.dayofweek # 0=Monday, 6=Sunday
            df_features['bulan'] = df_features['waktu'].dt.month
            df_features['kuartal'] = df_features['waktu'].dt.quarter
            
        # Encode asal_pendaftaran
        if 'asal_pendaftaran' in df_features.columns:
            if 'asal_pendaftaran' not in self.label_encoders:
                self.label_encoders['asal_pendaftaran'] = LabelEncoder()
                df_features['asal_pendaftaran_encoded'] = self.label_encoders['asal_pendaftaran'].fit_transform(df_features['asal_pendaftaran'].astype(str))
            else:
                # Handle unseen labels
                le = self.label_encoders['asal_pendaftaran']
                unique_vals = df_features['asal_pendaftaran'].astype(str)
                unique_vals = unique_vals.map(lambda x: x if x in le.classes_ else 'unknown')
                df_features['asal_pendaftaran_encoded'] = le.transform(unique_vals)
        else:
            df_features['asal_pendaftaran_encoded'] = 0  # Default value if column doesn't exist
            
        # Encode kode_poli jika tersedia
        if 'nm_poli' in df_features.columns:  # Menggunakan nm_poli sebagai pengganti kode_poli
            if 'nm_poli' not in self.label_encoders:
                self.label_encoders['nm_poli'] = LabelEncoder()
                df_features['nm_poli_encoded'] = self.label_encoders['nm_poli'].fit_transform(df_features['nm_poli'].astype(str))
            else:
                # Handle unseen labels
                le = self.label_encoders['nm_poli']
                unique_vals = df_features['nm_poli'].astype(str)
                unique_vals = unique_vals.map(lambda x: x if x in le.classes_ else 'unknown')
                df_features['nm_poli_encoded'] = le.transform(unique_vals)
        else:
            df_features['nm_poli_encoded'] = 0  # Default value if column doesn't exist
            
        # Buat label target (1 untuk gagal, 0 untuk berhasil)
        df_features['target'] = (df_features['status_kirim'] == 'Gagal').astype(int)
        
        # Pilih fitur yang akan digunakan untuk prediksi berdasarkan spesifikasi
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
        
        return X, y, available_features
        
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Melatih model-model untuk prediksi kegagalan pendaftaran"""
        if df.empty:
            return {}
            
        # Siapkan fitur
        X, y, feature_names = self.prepare_features(df)
        
        if X.empty or len(X) == 0:
            st.warning("Dataset tidak memiliki fitur yang cukup untuk pelatihan.")
            return {}
            
        # Cek apakah hanya ada satu kelas unik dalam y
        unique_classes = y.unique()
        if len(unique_classes) <= 1:
            # Cek apakah semua data memiliki status yang sama
            unique_statuses = df['status_kirim'].unique() if 'status_kirim' in df.columns else []
            if len(unique_statuses) == 1 and unique_statuses[0] == 'Sudah':
                st.warning(f"Dataset hanya memiliki satu kelas: {unique_classes}. Tidak bisa melatih model klasifikasi. Silakan gunakan data yang memiliki kegagalan dan keberhasilan pendaftaran.")
                # Kembalikan informasi dasar meskipun tidak bisa melatih model
                return {
                    'feature_names': feature_names,
                    'X_test': pd.DataFrame(),
                    'y_test': pd.Series(),
                    'X_train': pd.DataFrame(),
                    'y_train': pd.Series(),
                    'models': {},
                    'best_model_name': None,
                    'error': 'single_class_dataset'
                }
            else:
                # Jika hanya ada satu kelas dalam target (y) tapi bukan karena semua data 'Sudah',
                # mungkin perlu menangani kasus ini berbeda
                st.warning(f"Dataset hanya memiliki satu kelas dalam target: {unique_classes}. Tidak bisa melatih model klasifikasi. Silakan gunakan data yang memiliki kegagalan dan keberhasilan pendaftaran.")
                # Kembalikan informasi dasar meskipun tidak bisa melatih model
                return {
                    'feature_names': feature_names,
                    'X_test': pd.DataFrame(),
                    'y_test': pd.Series(),
                    'X_train': pd.DataFrame(),
                    'y_train': pd.Series(),
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
            'y_train': y_train
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
                else:  # SVM
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
        X, _, feature_names = self.prepare_features(df)
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

def load_data_from_database(start_date: str, end_date: str) -> pd.DataFrame:
    """Fungsi untuk memuat data dari database dengan fallback ke CSV jika koneksi gagal"""
    db_manager = BPJSQueryManager()
    
    # Coba muat data dari database
    df = db_manager.load_patient_data_with_fallback(start_date, end_date, fallback='auto')
    
    if df is not None and not df.empty:
        st.success(f"Data berhasil dimuat dari database: {len(df)} record")
        return df
    else:
        st.warning("Gagal memuat data dari database, mencoba fallback ke file CSV...")
        # Fallback ke file CSV yang disebutkan pengguna
        csv_path = "database/bpjs antrol.csv"
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                st.success(f"Data berhasil dimuat dari CSV: {len(df)} record")
                return df
            except Exception as e:
                st.error(f"Gagal membaca file CSV: {str(e)}")
        else:
            st.error(f"File CSV tidak ditemukan: {csv_path}")
    
    # Jika semua metode gagal, kembalikan data contoh
    st.info("Menggunakan data contoh karena koneksi database dan file CSV tidak tersedia...")
    return create_sample_data()

def create_sample_data() -> pd.DataFrame:
    """Fungsi untuk membuat data contoh jika file tidak ditemukan"""
    # Membuat data contoh yang sesuai dengan kebutuhan
    np.random.seed(42)
    n_samples = 1000  # Perbanyak data agar lebih representatif
    
    # Generate data contoh
    waktu_data = pd.date_range(start='2023-01-01', periods=n_samples, freq='H')
    df = pd.DataFrame({
        'waktu': waktu_data,
        'asal_pendaftaran': np.random.choice(['APM', 'Mobile JKN', 'Loket'], n_samples, p=[0.4, 0.5, 0.1]),
        'nm_poli': np.random.choice(['Umum', 'Gigi', 'KIA', 'Lansia', 'Mata'], n_samples, p=[0.3, 0.2, 0.2, 0.2, 0.1]),
        'status_kirim': np.random.choice(['Sudah', 'Gagal', 'Belum', 'Ambil Antrian'], n_samples, p=[0.70, 0.15, 0.10, 0.05])  # 70% berhasil, 15% gagal, 10% belum, 5% ambil antrian
    })
    
    # Konversi kolom waktu ke datetime jika belum
    df['waktu'] = pd.to_datetime(df['waktu'])
    
    # Ekstrak jam dari kolom waktu sebelum loop
    jam_data = df['waktu'].dt.hour.values
    
    # Buat pola agar model bisa belajar (gagal lebih sering pada jam-jam tertentu atau asal tertentu)
    # Gagal lebih sering di APM dan jam sibuk
    for i in range(len(df)):
        if df.loc[i, 'asal_pendaftaran'] == 'APM' and jam_data[i] in [7, 8, 9, 16, 17]:
            df.loc[i, 'status_kirim'] = np.random.choice(['Sudah', 'Gagal', 'Belum', 'Ambil Antrian'], p=[0.5, 0.35, 0.10, 0.05])  # 35% gagal
        elif df.loc[i, 'asal_pendaftaran'] == 'Mobile JKN':
            df.loc[i, 'status_kirim'] = np.random.choice(['Sudah', 'Gagal', 'Belum', 'Ambil Antrian'], p=[0.85, 0.05, 0.07, 0.03])  # 5% gagal
    
    return df

def main():
    """Fungsi utama untuk menampilkan analisis prediktif di Streamlit"""
    st.title("Predictive Analytics: Prediksi Kemungkinan Kegagalan Pendaftaran Pasien BPJS")
    st.write("""
    **Pertanyaan Bisnis:** Bisakah sistem memprediksi lebih awal apakah pendaftaran pasien BPJS akan gagal sebelum dikirim ke server BPJS?
    
    **Analisis yang Dilakukan:**
    - Data digunakan: histori log pendaftaran (fitur: jam, asal_pendaftaran, kode_poli, status_kirim, error_message).
    - Teknik: machine learning (model Random Forest / SVM).
    - Langkah: Label = status_kirim (berhasil/gagal), Training–testing 80:20, Evaluasi akurasi, precision, recall.
    """)
    
    # Sidebar untuk parameter
    st.sidebar.header("Parameter Analisis")
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    
    start_date = st.sidebar.date_input("Tanggal Mulai", value=yesterday)
    end_date = st.sidebar.date_input("Tanggal Akhir", value=today)
    
    # Konversi ke string
    start_date_str = str(start_date)
    end_date_str = str(end_date)
    
    # Pilihan sumber data
    data_source = st.sidebar.radio(
        "Sumber Data:",
        ("Database (dengan fallback CSV)", "Upload CSV File", "Data Contoh")
    )
    
    # Load data berdasarkan sumber yang dipilih
    df = None
    if data_source == "Database (dengan fallback CSV)":
        df = load_data_from_database(start_date_str, end_date_str)
    elif data_source == "Upload CSV File":
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"File CSV dimuat: {len(df)} record")
            except Exception as e:
                st.error(f"Error saat membaca file: {str(e)}")
        else:
            st.info("Silakan upload file CSV")
    else:  # Data Contoh
        df = create_sample_data()
        st.info(f"Data contoh dimuat: {len(df)} record")
    
    if df is not None and not df.empty:
        st.subheader("Pratinjau Data")
        st.dataframe(df.head(10))
        
        # Tampilkan statistik dasar
        st.subheader("Statistik Data")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Registrasi", len(df))
        col2.metric("Berhasil", len(df[df['status_kirim'] == 'Sudah Dikirim']))
        col3.metric("Gagal", len(df[df['status_kirim'] != 'Sudah Dikirim']))
        
        # Tombol untuk melatih model
        if st.button("Latih Model Prediksi"):
            with st.spinner("Melatih model prediksi..."):
                analyzer = BPJSPredictiveAnalyzer()
                training_results = analyzer.train_models(df)
                
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
                        importance_df = analyzer.get_feature_importance(training_results['feature_names'])
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
                    
                    # Simpan model analyzer ke session state untuk digunakan nanti
                    st.session_state.analyzer = analyzer
                    st.session_state.training_results = training_results
                    
                    # Insight yang diperoleh
                    st.subheader("Insight yang Diperoleh")
                    best_model_name = training_results['best_model_name']
                    best_model_info = models[best_model_name]
                    accuracy = best_model_info['accuracy']
                    st.write(f"• Model {best_model_name.upper()} mampu memprediksi kegagalan pendaftaran dengan akurasi {accuracy:.1%}.")
                    
                    if training_results['best_model_name'] == 'random_forest':
                        importance_df = analyzer.get_feature_importance(training_results['feature_names'])
                        if not importance_df.empty:
                            top_factor = importance_df.iloc[0]['fitur']
                            st.write(f"• Faktor paling berpengaruh terhadap kegagalan adalah {top_factor}.")
                    
                elif 'error' in training_results and training_results['error'] == 'single_class_dataset':
                    # Kasus khusus: dataset hanya memiliki satu kelas
                    st.warning("Dataset hanya memiliki satu kelas. Tidak bisa melatih model klasifikasi.")
                    st.info("Silakan gunakan dataset yang memiliki kombinasi kegagalan dan keberhasilan pendaftaran untuk melatih model prediktif.")
                else:
                    st.error("Gagal melatih model. Pastikan data memiliki kolom yang diperlukan.")
    
        # Bagian untuk prediksi data baru jika model sudah dilatih
        if 'analyzer' in st.session_state and 'training_results' in st.session_state:
            st.subheader("Prediksi untuk Data Baru")
            st.write("Model akan membuat prediksi berdasarkan data yang dimuat.")
            
            if st.button("Lakukan Prediksi"):
                with st.spinner("Melakukan prediksi..."):
                    analyzer = st.session_state.analyzer
                    predicted_df = analyzer.predict_failure_risk(df)
                    
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
