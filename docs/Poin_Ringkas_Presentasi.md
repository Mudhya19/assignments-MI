# 📊 POIN-POIN PRESENTASI - RINGKAS & SIAP PRESENTASI
## Unsupervised Clustering of Longitudinal Clinical Measurements in EHR

---

## 🎯 OPENING STATEMENT (30 detik)

> "Assalamualaikum Pak/Bu. Nama saya [nama]. Hari ini saya akan membahas penelitian dari Cleveland Clinic tentang **bagaimana machine learning bisa menganalisis data pasien dari waktu ke waktu untuk memprediksi risiko kesehatan**."

---

---

# SLIDE 1: TITLE SLIDE (10 detik)

## Poin Utama:
- **Paper terbaru** Oktober 2024 dari Cleveland Clinic (institusi top)
- Publikasi di **PLOS Digital Health** (journal berkualitas tinggi)
- Tentang: **Clustering unsupervised untuk data longitudinal pasien**

---

---

# SLIDE 2: PROBLEM STATEMENT (40 detik)

## Opportunity (Peluang)
- ✅ Rumah sakit punya data pasien selama bertahun-tahun (Electronic Health Records)
- ✅ Ada algoritma signal processing yang bisa dipelajari untuk analyze data medis

## Challenge (Tantangan)
1. **Pasien datang tidak teratur** → Data tidak rapi/konsisten
2. **Data sering hilang** → Tidak semua pasien punya lengkap (common di real world)
3. **Tidak tahu algoritma mana yang terbaik** → Belum ada panduan sistematis

## Critical Gap
> **Masalah: Belum pernah ada yang secara sistematis bandingkan 30 algoritma untuk clinical data dengan ground truth yang diketahui**

---

---

# SLIDE 3: RESEARCH OBJECTIVES (45 detik)

## Tujuan 1: Evaluasi Algoritma (Simulasi)
- Test 30 algoritma berbeda
- Pada 6,912 dataset simulasi dengan **ground truth diketahui**
- Lihat mana yang perform paling baik

## Tujuan 2: Real-World Application (Validasi)
- Ambil algoritma terbaik dari simulasi
- Test pada **43,426 anak nyata** dengan obesity
- Lihat **apakah bisa predict metabolic syndrome**

## Kenapa Simulasi?
✅ **Known ground truth** = tahu jawaban yang benar dengan pasti  
✅ **Kontrol parameter** = test berbagai kondisi (data lengkap vs banyak missing)

---

---

# SLIDE 4: DATASET PREPARATION (45 detik)

## 3 Tipe Pengukuran Klinis:
1. **BMI** (Body Mass Index) - ukuran obesity
2. **SBP** (Systolic Blood Pressure) - tekanan darah
3. **Random Glucose** - gula darah

## Simulated Data:
- Start: **6 real trajectories** per measurement (18 total)
- Manipulate: effect size, dispersion, missing data, number of clusters
- **Total: 6,912 simulated datasets**

## Real Cohort:
- **N = 43,426 anak** (umur 2-18 tahun)
- Follow-up rata-rata: **8.47 tahun**
- **1,474 dengan MetS** (3.4%)

---

---

# SLIDE 5: 30 ALGORITHMS (60 detik) ⭐ PENTING DIJELASKAN

## Gimana Ada 30 Algoritma?
**2 × 8 × 6 = 30** (kombinasi dari 3 komponen)

### Component 1: Assignment Method (2 pilihan)
- **Partitional** = Hard (patient 100% to 1 cluster)
- **Fuzzy** = Soft (patient bisa 60% cluster A, 40% cluster B)

### Component 2: Distance Measure (8 pilihan)
**Temporal Matching (untuk time-series):**
- DTW, DTW-LB, LB-Improved, LB-Keogh
  → Tahu pola temporal, bisa flexible

**Simple Metrics:**
- Euclidean, Manhattan, Soft-DTW, SBD
  → Basic, tapi mungkin tidak cocok untuk time-series

### Component 3: Centroid Computation (6 pilihan)
- PAM (Partitioning Around Medoids) - general purpose
- DBA (DTW Barycenter Averaging) - specially designed for DTW
- Others...

## Why Ini Elegant?
**Bukan 30 completely different, tapi kombinasi sistematis → dapat test mana component terbaik!**

---

---

# SLIDE 6: EVALUATION METRICS (45 detik)

