# 📊 CATATAN PRESENTASI: Peran Teks dalam Dashboard Interaktif

## From Instruction to Insight: Exploring the Functional and Semantic Roles of Text

**Paper:** Sultanum & Setlur (IEEE TVCG, 2024)  
**Topik:** Soal 4 - Penerapan Praktis & Peluang Pengembangan Lanjutan  
**Durasi Presentasi:** ~15-20 menit (5 slide)

---

## 🎯 RINGKASAN 1 HALAMAN (Baca Dulu!)

Paper ini menjawab pertanyaan fundamental: **"bagaimana pendekatan dan temuan dari studi ini dapat diterapkan atau dikembangkan lebih lanjut—baik dalam konteks desain dashboard di sektor tertentu (misal: pendidikan, kesehatan, bisnis), maupun dalam penelitian lanjutan?"**

Melalui analisis 190 dashboards + 13 expert interviews, authors menemukan:

1. **9 jenis komponen teks** dengan peran fungsional berbeda
2. **4 level semantic** (elemental → contextual) yang membentuk insight value
3. **Dashboard genre menentukan strategi** — narrative dashboards gunakan banyak takeaways (LV3-LV4), exploratory dashboards fokus pada data exploration (LV1-LV2) tanpa "prescribed analytics"
4. **12 heuristics practical** untuk design text yang efektif

**Signifikance:** Text bukan sekadar "deskripsi"—ia structural enabler untuk narrative, explanation, dan insight discovery dalam environment kompleks dashboards.

---

## 📝 SLIDE 1: JUDUL (30 detik)

**Yang Dibaca:**

- Judul paper
- Subtitle: "From Instruction to Insight..."
- Authors & conference
- Konteks: "Analisis Paper untuk Presentasi Kelas"

**Notes untuk Anda:**

- Buat eye contact dengan audience
- Jangan buru-buru—biarkan audience baca judul
- Optional: Deskripsi singkat konteks (ini paper terbaru dari IEEE TVCG 2024)

---

## 📝 SLIDE 2: MOTIVASI & KONTRIBUSI UTAMA (3-4 menit)

### STRUKTUR SLIDE:

**Bagian A: Motivasi Penelitian (bacakan dengan emfasis)**

Dosen mau tahu: _"Mengapa studi ini penting?"_

**Yang Anda Jelaskan:**

> "Kalau kita lihat dashboard publik di internet, ternyata 55% sudah mengandung blok teks yang significant. Namun, ketika saya baca literature, penelitian tentang peran teks dalam dashboard hampir tidak ada—mayoritas fokus pada single-chart annotations saja, bukan dashboard-wide integration.

> Tools dashboard automation saat ini juga fokus pada automating charts dan layout, tapi kurang perhatian pada text generation dan placement. Nah, sekarang dengan emerging LLMs, kita punya opportunity untuk automate text content. Tapi tanpa pemahaman fundamental tentang bagaimana teks _seharusnya_ digunakan, kita tidak bisa design guardrails yang meaningful untuk LLM-generated content. Jadi, timing-nya perfect untuk research ini."

**Poin Kunci Yang Disampaikan:**

- Gap antara prevalensi text di dashboards vs penelitian about text
- Tools fokus pada visual automation, bukan text
- LLM membuka peluang + ancaman (perlu framework)

---

**Bagian B: Kontribusi Utama (bacakan clara)**

Dosen mau tahu: _"Apa kontribusi paper ini?"_

**Yang Anda Jelaskan:**

> "Paper ini punya 3 main contributions:

> **Pertama,** authors melakukan empirical characterization dari current practices. Mereka analyze 190 dashboards dan temukan 9 jenis text components—mulai dari title, subheading, chart annotation, sampai tooltips. Setiap component punya peran fungsional yang berbeda. Plus, mereka adapt semantic framework dari Lundgard & Satyanarayan untuk capture content depth—dari LV1 (elemental descriptions) sampai LV4 (contextual insights). Ini penting karena menunjukkan bahwa teks dalam dashboard ada hierarchy—bukan semua teks setara.

> **Kedua,** mereka propose 12 heuristics untuk recommended practices. Ini bukan fancy theory—ini practical guidance untuk designers. Heuristics ini dikelompokkan dalam 4 categories: Analytical Support, Semantics, Presentation, dan Navigation. Setiap heuristic validated oleh 13 expert dashboard creators dengan 10+ tahun experience.

