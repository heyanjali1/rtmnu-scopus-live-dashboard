# 🏛️ RTMNU Live Scopus Intelligence Dashboard
### Rashtrasant Tukadoji Maharaj Nagpur University (Estd. 1923) • Centenary State University
**NIRF ID:** `IR-O-U-0320` (Category: University) | **Accreditation:** ⭐ NAAC A+ (CGPA 3.32) | **Scopus AF-ID:** `60015668`

---

## 🌟 Overview
The **RTMNU Live Scopus Intelligence Dashboard** is an enterprise-grade bibliometric intelligence portal designed to monitor, analyze, and synthesize scholarly research output for **Rashtrasant Tukadoji Maharaj Nagpur University (RTMNU)**. 

Built with **Python**, **Streamlit**, and **Plotly**, the dashboard integrates with the **Elsevier Scopus Search API** using cursor pagination, 60-minute auto-sync, and high-performance local caching.

---

## 🏛️ Key Institutional Identifiers
- **Institution Name:** Rashtrasant Tukadoji Maharaj Nagpur University (RTMNU)
- **Location:** Nagpur, Maharashtra, India
- **Status:** Centenary State University (Established 1923)
- **NIRF Institutional ID:** `IR-O-U-0320`
- **NAAC Accreditation:** Grade A+ (CGPA 3.32)
- **Scopus Affiliation ID:** `60015668`
- **Live Scopus Multi-Variant Query:**
  ```sql
  AF-ID(60015668) OR AFFIL({Rashtrasant Tukadoji Maharaj Nagpur University}) OR AFFIL({Nagpur University}) OR AFFIL({RTMNU}) OR AFFIL({RTM Nagpur University})
  ```

---

## 🚀 Analytical Capabilities across 7 Tabs

| Tab | Feature & Visual Components |
| :--- | :--- |
| **📈 Tab 1: Trends** | **Dual-Axis Chart**: Annual publications (Blue `#0284C7`) + Cumulative Total (Gold `#F59E0B`, width 3) + Monthly publication velocity + Detailed statistics table. |
| **🎯 Tab 2: Impact** | **Citation Accrual Curve**: Cumulative growth trajectory + Department citations ranking + Top 20 Landmark papers with live clickable **`DOI (↗)`** links. |
| **🌐 Tab 3: Collaboration** | **Global Choropleth Map**: International co-authorship world map + Top 10 partner nations + Institutional disciplinary treemap + Corporate/Industry R&D breakdown. |
| **🏆 Tab 4: Quality & Benchmarks** | **Quartiles Donut (Q1–Q4)** + Impact vs. Volume Quadrant Bubble Chart with **Gold Benchmark Line** (Univ Avg CPP) + Multi-dimensional Department Radar Benchmark. |
| **👥 Tab 5: Authors & Dossier** | **Top 3 Podium Cards** (🥇 Gold, 🥈 Silver, 🥉 Bronze) + 50-Author Leaderboard + Faculty Selector + **`🖨 Print Profile` 100% Isolated 1-Click Browser Print** + Dynamic Dossier + Offline HTML export. |
| **📡 Tab 6: Live Feed** | Searchable publications catalog with **📊 Export Excel (`.xlsx`)**, **📑 Export BibTeX (`.bib`)**, and **📄 Export CSV (`.csv`)**. |
| **🤖 Tab 7: AI Copilot** | Fast zero-external-API natural language research assistant with prompt chips (`📊 Executive Dossier`, `🏛 Dept Rankings`, `🏆 Q1 Quality Analysis`, `👥 Top Authors`) & **`🗑 Clear Chat History`**. |

---

## 🛠️ Tech Stack & Design System
- **Frontend / UI:** Streamlit with custom **ICARE Glassmorphism Design System** (`styles.py`).
- **Theming:** Full **🌙 Dark Mode** (`#070D1E`) & **☀️ Light Mode** (`#F8FAFC`) support with high-contrast typography and dynamic BaseWeb widget styling.
- **Data & Visualizations:** Pandas, Plotly Express, Plotly Graph Objects.
- **API Connectivity:** Elsevier Scopus Search API (`https://api.elsevier.com/content/search/scopus`) with cursor pagination and offline fallback engine (`mock_data.py`).
- **Exports:** OpenPyXL (Excel), BibTeX, CSV, and standalone HTML print dossiers.

---

## 💻 Local Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/heyanjali1/rtmnu-scopus-live-dashboard.git
   cd rtmnu-scopus-live-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Scopus API Key:**
   Create a `.env` file in the root directory:
   ```ini
   SCOPUS_API_KEY="your_elsevier_scopus_api_key_here"
   ```

4. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 🏛️ Credits & Institutional Portal
- **Institution:** Rashtrasant Tukadoji Maharaj Nagpur University (RTMNU)
- **Portal Intelligence:** Powered by **ICARE Ratings & Rankings Portal Intelligence** & Elsevier Scopus Search API.
