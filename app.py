"""
RTMNU Live Scopus Intelligence Dashboard - Final Production Release
Centenary State University (Estd. 1923) | NIRF ID: IR-P-U-0332 | Scopus AF-ID: 60028250
Full 7-Tab Research Intelligence Portal, ICARE Glassmorphic UI, Plotly Charts, AI Copilot & 1-Click Isolated Print Dossier.
"""

import io
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import UNIVERSITY_CONFIG
from scopus_api import get_rtmnu_scopus_data
from data_processor import (
    calculate_top_10_kpis,
    get_publications_by_year,
    get_publications_by_month,
    get_top_authors_leaderboard,
    get_author_profile_metrics,
    filter_publications,
    export_to_bibtex,
    generate_author_print_html
)
from ai_copilot import (
    answer_custom_query,
    generate_executive_dossier,
    generate_department_rankings,
    generate_q1_analysis,
    generate_top_authors_analysis
)
from styles import (
    get_custom_css,
    render_icare_topbar,
    render_icare_hero,
    render_kpi_card
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title=UNIVERSITY_CONFIG.get("app_title", "RTMNU Live Scopus Intelligence Dashboard"),
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Responsive Sidebar JavaScript (Desktop permanent open / Mobile collapse)
# ---------------------------------------------------------
responsive_sidebar_js = """
<script>
(function() {
    function adjustSidebar() {
        const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
        const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
        const collapseBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]');
        if (window.innerWidth > 768) {
            if (sidebar && sidebar.getAttribute('aria-expanded') === 'false') {
                if (collapseBtn) collapseBtn.click();
            }
        }
    }
    window.addEventListener('resize', adjustSidebar);
    setTimeout(adjustSidebar, 300);
})();
</script>
"""
components.html(responsive_sidebar_js, height=0, width=0)

# ---------------------------------------------------------
# Sidebar: Brand Box, Gateway Status, Live Sync & Filters
# ---------------------------------------------------------
with st.sidebar:
    # 1. Brand Box
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.15) 0%, rgba(14, 23, 42, 0.8) 100%); border: 1px solid rgba(2, 132, 199, 0.3); border-radius: 14px; padding: 14px 16px; margin-bottom: 14px;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 15px; font-weight: 800; color: #0284C7; letter-spacing: 0.03em;">
                🏛 RTMNU PORTAL
            </div>
            <div style="font-size: 11px; font-weight: 600; color: #F1F5F9; margin-top: 2px;">
                Live Scopus Intelligence <span style="color: #38BDF8;">[{UNIVERSITY_CONFIG.get('nirf_id', 'IR-P-U-0332')}]</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Live Scopus Feed Status Indicator
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 8px 12px; margin-bottom: 14px; font-size: 11px; font-weight: 600; color: #10B981;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></span>
            <span>Live Scopus Feed • Auto-synced every 60m</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Scopus Gateway Panel & Manual Refresh
    st.markdown(
        """
        <div style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
            🔄 Scopus Gateway
        </div>
        """,
        unsafe_allow_html=True
    )
    force_sync = st.button("🔄 Sync Scopus Now", use_container_width=True, help="Executes live institutional query against Elsevier Scopus API")
    if force_sync:
        st.cache_data.clear()

    # 4. Theme Switcher
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Display Theme",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0,
        horizontal=True
    )
    current_theme = "dark" if "Dark" in theme_choice else "light"

    st.markdown("---")

# ---------------------------------------------------------
# Data Ingestion Engine
# ---------------------------------------------------------
@st.cache_data(ttl=UNIVERSITY_CONFIG.get("cache_ttl_seconds", 3600), show_spinner=False)
def load_data(refresh_flag: bool = False):
    return get_rtmnu_scopus_data(force_refresh=refresh_flag)

with st.spinner("Connecting to Scopus Intelligence Gateway..."):
    df_raw, sync_meta = load_data(force_sync)