> **Ketiga,** mereka identify research opportunities untuk future work—mulai dari dashboard linters, automatic explanation generation, intelligent text-chart linking, sampe personalization based on user role."

**Poin Kunci Yang Disampaikan:**

- 9 text components identified (functional categorization)
- 4 semantic levels (content depth)
- 12 practical heuristics
- Foundation untuk future research & tool design

**VISUAL AID:** Jika audience perlu visualisasi, Anda bisa reference:

- 9 components: Title, Subheading, Section Header, Chart Title, Interaction Guidance, Metadata, Content Block, Text-Data Summaries, Chart Annotation, Tooltip, Data Table
- 4 semantic levels: LV1 (elemental), LV2 (statistical), LV3 (perceptual), LV4 (contextual)

---

## 📝 SLIDE 3: TEMUAN PENTING & HUBUNGAN TEKS-PENGGUNA (3-4 menit)

### STRUKTUR SLIDE:

**Bagian A: Komponen Teks (bacakan dengan organized)**

Dosen mau tahu: _"Apa saja komponen teks yang ditemukan?"_

**Yang Anda Jelaskan:**

> "Jadi, findings menunjukkan bahwa ada 9-11 komponen teks yang commonly digunakan dalam dashboards. Itu bukan just 'text blocks'—ada nuansa functional yang penting.

> Misalnya, **Title** adalah yang paling umum (92% dashboards), dan itu bukan hanya label—title set the overarching theme dan guide initial interpretation.

> **Metadata** ada di 76% dashboards, dan ini critical untuk trust—berisi info tentang data source, author, kapan last updated, disclaimers.

> **Content Blocks**—ini adalah sentence atau multiline text yang provide narrative & context. Ada di 67% dashboards.

> Terus ada **Text-Data Summaries** atau 'BANs' (Big-Ass Numbers)—itu KPI boxes yang show key metrics. Ada di 58% dashboards.

> Sama pentingnya, ada **Chart Annotations**—text callouts overlaid pada charts untuk highlight specific data points atau trends. Ini ada di 19% dashboards—tidak sebanyak yang lain, tapi very impactful ketika digunakan.

> Dan semua dashboard modern punya **Tooltips**—text yang muncul ketika hover. 42% dari mereka customize tooltip mereka beyond default values, karena itu opportunity untuk provide richer information."

**Poin Kunci:**

- 9-11 komponen dengan roles berbeda
- Ada hierarchy—bukan semua teks sama importance
- Text-data summaries & annotations adalah high-impact elements

---

**Bagian B: Semantic Levels (bacakan dengan clear examples)**

Dosen mau tahu: _"Apa bedanya text di berbagai dashboards?"_

**Yang Anda Jelaskan:**

> "Beyond functional categorization, ada juga semantic depth yang different. Authors adapt framework yang disebut LV1-LV4:

> **LV1 - Elemental Properties** (97% dashboards): Ini basic descriptions. Contohnya, chart title yang bilang 'Gender & Population Graph'—itu LV1. Anda describe APA yang visible, bukan interpret APA meaning-nya.

> **LV2 - Statistical Concepts** (74% dashboards): Ini mention specific data facts—outliers, comparisons, descriptive statistics. Misalnya, 'Total Population: 17 Million'—itu LV2. Sudah agak deeper dari LV1, tapi masih factual.

> **LV3 - Perceptual & Cognitive Phenomena** (27% dashboards): Ini interpret patterns. Contohnya, 'Population distribution shifted from urban centers to suburban areas'—itu observation yang require synthesis dari multiple data points. Only 27% dashboards punya ini, jadi quite selective.

> **LV4 - Contextual & Domain-Specific Insights** (50% dashboards): Ini provide external context. Misalnya, 'This shift is driven by rising urban housing costs and remote work adoption'—itu connect data ke real-world factors. Jadi users tidak just see pattern, tapi understand WHY.

> Key insight: Hierarchy visual dari text (title → subheading → chart title) mirrors semantic hierarchy (dari LV4 insights down to LV1 elemental). Ini bukan design accident—ini functional untuk guide user cognitive processing."

**Poin Kunci:**

- 4 semantic levels (LV1-LV4)
- Visual structure mirrors semantic depth
- Different levels serve different understanding purposes

---

**Bagian C: Insight Hubungan Teks-Perilaku Pengguna (bacakan dengan emphasis)**

Dosen mau tahu: _"Gimana teks mempengaruhi how users interact dengan dashboards?"_

**Yang Anda Jelaskan:**