## Adjusted Rand Index (ARI)
- **Ukur**: Seberapa baik clustering match dengan truth?
- **Range**: -1 sampai +1
  - **1.0** = Perfect (100% benar)
  - **0.70** = Good ✅ (Acceptable untuk clinical use)
  - **0.50-0.70** = Moderate ⚠️
  - **<0.30** = Poor ✗ (Jangan pakai)
  - **0** = Random (sepertilemparan koin)

## Statistical Testing
- **Nemenyi Test**: Bandingkan 30 algoritma secara statistik
- **FDR Correction**: Hindari false positives saat multiple comparisons

## Real Data Validation
- **Consensus >70%**: Run algoritma 5× dengan random seeds berbeda
- Jika konsisten → cluster stabil & trustworthy

---

---

# SLIDE 7: KEY RESULTS - ALGORITHM PERFORMANCE (60 detik)

## TOP 3 WINNERS 🏆

| Rank | Algorithm | Score | Notes |
|------|-----------|-------|-------|
| 🥇 1st | DTW-LB + PAM | Rank 4.19 | Fast & Accurate |
| 🥈 2nd | LB-Improved + PAM | Rank 4.19 | Even Faster |
| 🥉 3rd | DTW + PAM | Rank 5.53 | Best Accuracy |

**Median ARI: 0.70** (Good!)

## 3 KEY FINDINGS

### Finding 1: Partitional >> Fuzzy
- Semua top 3 pake Partitional (hard assignment)
- Fuzzy algorithms ranked jauh lebih rendah
- **Conclusion**: Untuk clinical data, gunakan **hard assignment** ✅

### Finding 2: SURPRISE - PAM > DBA!
- DBA designed khusus untuk DTW (should be optimal)
- **TAPI** PAM (general-purpose) **lebih bagus!**
- **Why**: Clinical data messy, PAM lebih robust
- **Lesson**: Jangan assume specialized = better! ✅

### Finding 3: DTW Family Dominates
- DTW variants occupy top 10 positions
- Simple metrics (Euclidean) ranked 18-30 (worst)
- **Conclusion**: Temporal-aware metrics ESSENTIAL untuk time-series! ✅

---

---

# SLIDE 8: CRITICAL FINDING - MAGNITUDE VS SHAPE (90 detik) 🔴 PALING PENTING!

## MAGNITUDE-BASED CLUSTERING ✅ ROBUST

**What**: Cluster based on peak values (high vs low BMI)

**Performance across missingness:**
```
0% missing  → ARI 0.70
10% missing → ARI 0.70 (stable!)
25% missing → ARI 0.68 (stable!)
50% missing → ARI 0.67 (stable!)
```

**Why robust?** Peak values visible bahkan dengan gaps

---

## SHAPE-BASED CLUSTERING ❌ VULNERABLE

**What**: Cluster based on trajectory trend (rising vs stable)

**Performance across missingness:**
```
0% missing  → ARI 0.60
10% missing → ARI 0.35 (DROP 40%! 😱)
25% missing → ARI 0.15 (COLLAPSE!)
50% missing → ARI 0 (FAIL!)
```

**Why vulnerable?** Trajectory pattern perlu complete sequence untuk terlihat

---

## PRACTICAL IMPLICATION ⚡

> **REAL EHR punya >10% missing data (umum!)**
> 
> **JADI:**
> - ✅ **GUNAKAN: Magnitude features** (peak values, baseline)
> - ❌ **JANGAN: Shape features** (trajectory trends)
> 
> **Otherwise:** Algorithm akan gagal!

---

---

# SLIDE 9: REAL-WORLD APPLICATION (45 detik)

## Algorithm Dipilih
**Partitional + DTW + PAM**

**Why?**
- Top 3 overall performance
- Robust untuk variable trajectory lengths (pasien follow-up beda lama)
- Proven dalam simulation

## Optimal Clusters
**k = 5 identified**

**Quality Assessment:**
- C1, C2, C3: Consensus ≥ 70% ✅ (stable, trust)
- C4, C5: Consensus < 70% ⚠️ (less stable, tapi included)

## Cohort Details
- **N = 43,426** anak (umur 2-18)
- **55.7% male**, diverse race/ethnicity
- **Mean follow-up 8.47 tahun** (cukup panjang)
- **3.4% MetS cases** (1,474 anak)

---

---

# SLIDE 10: BMI TRAJECTORY CLUSTERS (90 detik) 🎯 CORE FINDINGS

## 5 CLUSTERS dengan DIFFERENT RISK