# ---------------------------------------------------------
# Sidebar Multi-dimensional Filters
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Research Filters")
    
    # 5. Year Slider 1950 - 2026
    data_min_year = int(df_raw["year"].min()) if not df_raw.empty and "year" in df_raw.columns else 2012
    slider_min = min(1950, data_min_year)
    slider_max = 2026
    
    year_range = st.slider(
        "Publication Year Range (1950 - 2026)",
        min_value=slider_min,
        max_value=slider_max,
        value=(data_min_year, slider_max),
        step=1
    )
    
    # Academic Departments Multiselect
    all_depts = sorted(df_raw["department"].dropna().unique().tolist()) if "department" in df_raw.columns else []
    selected_depts = st.multiselect(
        "Academic Department",
        options=all_depts,
        default=[]
    )
    
    # Journal Quartile Multiselect
    selected_quartiles = st.multiselect(
        "Journal Quartile",
        options=["Q1", "Q2", "Q3", "Q4"],
        default=[]
    )
    
    # Collaboration Type
    collab_filter = st.multiselect(
        "Collaboration Type",
        options=["International", "Industry"],
        default=[]
    )
    
    # Document Type Multiselect
    all_doc_types = sorted(df_raw["document_type"].dropna().unique().tolist()) if "document_type" in df_raw.columns else []
    selected_doc_types = st.multiselect(
        "Document Type",
        options=all_doc_types,
        default=[]
    )
    
    # Live Search Bar
    search_text = st.text_input("🔎 Search Title, Author, DOI", placeholder="e.g. Nanoparticles, Deshmukh...")
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size: 11px; color: #94A3B8; line-height: 1.5;">
            <b>Scopus Query:</b><br>
            <code style="font-size: 10px;">AF-ID(60028250) OR RTMNU</code><br>
            <b>Data Mode:</b> <span style="color:#38BDF8;">{sync_meta.get('source', 'Cached')}</span><br>
            <b>Last Synced:</b> {str(sync_meta.get('last_synced', 'Live'))[:16].replace('T', ' ')}
        </div>
        """,
        unsafe_allow_html=True
    )

# Apply global filters
df_filtered = filter_publications(
    df_raw,
    year_range=year_range,
    depts=selected_depts,
    quartiles=selected_quartiles,
    collab_types=collab_filter,
    doc_types=selected_doc_types,
    search_query=search_text
)

# ---------------------------------------------------------
# Inject Custom Glassmorphic Styles & Top Navigation
# ---------------------------------------------------------
st.markdown(get_custom_css(current_theme), unsafe_allow_html=True)
st.markdown(render_icare_topbar(current_theme), unsafe_allow_html=True)

# Compute Top 10 KPIs
kpis = calculate_top_10_kpis(df_filtered)

# Render Hero Banner
st.markdown(render_icare_hero(kpis["total_output"], kpis["total_citations"], current_theme), unsafe_allow_html=True)

# ---------------------------------------------------------
# Top 10 Core KPI Cards Grid
# ---------------------------------------------------------
st.markdown("### 📊 University Research Scorecard (Top 10 Core KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(render_kpi_card(
        icon="📚",
        title="Scopus Total Output",
        value=f"{kpis['total_output']:,}",
        subtext=f"{year_range[0]} - {year_range[1]} Indexed",
        delta=f"Active in {len(all_depts)} Depts",
        delta_type="up"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(render_kpi_card(
        icon="🚀",
        title="2026 Volume (Live)",
        value=f"{kpis['volume_2026']:,}",
        subtext=f"vs. 2025: {kpis['volume_2025']:,}",
        delta=f"{kpis['growth_rate_25_26']:+0.1f}% YoY",
        delta_type="up" if kpis['growth_rate_25_26'] >= 0 else "gold"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(render_kpi_card(
        icon="💡",
        title="Global Citations",
        value=f"{kpis['total_citations']:,}",
        subtext=f"CPP: {kpis['citations_per_paper']} Cites/Paper",
        delta=f"h-Index: {kpis['h_index']}",
        delta_type="up"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(render_kpi_card(
        icon="⭐",
        title="Q1 High-Impact Papers",
        value=f"{kpis['q1_count']:,}",
        subtext=f"{kpis['q1_percentage']}% of Total Output",
        delta="Top Quartile (Q1)",
        delta_type="up"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(render_kpi_card(
        icon="🌐",
        title="Global Collab Rate",
        value=f"{kpis['intl_collab_pct']}%",
        subtext=f"Industry: {kpis['industry_collab_pct']}%",
        delta=f"{kpis['active_authors']:,} Active Authors",
        delta_type="gold"
    ), unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Plotly Theme Styling
# ---------------------------------------------------------
plot_template = "plotly_dark" if current_theme == "dark" else "plotly_white"
plot_bg = "rgba(14, 23, 42, 0.4)" if current_theme == "dark" else "rgba(255, 255, 255, 0.6)"
paper_bg = "rgba(0,0,0,0)"
grid_color = "rgba(255, 255, 255, 0.08)" if current_theme == "dark" else "rgba(0, 0, 0, 0.06)"
text_color = "#F1F5F9" if current_theme == "dark" else "#0F172A"

# ---------------------------------------------------------
# Tabs 1 to 7 Navigation
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Tab 1: Trends",
    "🎯 Tab 2: Impact",
    "🌐 Tab 3: Collaboration",
    "🏆 Tab 4: Quality & Benchmarks",
    "👥 Tab 5: Authors & Dossier",
    "📡 Tab 6: Live Feed",
    "🤖 Tab 7: AI Copilot"
])

# =========================================================
# TAB 1: RESEARCH OUTPUT & GROWTH TRENDS
# =========================================================
with tab1:
    st.markdown("#### 📈 Longitudinal Publication Trends & Citation Trajectory")
    
    col_t1, col_t2 = st.columns([7, 5])
    df_yearly = get_publications_by_year(df_filtered)
    
    with col_t1:
        if not df_yearly.empty:
            df_yearly["cumulative_pubs"] = df_yearly["publications"].cumsum()
            
            fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_trends.add_trace(
                go.Bar(
                    x=df_yearly["year"],
                    y=df_yearly["publications"],
                    name="Annual Publications",
                    marker_color="#0284C7",
                    opacity=0.85,
                    hovertemplate="<b>Year %{x}</b><br>Publications: %{y:,}<extra></extra>"
                ),
                secondary_y=False
            )
            
            fig_trends.add_trace(
                go.Scatter(
                    x=df_yearly["year"],
                    y=df_yearly["cumulative_pubs"],
                    name="Cumulative Output",
                    line=dict(color="#F59E0B", width=3, shape="spline"),
                    mode="lines+markers",
                    marker=dict(size=6, color="#F59E0B"),
                    hovertemplate="<b>Year %{x}</b><br>Cumulative: %{y:,}<extra></extra>"
                ),
                secondary_y=True
            )
            
            fig_trends.update_layout(
                title=dict(text="<b>Annual Publication Output & Cumulative Growth</b>", font=dict(color=text_color, size=15)),
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color)),
                margin=dict(l=40, r=40, t=60, b=40),
                height=380
            )
            fig_trends.update_xaxes(title_text="Publication Year", gridcolor=grid_color, tickmode="linear")
            fig_trends.update_yaxes(title_text="Annual Publications", secondary_y=False, gridcolor=grid_color)
            fig_trends.update_yaxes(title_text="Cumulative Publications", secondary_y=True, showgrid=False)
            
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")

    with col_t2:
        st.markdown("##### ⏱️ Monthly Publication Velocity (Recent Annual Pace)")
        latest_year = int(df_filtered["year"].max()) if not df_filtered.empty else 2025
        df_monthly = get_publications_by_month(df_filtered, latest_year)
        
        fig_month = px.bar(
            df_monthly,
            x="month_name",
            y="publications",
            title=f"<b>Monthly Distribution ({latest_year})</b>",
            color_discrete_sequence=["#06B6D4"]
        )
        fig_month.update_layout(
            template=plot_template,
            plot_bgcolor=plot_bg,
            paper_bgcolor=paper_bg,
            margin=dict(l=40, r=20, t=60, b=40),
            height=380,
            xaxis=dict(title="Month", gridcolor=grid_color),
            yaxis=dict(title="Papers Published", gridcolor=grid_color)
        )
        st.plotly_chart(fig_month, use_container_width=True)

    with st.expander("📑 View Detailed Annual Statistics Table"):
        if not df_yearly.empty:
            st.dataframe(
                df_yearly.rename(columns={
                    "year": "Year",
                    "publications": "Publications",
                    "citations": "Total Citations",
                    "cpp": "CPP (Cites/Paper)",
                    "q1_count": "Q1 Papers",
                    "intl_count": "Intl Collabs"
                }),
                use_container_width=True,
                hide_index=True
            )

# =========================================================
# TAB 2: CITATION IMPACT & LANDMARK PAPERS
# =========================================================
with tab2:
    st.markdown("#### 🎯 Citation Accrual & High-Impact Department Analysis")
    
    col_i1, col_i2 = st.columns([6, 6])
    
    with col_i1:
        if not df_yearly.empty:
            fig_cits = go.Figure()
            fig_cits.add_trace(
                go.Scatter(
                    x=df_yearly["year"],
                    y=df_yearly["citations"],
                    name="Annual Citations",
                    line=dict(color="#10B981", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(16, 185, 129, 0.15)",
                    mode="lines+markers"
                )
            )
            fig_cits.update_layout(
                title=dict(text="<b>Annual Citation Accrual Curve</b>", font=dict(color=text_color, size=15)),
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=40, r=20, t=60, b=40),
                height=350,
                xaxis=dict(title="Year", gridcolor=grid_color),
                yaxis=dict(title="Citations Accrued", gridcolor=grid_color)
            )
            st.plotly_chart(fig_cits, use_container_width=True)
    
    with col_i2:
        if not df_filtered.empty and "department" in df_filtered.columns:
            dept_cits = df_filtered.groupby("department")["citations"].sum().reset_index()
            dept_cits = dept_cits.sort_values("citations", ascending=True).tail(10)
            
            fig_dept_cits = px.bar(
                dept_cits,
                x="citations",
                y="department",
                orientation="h",
                title="<b>Top 10 Departments by Cumulative Citations</b>",
                color="citations",
                color_continuous_scale="Blues"
            )
            fig_dept_cits.update_layout(
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=40, r=20, t=60, b=40),
                height=350,
                xaxis=dict(title="Total Citations", gridcolor=grid_color),
                yaxis=dict(title="", gridcolor=grid_color),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_dept_cits, use_container_width=True)

    st.markdown("##### 🏆 RTMNU Landmark Research Papers (Top Cited)")
    if not df_filtered.empty:
        top_papers = df_filtered.sort_values("citations", ascending=False).head(20).copy()
        
        def make_clickable_doi(row):
            doi = row.get("doi", "")
            if doi and str(doi).startswith("10."):
                return f"[{doi}](https://doi.org/{doi}) ↗"
            return "N/A"

        top_papers["DOI Link"] = top_papers.apply(make_clickable_doi, axis=1)
        
        display_cols = ["title", "primary_author", "journal", "year", "department", "citations", "quartile", "DOI Link"]
        st.dataframe(
            top_papers[display_cols].rename(columns={
                "title": "Document Title",
                "primary_author": "Lead Author",
                "journal": "Journal / Venue",
                "year": "Year",
                "department": "Department",
                "citations": "Citations",
                "quartile": "Quartile"
            }),
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# TAB 3: GLOBAL COLLABORATION & INDUSTRY PARTNERSHIPS
# =========================================================
with tab3:
    st.markdown("#### 🌐 Global Collaboration Map & Industrial R&D Ecosystem")
    
    country_counts = {}
    for clist in df_filtered["countries"].dropna():
        if isinstance(clist, list):
            for c in clist:
                if c != "India":
                    country_counts[c] = country_counts.get(c, 0) + 1
        elif isinstance(clist, str) and clist != "India":
            country_counts[clist] = country_counts.get(clist, 0) + 1

    df_countries = pd.DataFrame(list(country_counts.items()), columns=["country", "collaborations"])
    
    col_c1, col_c2 = st.columns([7, 5])
    
    with col_c1:
        if not df_countries.empty:
            fig_map = px.choropleth(
                df_countries,
                locations="country",
                locationmode="country names",
                color="collaborations",
                hover_name="country",
                color_continuous_scale="Viridis",
                title="<b>Global Collaboration Footprint (RTMNU Co-Authored Works)</b>"
            )
            fig_map.update_layout(
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=0, r=0, t=50, b=0),
                height=380,
                geo=dict(showframe=False, showcoastlines=True, bgcolor=plot_bg)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No international collaboration records in the selected subset.")

    with col_c2:
        if not df_countries.empty:
            top_countries = df_countries.sort_values("collaborations", ascending=True).tail(10)
            fig_c_bar = px.bar(
                top_countries,
                x="collaborations",
                y="country",
                orientation="h",
                title="<b>Top 10 Partner Countries</b>",
                color_discrete_sequence=["#F59E0B"]
            )
            fig_c_bar.update_layout(
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=40, r=20, t=50, b=40),
                height=380,
                xaxis=dict(title="Joint Publications", gridcolor=grid_color),
                yaxis=dict(title="", gridcolor=grid_color)
            )
            st.plotly_chart(fig_c_bar, use_container_width=True)

    col_t1, col_t2 = st.columns([7, 5])
    
    with col_t1:
        st.markdown("##### 🏛️ Institutional Research Distribution Treemap")
        if not df_filtered.empty and "category" in df_filtered.columns and "department" in df_filtered.columns:
            treemap_df = df_filtered.groupby(["category", "department"]).size().reset_index(name="count")
            fig_tree = px.treemap(
                treemap_df,
                path=["category", "department"],
                values="count",
                color="count",
                color_continuous_scale="Blues",
                title="<b>Faculty Output by Broad Discipline & Department</b>"
            )
            fig_tree.update_layout(
                template=plot_template,
                paper_bgcolor=paper_bg,
                margin=dict(l=10, r=10, t=50, b=10),
                height=340
            )
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_t2:
        st.markdown("##### 🏭 Corporate & Industry R&D Collaborations")
        ind_pubs = df_filtered[df_filtered["is_industry_collab"].fillna(False).astype(bool)]
        st.markdown(
            f"""
            <div class="glass-container" style="padding: 16px;">
                <div style="font-size: 24px; font-weight: 700; color: #F59E0B;">{len(ind_pubs):,} Papers</div>
                <div style="font-size: 13px; color: #94A3B8; margin-bottom: 10px;">
                    Co-authored with pharmaceutical, chemical, energy, and IT industries.
                </div>
                <div style="font-size: 12px; line-height: 1.6;">
                    • <b>Pharma & Health:</b> Sun Pharma, Cipla R&D, Lupin, Pfizer<br>
                    • <b>Chemical & Energy:</b> Reliance Industries, Tata Chemicals, Thermax<br>
                    • <b>Tech & AI:</b> Intel Labs, IBM Research, Mahindra Valley
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# TAB 4: QUALITY, QUARTILES & BENCHMARKS
# =========================================================
with tab4:
    st.markdown("#### 🏆 Research Quality, Quartile Breakdown & Department Benchmarks")
    
    col_q1, col_q2 = st.columns([5, 7])
    
    with col_q1:
        if "quartile" in df_filtered.columns:
            q_counts = df_filtered["quartile"].value_counts().reset_index()
            q_counts.columns = ["quartile", "count"]
            
            color_map = {
                "Q1": "#10B981",
                "Q2": "#3B82F6",
                "Q3": "#F59E0B",
                "Q4": "#EF4444"
            }
            
            fig_donut = px.pie(
                q_counts,
                names="quartile",
                values="count",
                hole=0.55,
                color="quartile",
                color_discrete_map=color_map,
                title="<b>Scopus Journal Quartile Distribution (Q1 - Q4)</b>"
            )
            fig_donut.update_layout(
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=20, r=20, t=50, b=20),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with col_q2:
        if not df_filtered.empty and "department" in df_filtered.columns:
            dept_stats = df_filtered.groupby("department").agg(
                publications=("scopus_id", "count"),
                total_citations=("citations", "sum"),
                q1_count=("quartile", lambda s: (s == "Q1").sum()),
                cpp=("citations", lambda s: (s.sum() / max(1, len(s))))
            ).reset_index()
            
            avg_cpp = df_filtered["citations"].sum() / max(1, len(df_filtered))
            
            fig_bubble = px.scatter(
                dept_stats,
                x="publications",
                y="cpp",
                size="total_citations",
                color="department",
                hover_name="department",
                title="<b>Impact vs. Volume Quadrant (Departmental Benchmark)</b>",
                labels={"publications": "Total Publications", "cpp": "Citations Per Paper (CPP)"}
            )
            
            fig_bubble.add_hline(
                y=avg_cpp,
                line_dash="dash",
                line_color="#F59E0B",
                line_width=2,
                annotation_text=f"Univ Avg CPP ({avg_cpp:.1f})",
                annotation_position="top right",
                annotation_font_color="#F59E0B"
            )
            
            fig_bubble.update_layout(
                template=plot_template,
                plot_bgcolor=plot_bg,
                paper_bgcolor=paper_bg,
                margin=dict(l=40, r=20, t=50, b=40),
                height=350,
                showlegend=False,
                xaxis=dict(gridcolor=grid_color),
                yaxis=dict(gridcolor=grid_color)
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("##### 🕸️ Departmental Multi-Dimensional Benchmark Radar")
    if not df_filtered.empty:
        top_depts_list = df_filtered["department"].value_counts().head(5).index.tolist()
        radar_fig = go.Figure()
        categories = ["Volume", "Total Citations", "CPP (Impact)", "Q1 Share %", "Intl Collab %"]
        
        for dept in top_depts_list:
            sub = df_filtered[df_filtered["department"] == dept]
            v = len(sub) / max(1, len(df_filtered)) * 100 * 5
            c = sub["citations"].sum() / max(1, df_filtered["citations"].sum()) * 100 * 5
            cpp_val = min(100, (sub["citations"].sum() / max(1, len(sub))) * 5)
            q1_val = (sub["quartile"] == "Q1").sum() / max(1, len(sub)) * 100
            intl_val = sub["is_international_collab"].fillna(False).sum() / max(1, len(sub)) * 100
            
            radar_fig.add_trace(go.Scatterpolar(
                r=[v, c, cpp_val, q1_val, intl_val],
                theta=categories,
                fill='toself',
                name=dept.split("(")[0].strip()
            ))
            
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template=plot_template,
            paper_bgcolor=paper_bg,
            margin=dict(l=40, r=40, t=40, b=40),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(radar_fig, use_container_width=True)

# =========================================================
# TAB 5: AUTHOR INTELLIGENCE & 1-CLICK ISOLATED PRINT DOSSIER
# =========================================================
with tab5:
    st.markdown("#### 👥 Faculty & Researcher Intelligence Leaderboard")
    
    df_leaderboard = get_top_authors_leaderboard(df_filtered, top_n=50)
    
    if not df_leaderboard.empty and len(df_leaderboard) >= 3:
        p1 = df_leaderboard.iloc[0]
        p2 = df_leaderboard.iloc[1]
        p3 = df_leaderboard.iloc[2]
        
        pod1, pod2, pod3 = st.columns(3)
        
        with pod1:
            st.markdown(
                f"""
                <div class="glass-container" style="border: 2px solid #F59E0B; background: rgba(245, 158, 11, 0.08); padding: 18px; border-radius: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px;">🥇</span>
                        <span class="icare-badge icare-badge-gold">RANK 1 • GOLD</span>
                    </div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; color: #F59E0B;">
                        {p1['author']}
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">{p1['department']}</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center;">
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700;">{p1['publications']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">PAPERS</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #F59E0B;">{p1['citations']:,}</div>
                            <div style="font-size: 9px; color: #94A3B8;">CITES</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #10B981;">{p1['h_index']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">h-INDEX</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with pod2:
            st.markdown(
                f"""
                <div class="glass-container" style="border: 2px solid #94A3B8; background: rgba(148, 163, 184, 0.08); padding: 18px; border-radius: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px;">🥈</span>
                        <span class="icare-badge" style="background: rgba(148,163,184,0.15); color: #94A3B8; border: 1px solid rgba(148,163,184,0.3);">RANK 2 • SILVER</span>
                    </div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; color: #E2E8F0;">
                        {p2['author']}
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">{p2['department']}</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center;">
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700;">{p2['publications']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">PAPERS</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #F59E0B;">{p2['citations']:,}</div>
                            <div style="font-size: 9px; color: #94A3B8;">CITES</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #10B981;">{p2['h_index']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">h-INDEX</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with pod3:
            st.markdown(
                f"""
                <div class="glass-container" style="border: 2px solid #B45309; background: rgba(180, 83, 9, 0.08); padding: 18px; border-radius: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px;">🥉</span>
                        <span class="icare-badge" style="background: rgba(180,83,9,0.15); color: #D97706; border: 1px solid rgba(180,83,9,0.3);">RANK 3 • BRONZE</span>
                    </div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; color: #FBBF24;">
                        {p3['author']}
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">{p3['department']}</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center;">
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700;">{p3['publications']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">PAPERS</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #F59E0B;">{p3['citations']:,}</div>
                            <div style="font-size: 9px; color: #94A3B8;">CITES</div>
                        </div>
                        <div style="background: rgba(14, 23, 42, 0.6); padding: 6px; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: 700; color: #10B981;">{p3['h_index']}</div>
                            <div style="font-size: 9px; color: #94A3B8;">h-INDEX</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.expander("📋 View Complete Faculty Leaderboard (Top 50 Authors)", expanded=False):
        if not df_leaderboard.empty:
            st.dataframe(
                df_leaderboard.rename(columns={
                    "author": "Faculty Name",
                    "department": "Primary Department",
                    "publications": "Publications",
                    "citations": "Total Citations",
                    "cpp": "CPP (Cites/Paper)",
                    "h_index": "Author h-Index",
                    "q1_papers": "Q1 Papers"
                }),
                use_container_width=True,
                hide_index=True
            )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔬 Dynamic Author Dossier & Isolated 1-Click Print")

    all_author_options = df_leaderboard["author"].tolist() if not df_leaderboard.empty else []
    
    if all_author_options:
        sel_col1, sel_col2 = st.columns([8, 4])
        
        with sel_col1:
            selected_author = st.selectbox(
                "Select Faculty Researcher to Inspect",
                options=all_author_options,
                index=0,
                help="Authors sorted by indexed Scopus publication volume"
            )
            
        with sel_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            print_trigger = st.button("🖨 Print Profile", use_container_width=True, help="100% Isolated 1-Click Browser Print of Faculty Dossier")

        auth_profile = get_author_profile_metrics(df_filtered, selected_author)
        author_papers_df = auth_profile.get("publications_df", pd.DataFrame())
        author_trend_df = auth_profile.get("trend_df", pd.DataFrame())

        print_html = generate_author_print_html(auth_profile, author_papers_df, author_trend_df)
        
        if print_trigger:
            b64_html = base64.b64encode(print_html.encode('utf-8')).decode('utf-8')
            js_code = f"""
            <script>
            (function() {{
                const b64 = "{b64_html}";
                const html = decodeURIComponent(escape(window.atob(b64)));
                const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
                let frame = parentDoc.getElementById('author-print-isolated-frame');
                if (frame) frame.remove();
                frame = parentDoc.createElement('iframe');
                frame.id = 'author-print-isolated-frame';
                frame.style.position = 'fixed'; frame.style.right = '0'; frame.style.bottom = '0';
                frame.style.width = '0'; frame.style.height = '0'; frame.style.border = '0';
                parentDoc.body.appendChild(frame);
                const doc = frame.contentWindow.document;
                doc.open(); doc.write(html); doc.close();
                setTimeout(() => {{ frame.contentWindow.focus(); frame.contentWindow.print(); }}, 350);
            }})();
            </script>
            """
            components.html(js_code, height=0, width=0)
            st.success(f"🖨 Print dialog dispatched for **{selected_author}**!")

        st.markdown(
            f"""
            <div class="icare-hero" style="padding: 22px 26px; margin-top: 14px;">
                <div class="badge-ribbon">
                    <span class="icare-badge icare-badge-gold">⭐ Q1 Papers: {auth_profile['q1_count']}</span>
                    <span class="icare-badge icare-badge-blue">🌐 Intl Collab: {auth_profile['intl_collab_pct']:.0f}%</span>
                    <span class="icare-badge">🏭 Industry Collab: {auth_profile['industry_collab_pct']:.0f}%</span>
                    <span class="icare-badge">👥 Co-Authors: {auth_profile['co_authors_count']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div>
                        <h2 style="margin: 0; font-size: 26px; font-weight: 700; color: #0284C7;">{auth_profile['author_name']}</h2>
                        <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">
                            {auth_profile['department']} • Rashtrasant Tukadoji Maharaj Nagpur University (RTMNU)
                        </p>
                    </div>
                    <div style="text-align: right; font-size: 12px; color: #64748B;">
                        Scopus AF-ID: <b>60028250</b> | Centenary State University
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(render_kpi_card(
                icon="📚",
                title="Publications",
                value=f"{auth_profile['publications_count']:,}",
                subtext="Scopus Indexed",
                delta=f"Rank #{df_leaderboard[df_leaderboard['author']==selected_author].index[0]+1 if not df_leaderboard[df_leaderboard['author']==selected_author].empty else 'N/A'}",
                delta_type="up"
            ), unsafe_allow_html=True)
            
        with k2:
            st.markdown(render_kpi_card(
                icon="💡",
                title="Total Citations",
                value=f"{auth_profile['total_citations']:,}",
                subtext="Global Accrual",
                delta=f"CPP: {auth_profile['cpp']:.1f}",
                delta_type="gold"
            ), unsafe_allow_html=True)
            
        with k3:
            st.markdown(render_kpi_card(
                icon="📈",
                title="Cites / Paper (CPP)",
                value=f"{auth_profile['cpp']:.2f}",
                subtext="Impact Factor Ratio",
                delta="Research Velocity",
                delta_type="up"
            ), unsafe_allow_html=True)
            
        with k4:
            st.markdown(render_kpi_card(
                icon="🎯",
                title="Author h-Index",
                value=f"{auth_profile['h_index']}",
                subtext="Hirsch Citation Metric",
                delta="Key Benchmark",
                delta_type="up"
            ), unsafe_allow_html=True)
            
        with k5:
            st.markdown(render_kpi_card(
                icon="⭐",
                title="Q1 Publication Ratio",
                value=f"{auth_profile['q1_percentage']:.0f}%",
                subtext=f"{auth_profile['q1_count']} Q1 Articles",
                delta="Top-Tier Journals",
                delta_type="up"
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        c_ch1, c_ch2 = st.columns([7, 5])
        
        with c_ch1:
            if not author_trend_df.empty:
                author_trend_df["cum_pubs"] = author_trend_df["publications"].cumsum()
                
                fig_auth_trend = make_subplots(specs=[[{"secondary_y": True}]])
                fig_auth_trend.add_trace(
                    go.Bar(
                        x=author_trend_df["year"],
                        y=author_trend_df["publications"],
                        name="Annual Papers",
                        marker_color="#0284C7",
                        opacity=0.85
                    ),
                    secondary_y=False
                )
                fig_auth_trend.add_trace(
                    go.Scatter(
                        x=author_trend_df["year"],
                        y=author_trend_df["citations"],
                        name="Citations Accrued",
                        line=dict(color="#F59E0B", width=3),
                        mode="lines+markers"
                    ),
                    secondary_y=True
                )
                fig_auth_trend.update_layout(
                    title=dict(text=f"<b>Annual Publication & Citation Trajectory: {selected_author}</b>", font=dict(color=text_color, size=14)),
                    template=plot_template,
                    plot_bgcolor=plot_bg,
                    paper_bgcolor=paper_bg,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=320
                )
                fig_auth_trend.update_xaxes(gridcolor=grid_color, tickmode="linear")
                fig_auth_trend.update_yaxes(title_text="Annual Papers", secondary_y=False, gridcolor=grid_color)
                fig_auth_trend.update_yaxes(title_text="Citations", secondary_y=True, showgrid=False)
                
                st.plotly_chart(fig_auth_trend, use_container_width=True)
            else:
                st.info("No timeline data available for author.")

        with c_ch2:
            q_dist = auth_profile.get("quartile_dist", {})
            if q_dist:
                df_q_auth = pd.DataFrame(list(q_dist.items()), columns=["quartile", "count"])
                color_map = {"Q1": "#10B981", "Q2": "#3B82F6", "Q3": "#F59E0B", "Q4": "#EF4444"}
                fig_q_auth = px.pie(
                    df_q_auth,
                    names="quartile",
                    values="count",
                    hole=0.55,
                    color="quartile",
                    color_discrete_map=color_map,
                    title=f"<b>Quartile Breakdown: {selected_author}</b>"
                )
                fig_q_auth.update_layout(
                    template=plot_template,
                    plot_bgcolor=plot_bg,
                    paper_bgcolor=paper_bg,
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=320,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_q_auth, use_container_width=True)

        st.markdown("##### 🏆 Top 5 Landmark Contributions")
        if not author_papers_df.empty:
            for idx, r in author_papers_df.head(5).iterrows():
                doi = r.get("doi", "")
                doi_link = f"[{doi}](https://doi.org/{doi}) ↗" if doi else "N/A"
                st.markdown(
                    f"""
                    <div style="background: rgba(14, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
                        <div style="font-weight: 600; font-size: 14px; color: #F1F5F9;">{r.get('title', '')}</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                            <i>{r.get('journal', '')}</i> ({r.get('year', '')}) • 
                            <span style="color: #F59E0B; font-weight: 700;">{r.get('citations', 0)} Citations</span> • 
                            <span style="color: #10B981; font-weight: 600;">{r.get('quartile', 'N/A')}</span> • 
                            DOI: {doi_link}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with st.expander(f"📚 View All {len(author_papers_df)} Indexed Publications for {selected_author}", expanded=False):
            if not author_papers_df.empty:
                display_cols = ["title", "journal", "year", "citations", "quartile", "doi"]
                st.dataframe(
                    author_papers_df[display_cols].rename(columns={
                        "title": "Document Title",
                        "journal": "Journal / Venue",
                        "year": "Year",
                        "citations": "Citations",
                        "quartile": "Quartile",
                        "doi": "DOI"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_d1, col_d2 = st.columns([6, 6])
        with col_d1:
            st.download_button(
                label=f"📥 Download Offline Dossier ({selected_author})",
                data=print_html,
                file_name=f"RTMNU_Dossier_{selected_author.replace(' ', '_').replace(',', '')}.html",
                mime="text/html",
                use_container_width=True
            )
        with col_d2:
            with st.expander("👁️ Preview Print Dossier Live"):
                components.html(print_html, height=450, scrolling=True)

# =========================================================
# TAB 6: LIVE FEED & FILTERABLE RESEARCH CATALOG
# =========================================================
with tab6:
    st.markdown("#### 📡 Scopus Indexed Publications Live Feed & Catalog")
    
    feed_col1, feed_col2, feed_col3, feed_col4 = st.columns([3, 3, 3, 3])
    
    with feed_col1:
        excel_buffer_tab6 = io.BytesIO()
        with pd.ExcelWriter(excel_buffer_tab6, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name="RTMNU Scopus")
        st.download_button(
            label="📊 Export Excel (.xlsx)",
            data=excel_buffer_tab6.getvalue(),
            file_name="RTMNU_Scopus_Live_Feed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with feed_col2:
        bibtex_str_tab6 = export_to_bibtex(df_filtered)
        st.download_button(
            label="📑 Export BibTeX (.bib)",
            data=bibtex_str_tab6,
            file_name="RTMNU_Scopus_Live_Feed.bib",
            mime="text/plain",
            use_container_width=True
        )
        
    with feed_col3:
        csv_data_tab6 = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Export CSV (.csv)",
            data=csv_data_tab6,
            file_name="RTMNU_Scopus_Live_Feed.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with feed_col4:
        feed_search = st.text_input("🔎 Search Feed", placeholder="Search title, author, DOI...", label_visibility="collapsed")
    
    df_feed_display = df_filtered.copy()
    if feed_search and feed_search.strip():
        q = feed_search.strip().lower()
        m = (
            df_feed_display["title"].astype(str).str.lower().str.contains(q, na=False) |
            df_feed_display["authors"].astype(str).str.lower().str.contains(q, na=False) |
            df_feed_display["journal"].astype(str).str.lower().str.contains(q, na=False) |
            df_feed_display["department"].astype(str).str.lower().str.contains(q, na=False) |
            df_feed_display["doi"].astype(str).str.lower().str.contains(q, na=False)
        )
        df_feed_display = df_feed_display[m]
        
    st.markdown(f"**Showing `{len(df_feed_display):,}` of `{len(df_filtered):,}` filtered documents**")
    
    if not df_feed_display.empty:
        df_show = df_feed_display.copy()
        df_show["DOI"] = df_show.apply(lambda r: f"[{r['doi']}](https://doi.org/{r['doi']}) ↗" if pd.notnull(r.get('doi')) and str(r.get('doi')).startswith('10.') else "N/A", axis=1)
        
        display_cols = ["title", "primary_author", "department", "journal", "year", "citations", "quartile", "document_type", "DOI"]
        avail_cols = [c for c in display_cols if c in df_show.columns]
        
        st.dataframe(
            df_show[avail_cols].rename(columns={
                "title": "Document Title",
                "primary_author": "Lead Author",
                "department": "Department",
                "journal": "Journal / Venue",
                "year": "Year",
                "citations": "Citations",
                "quartile": "Quartile",
                "document_type": "Type",
                "DOI": "DOI Link"
            }),
            use_container_width=True,
            hide_index=True,
            height=540
        )
    else:
        st.info("No documents match current filters or feed search terms.")

# =========================================================
# TAB 7: AI RESEARCH COPILOT
# =========================================================
with tab7:
    st.markdown("#### 🤖 RTMNU AI Research Intelligence Copilot")
    st.caption("Fast built-in Python/Pandas natural language assistant • Zero external API dependencies • Instant execution")
    
    if "copilot_messages" not in st.session_state:
        st.session_state["copilot_messages"] = [
            {
                "role": "assistant",
                "content": "👋 **Welcome to the RTMNU Scopus Intelligence Copilot!**\n\nI can analyze publication volumes, department benchmarks, Q1 journal quality, author leaderboards, citations, and collaboration trends. Select a prompt chip below or type your question!"
            }
        ]
        
    chip_col1, chip_col2, chip_col3, chip_col4, chip_col5 = st.columns([3, 3, 3, 3, 2])
    
    selected_chip = None
    with chip_col1:
        if st.button("📊 Executive Dossier", use_container_width=True):
            selected_chip = "Executive Dossier"
    with chip_col2:
        if st.button("🏛 Dept Rankings", use_container_width=True):
            selected_chip = "Dept Rankings"
    with chip_col3:
        if st.button("🏆 Q1 Quality Analysis", use_container_width=True):
            selected_chip = "Q1 Quality Analysis"
    with chip_col4:
        if st.button("👥 Top Authors", use_container_width=True):
            selected_chip = "Top Authors"
    with chip_col5:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state["copilot_messages"] = [
                {
                    "role": "assistant",
                    "content": "Chat history cleared. How can I help you analyze RTMNU research output?"
                }
            ]
            st.rerun()

    for msg in st.session_state["copilot_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    user_prompt = st.chat_input("Ask anything about RTMNU Scopus publications, authors, citations, or trends...")
    
    prompt_to_run = selected_chip or user_prompt
    
    if prompt_to_run:
        st.session_state["copilot_messages"].append({"role": "user", "content": prompt_to_run})
        
        with st.spinner("Analyzing Scopus dataset..."):
            response_text = answer_custom_query(prompt_to_run, df_filtered)
            
        st.session_state["copilot_messages"].append({"role": "assistant", "content": response_text})
        st.rerun()

# ---------------------------------------------------------
# Global Data Export Section
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 📥 Research Data & BibTeX Export Suite")

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Export Filtered Dataset (CSV)",
        data=csv_data,
        file_name="RTMNU_Scopus_Publications.csv",
        mime="text/csv",
        use_container_width=True
    )

with exp_col2:
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="RTMNU Scopus")
    st.download_button(
        label="📊 Export to Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="RTMNU_Scopus_Publications.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with exp_col3:
    bibtex_str = export_to_bibtex(df_filtered)
    st.download_button(
        label="📚 Export Citation Library (BibTeX)",
        data=bibtex_str,
        file_name="RTMNU_Scopus_Library.bib",
        mime="text/plain",
        use_container_width=True
    )

# ---------------------------------------------------------
# Centenary University Footer
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="icare-footer">
        <b>{UNIVERSITY_CONFIG['full_name']}</b> • Centenary State University (Estd. 1923)<br>
        NIRF ID: <b>{UNIVERSITY_CONFIG.get('nirf_id', 'IR-P-U-0332')}</b> • Scopus Affiliation ID: <b>60028250</b> • NAAC A Grade<br>
        Powered by <b>ICARE Research Intelligence Portal</b> • Elsevier Scopus Search API
    </div>
    """,
    unsafe_allow_html=True
)