> "Okay, ini finding yang paling important. Authors discover bahwa **dashboard genre adalah strong signal untuk discriminating text use**. Meaning: type dashboard menentukan strategy text yang optimal.

> **Untuk Narrative Dashboards** (infographics, designed untuk storytelling):
>
> - Heavy usage of LV3-LV4 content (57% & 76% vs 14% & 33% di analytical dashboards)
> - More content blocks (91% vs 53%) dan chart annotations (29% vs 14%)
> - Reason: Audience adalah general public, casual use—mereka expect dashboards guide them ke insights. Jadi authors explicitly make takeaways clear.

> **Untuk Exploratory/Analytical Dashboards** (untuk expert users, decision-making):
>
> - Focus pada LV1-LV2 content
> - Avoid 'prescribed analytics'—one expert bahkan bilang: 'The last thing I want to do is feed conclusions to the user'
> - Strategy: Provide context & definitions (metadata, interaction guidance), tapi let users draw own conclusions
> - Reason: Expert users ingin explore sendiri, buat own interpretations

> **Tentang Dynamic Text:** 49% dashboards gunakan dynamic text—meaning, text update berdasarkan user interactions. Ini critical untuk maintaining context saat users explore. Misalnya, breadcrumb yang bilang 'Currently viewing: Sales by Region > East Region > Q3 2024'.

> **Tentang Formatting:** Semua experts yang interviewed (7 dari 13) intentional tentang text formatting—font sizes untuk hierarchy, bold untuk emphasis, colors untuk legend. Ini bukan decorative—itu _functional_ untuk guiding attention dan supporting reading order."

**Poin Kunci:**

- Dashboard genre determines text strategy (narrative vs exploratory)
- Explicit vs implicit takeaways depend on audience & use case
- Dynamic text & formatting are functional, not decorative

---

## 📝 SLIDE 4: PENERAPAN PRAKTIS & PELUANG PENELITIAN (4-5 menit)

### STRUKTUR SLIDE:

**Bagian A: Penerapan di Sektor (bacakan dengan real-world examples)**

Dosen mau tahu: _"Gimana ini applied dalam praktik nyata?"_

**Yang Anda Jelaskan:**

> "Jadi findings ini applicable di banyak sektor. Let me give konkret examples:

> **SEKTOR PENDIDIKAN (Learning Analytics Dashboards):**
>
> Bayangkan dashboard untuk tracking student performance. Untuk student users, Anda ingin tinggi LV3-LV4 content—explain WHY certain metrics matter, give contextual guidance.
>
> Misalnya, alih-alih hanya show 'Your GPA: 3.2', Anda provide context: 'Your GPA is 3.2, which is above departmental median of 3.0. However, for graduate program admission, typically 3.5+ preferred. Consider reviewing materials in Chapter 5 where score dropped.'
>
> Untuk educators/researchers accessing same dashboard, mereka butuh exploratory interface—raw data, statistical comparisons—tapi with contextual annotations tentang pedagogical theories, curriculum alignment, etc.
>
> Impact: Better data literacy untuk students, more actionable insights untuk educators.

> **SEKTOR KESEHATAN (Clinical Dashboards):**
>
> Ini more critical because stakes are high. Text tidak just for explanation—it's for safety.
>
> Metadata menjadi paramount: 'This data is real-time for ICU, 6-hour lag for ward data, 24-hour lag for retrospective data.' Jangan assume users know timing.
>
> LV4 contextual information essential: Connect metrics ke clinical protocols. Misalnya, kalau ada alert tentang temperature, dashboards harus explain: 'Patient temperature >38.5°C triggers fever protocol—see Clinical Protocol A.'
>
> Interaction guidance juga penting: 'Click bell icon to escalate alert', 'Red thresholds indicate critical values per ACLS guidelines'.
>
> Impact: Fewer errors from misinterpretation, better compliance, safer patient care.

> **SEKTOR BISNIS (Executive Dashboards):**
>
> Text pakai dynamic updates—'Revenue $2.5M, up 15% month-over-month, down 3% year-over-year. Driven by seasonal Q1 weakness in Asia-Pacific region.'
>
> Breadcrumb trails critical untuk reproducibility: 'Currently viewing: North America > Enterprise Segment > Product A > Q4 Results'. Ini penting kalau exec mau share findings dengan colleagues.
>
> Predefined narrative blocks highlight action items: 'Q4 showed unexpected surge in churn rate (8% vs 4% historical average). Recommend accelerated customer success outreach.'
>
> Impact: Faster decision-making, better cross-functional alignment, actionable insights."