| Cluster | Pattern | N | MetS OR | Action |
|---------|---------|---|---------|--------|
| **C5** | Stable Low | 6,665 | 1.0 | ✅ Maintain |
| **C4** | Dysregulated | 10,632 | 1.35 | ⚠️ Investigate |
| **C1** | Rising (Mild) | 7,558 | 2.44 | 🔴 Intervene |
| **C2** | Rising (Moderate) | 7,619 | 2.60 | 🔴 Urgent |
| **C3** | Consistently High | 10,952 | **4.87** | 🚨 CRITICAL |

---

## JELASKAN SETIAP CLUSTER

### **C5: Stable Low (REFERENCE/PROTECTIVE)**
- BMI konsisten normal (25-50th percentile)
- Flat pattern sepanjang childhood
- **Risk**: Lowest → MetS OR = 1.0
- **Action**: Maintain lifestyle, annual check-ups

### **C4: Dysregulated (WARNING SIGN)**
- BMI jumping up-down (variable pattern)
- Highest variance = unstable
- **Risk**: Mild → MetS OR = 1.35
- **Action**: Investigate cause (thyroid? stress? medication?)

### **C1: Rising Mild (EARLY INTERVENTION)**
- BMI gradually increasing over childhood
- Starting from lower/normal percentiles
- **Risk**: Moderate → MetS OR = 2.44
- **Action**: Dietitian, lifestyle intervention (still reversible!)

### **C2: Rising Moderate (URGENT)**
- Similar to C1 tapi starting higher + steeper slope
- Worsening faster
- **Risk**: Moderate-High → MetS OR = 2.60
- **Action**: More intensive intervention, frequent follow-up

### **C3: Consistently High (CRITICAL) 🚨**
- **Elevated BMI THROUGHOUT childhood** (age 2-18)
- Tidak improvement sepanjang waktu
- **Risk**: HIGHEST → MetS OR = **4.87** (5× lebih tinggi!)
- **Action**: URGENT multidisciplinary care (specialist, dietitian, psych)

---

## NOVEL INSIGHT 💡

> **Same BMI value at age 12 tapi berbeda trajectory = BERBEDA RISK!**
> 
> **Contoh:**
> - Child A: 40th%ile → 95th%ile (rising pattern) → OR 2.44-2.60
> - Child B: 95th%ile → 95th%ile (stable pattern) → OR 4.87
> 
> **Lesson: Trajectory MATTERS lebih dari absolute value!**

---

---

# SLIDE 11: CLINICAL IMPLICATIONS (90 detik)

## KEY INSIGHT: Longitudinal > Static Measurements

```
TRADITIONAL:
"Apa BMI hari ini?" → Single snapshot

NEW:
"Gimana BMI berubah sepanjang waktu?" → Dynamic trajectory
```

---

## 5-STEP CLINICAL WORKFLOW

### Step 1: Identify Trajectory
- Pull BMI measurements dari EHR (min 3-5 measurements)
- Plot BMI vs Age
- Classify: rising? stable? variable?
- Apply algorithm → Get cluster label

### Step 2: Risk-Stratify
- Assign cluster (C1-C5)
- Know MetS odds ratio
- Prioritize resources

### Step 3: Allocate Interventions
- **C5** → Maintenance (annual visit)
- **C4** → Diagnostic workup
- **C1-C2** → Lifestyle intervention (dietitian, exercise)
- **C3** → Intensive multidisciplinary (specialist, mental health)

### Step 4: Monitor Transitions
- Reassess cluster setiap 6-12 bulan
- Track: Is trajectory improving?
- **Good**: C3→C2→C1→C5
- **Bad**: C5→C4 or C1→C3

### Step 5: Measure Outcomes
- **C5**: Stay in C5?
- **C1-C2**: Slope decreasing? Moving to lower cluster?
- **C3**: Weight stabilized? MetS prevented?

---

## ENABLES PRECISION MEDICINE

✅ **Different phenotypes → Different interventions**
✅ **Right patient → Right intervention → Right timing**
✅ **Optimize outcomes per subgroup**

---

---

# SLIDE 12: LIMITATIONS (60 detik)

## 4 Key Limitations (Transparently Disclosed)

1. **Limited trajectory diversity**
   - Only 6 real trajectories per measurement
   - May not capture all trajectory types
   - **Mitigation**: Future study expand to 20-30

2. **Simple imputation method**
   - Used only mean imputation (basic method)
   - Better methods: MICE, KNN
   - **Mitigation**: Test with advanced imputation future