**Poin Kunci:**

- Setiap sektor punya text needs berbeda
- Balance antara exploratory & narrative depends on audience
- Dynamic text & breadcrumbs adalah critical untuk tracking user context

---

**Bagian B: Peluang Penelitian Lanjutan (bacakan dengan enthusiasm!)**

Dosen mau tahu: _"Apa research opportunities yang terbuka?"_

**Yang Anda Jelaskan:**

> "Authors identify 4 main research directions yang exciting:

> **OPPORTUNITY 1: Dashboard Linters**
>
> Concept: Automated tools yang provide real-time feedback saat Anda author dashboards—similar to software linters (ESLint).
>
> Implementasi:
>
> - Check heuristic compliance otomatis. Misalnya, detect kalau metadata missing (author, data source), atau kalau content blocks terlalu panjang.
> - Semantic analysis: Identify mismatches antara textual emphasis dan visual emphasis. Misalnya, kalau text bilang 'Sales tripled' tapi data hanya +20%, itu mismatch.
> - Contextual recommendations: If dashboard is exploratory, warn tentang overly prescriptive language.
>
> Challenge: Balancing automation dengan designer intent. Jangan buat tools yang too restrictive.

> **OPPORTUNITY 2: Automatic Explanation Generation**
>
> Leverage NLP/NLG untuk auto-generate contextual insights dari data patterns.
>
> Applications:
>
> - Auto-generate chart captions describing trends
> - Auto-populate tooltips dengan relevant context dari knowledge bases
> - Generate metadata automatically dari data catalogs
> - Personalize explanations based on user role
>
> Challenge: Ensuring accuracy & avoiding biases dalam generated explanations. Plus, maintaining authenticity—jangan buat semua explanations terasa machine-generated.

> **OPPORTUNITY 3: Intelligent Text-Chart Linking**
>
> Build infrastructure untuk automatic linking antara text references dan visual elements.
>
> Features:
>
> - Semantic linking: NLP-based. 'Revenue peaked in Q3' → automatically link ke chart showing revenue spike
> - Dynamic highlighting: Hover on text → highlight relevant chart area
> - Interactive stories: Create narratives dengan synchronized text + visual exploration
>
> Current tools yang ada: FacetNotes (integrate text dengan data points), Kori (identify text-chart links), VizFlow (generate data-driven articles).
>
> Future: Multi-modal analysis, complex narratives, version control untuk linked elements.

> **OPPORTUNITY 4: Personalized & Dynamic Text**
>
> Adapt text content & semantic level based on user characteristics.
>
> Dimensions:
>
> - User role (Executive → lower detail, Analyst → higher detail)
> - Prior knowledge (Novice → more context, Expert → less explanation)
> - Current task (Exploring vs reporting vs presenting → different text strategies)
> - Interaction patterns (infer interests dari what user clicks, adapt text dynamically)
>
> Implementation: Rule-based (explicit rules mapping user to text strategy) atau learning-based (predict optimal config from behavior).
>
> Challenge: Privacy concerns, maintaining consistency across personalized views, measuring effectiveness."

**Poin Kunci:**

- 4 research opportunities yang practically viable
- Kombinasi NLP + visualization design required
- Challenges ada, tapi solvable dengan right approach

---

## 📝 SLIDE 5: KESIMPULAN (2-3 menit)

### STRUKTUR SLIDE:

**Yang Anda Jelaskan:**

> "Okay, jadi sebagai wrap-up:

> **KEY POSITIONING:** Paper ini reframe bagaimana kita think tentang text dalam dashboards. Bukan text = decorative accompaniment ke visuals. Sebaliknya, text = foundational enabler untuk narrative construction, explanation, insight discovery, sama navigation.

> Kalau visualization adalah 'what' (apa yang terjadi di data), text adalah 'why' dan 'so what' (kenapa itu penting, what should I do about it).

> **KONTRIBUSI METODOLOGI:** Paper memberikan empirical framework untuk characterizing text use—functional categorization + semantic levels. Plus 12 actionable heuristics. Ini bukan just descriptive—framework ini actionable untuk tool builders dan designers.

> **IMPLIKASI:**
>
> - Untuk **practitioners:** Anda sekarang punya formal framework, bukan just intuition, untuk making text decisions.
> - Untuk **tool builders:** Ini opportunities untuk developing text-specific authoring features.
> - Untuk **researchers:** Rich research agenda terbuka—linting, NLG, linking, personalization.
> - Untuk **educators:** Penting untuk teach bahwa visualization design = more than just charts. Text is integral.

> **BOTTOM LINE:** Effective dashboard communication requires mastery of both visuals AND text. They're complementary, not competing. Dan sekarang Anda punya framework untuk approaching it systematically.

> Mungkin ada quote yang bagus: 'A picture is worth a thousand words, but a word can paint a thousand pictures.' That's the essence."

---

## 🎤 TIPS PRESENTASI

### Before You Present:

- [ ] **Practice timing:** 5 slide untuk 15-20 menit. Jangan rush.
- [ ] **Prepare pronunciation:** 'Sultanum', 'Setlur', 'semantic', 'heuristics'—practice ini.
- [ ] **Know your numbers:** 190 dashboards, 13 experts, 9 components, 4 levels, 12 heuristics, 55%, 49%
- [ ] **Prepare 2-3 real examples:** Bawa screenshots dari dashboards untuk illustrate points.

### During Presentation:

- **Eye contact:** Maintain engagement dengan audience
- **Pacing:** Jangan baca slides word-for-word. Paraphrase. Slides are GUIDES, not scripts.
- **Emphasis:**
  - Slide 2: Emphasize WHY (gap research, relevance)
  - Slide 3: Emphasize WHAT & HOW (components, semantic levels, dashboard genre effect)
  - Slide 4: Emphasize REAL-WORLD APPLICATION
  - Slide 5: Emphasize BIGGER PICTURE
- **Interactivity:** Ask audience: "Siapa yang pernah lihat dashboard yang explains data terlalu banyak?" untuk create engagement.
- **Pauses:** Jangan takut pause setelah poin important—biar audience absorb.

### Jika Ada Pertanyaan:

**Q: "Apa difference antara ini dan previous research on text in charts?"**  
A: "Good question. Previous research mostly focus pada single-chart annotations—misalnya, bagaimana title & caption mempengaruhi interpretation dari satu chart. Tapi dashboard punya multiple charts, filters, interactive elements—it's more complex ecosystem. This paper specifically examine text dalam multi-component environment itu."

**Q: "12 heuristics ini daftar panjang. Mana yang most important?"**  
A: "That's practical question. Based on expert interviews, formatting heuristics (HP category) adalah yang most frequently practiced. But importance depends pada context—narrative dashboards prioritize HA heuristics (analytical support), exploratory dashboards prioritize HN heuristics (navigation)."

**Q: "Gimana kalau dashboard yang already exist? Apakah findings ini bisa applied?"**  
A: "Yes, definitely. Audit existing dashboard against 12 heuristics, identify gaps, prioritize improvements. Start dengan high-impact elements—titles, metadata, key annotations."

---

## 📚 QUICK REFERENCE STATS

**Jangan hafal, tapi know these:**

- 55% of public dashboards contain substantial text
- 190 dashboards analyzed (116 Tableau, 50 Power BI, 24 others)
- 13 expert interviews (10+ years average experience)
- 9-11 text component types
- 4 semantic levels (LV1-LV4)
- 12 heuristics for recommended practices
- 49% of dashboards use dynamic text
- Narrative dashboards: 91% have content blocks, 76% have LV4 content
- Exploratory dashboards: 53% have content blocks, 33% have LV4 content

---

## ✅ CHECKLIST SEBELUM PRESENTASI

- [ ] Slide sudah di-review dan benar
- [ ] Practice presentation min 2x
- [ ] Timing check (should be ~15-20 min)
- [ ] Know pronunciation dari terms kunci
- [ ] Have 2-3 dashboard screenshots as examples
- [ ] Prepare 1-2 backup answers untuk potential questions
- [ ] Dress appropriately, arrive early
- [ ] Bring printed notes (optional, untuk reference)

---

## 🎯 SETELAH PRESENTASI

Jika dosen tanya lebih lanjut atau minta elaboration:

**Siap jawab dengan confidence:**

- Konteks paper (IEEE TVCG 2024, recent & credible)
- Metodologi (empirical study + expert validation)
- Practical relevance (tools, sektor applications)
- Future directions (research opportunities)
- Critical thinking (benefits + challenges + limitations)

Good luck! 🚀

---

_Note: Dokumentasi ini adalah study guide untuk presentasi Anda. Read through sekali sebelum presentasi, highlight poin-poin yang ingin Anda emphasize, dan practice dengan timing._