3. **Selection bias in cohort**
   - Cleveland Clinic = urban, insured, regular care
   - May not generalize to rural/low-income
   - **Mitigation**: Replicate in other health systems

4. **MetS definition ambiguous**
   - No universal consensus for pediatric MetS
   - Different definitions give different results
   - **Mitigation**: Validate with other definitions

**BUT: These limitations DON'T negate main findings!**

---

## 2 KEY TAKEAWAYS

### Takeaway 1: Systematic Algorithm Evaluation is CRITICAL
- **Before**: Clinicians didn't know which algorithm to choose
- **After**: Evidence-based guidance with rankings
- **Future**: Any EHR clustering should be systematic & tested

### Takeaway 2: Longitudinal Patterns > Single Measurements
- **Traditional**: "What's the BMI today?"
- **New**: "How has BMI changed over time?"
- **Impact**: Better prediction, precision medicine

---

---

# SLIDE 13: CONCLUSION (2 menit - allow discussion)

## SUMMARY OF KEY FINDINGS

### Finding 1: DTW-Based is Optimal
```
✅ Use: DTW, DTW-LB, LB-Improved
❌ Avoid: Euclidean, Manhattan
```

### Finding 2: Magnitude Robust, Shape Vulnerable
```
✅ Use: Peak BMI values (robust)
❌ Avoid: Trajectory trends (vulnerable dengan missing data)
```

### Finding 3: 5 Clusters with Different Risk
```
OR range 1.0 to 4.87
→ Enables risk stratification
→ Guides intervention intensity
```

### Finding 4: Trajectory > Single Measurements
```
Same BMI value, different outcome depending on pattern
→ Paradigm shift to dynamic assessment
→ Enables early intervention for rising trends
```

---

## CLINICAL SIGNIFICANCE

🎯 **Enables precision medicine**: Different trajectories → different interventions

🎯 **C3 recognition**: OR 4.87 = CRITICAL, needs urgent multidisciplinary care

🎯 **Practical guidance**: For EHR with missing data, use magnitude not shape

---

## CONTRIBUTION TO SCIENCE

✅ **First systematic evaluation** of 30 algorithms on clinical EHR data

✅ **Rigorous two-phase design** (simulation + real-world validation)

✅ **Evidence-based guidance** for algorithm selection

✅ **Reproducible methodology** (code & data available)

---

## FUTURE DIRECTIONS

- Advanced imputation methods (MICE, KNN)
- Hierarchical clustering evaluation
- Broader measurement types (beyond BMI)
- Clinical integration studies (EHR implementation)

---

## FINAL MESSAGE 🎯

> "**Trajectory-based clustering > static measurements untuk clinical phenotyping.**
> 
> **This research shows bahwa machine learning bisa discover clinically meaningful patient subgroups dari EHR data, enabling precision medicine dengan personalized interventions untuk setiap phenotype.**
> 
> **As EHRs accumulate more longitudinal data, pendekatan seperti ini akan unlock actionable clinical insights dan enable truly personalized healthcare.**"

---

---

# 📋 QUICK CHECKLIST SEBELUM PRESENTASI

## Preparation:
- [ ] Practice opening statement (30 detik)
- [ ] Hafalkan 3 TOP findings (Slide 7)
- [ ] HAFAL Slide 8 (Magnitude vs Shape) - ini MOST IMPORTANT
- [ ] Pahami 5 clusters (Slide 10) - bisa jelasin contohnya
- [ ] Siapkan 5-step workflow (Slide 11)
- [ ] Ready untuk Q&A tentang clinical applications

## During Presentation:
- ✅ Speak clearly, jangan terburu-buru
- ✅ Highlight poin merah (CRITICAL findings)
- ✅ Give concrete examples (2 children dengan same BMI tapi berbeda risk)
- ✅ Emphasize clinical relevance (bukan hanya academic)
- ✅ Allow time untuk Slide 8 (magnitude vs shape) - MOST COMPLEX

## Key Phrases to Use:
- "**First systematic evaluation**..."
- "**This is the biggest discovery**..." (untuk Slide 8)
- "**Magnitude is robust, shape is vulnerable**..."
- "**Different trajectories need different interventions**..."
- "**Enables precision medicine**..."

---

**TOTAL PRESENTATION TIME: ~10-12 minutes**

**Semoga presentasi Anda sukses! Anda sudah siap dengan poin-poin yang ringkas dan mudah dipahami. 🚀**

