"""
RTMNU Scopus Dashboard - ICARE Design System & Glassmorphism Styles
Provides Dark/Light theme switching, glassmorphic UI tokens, topbar navigation,
and university hero banner.
"""

from typing import Dict, Any, Optional
from config import UNIVERSITY_CONFIG


def get_custom_css(theme: str = "dark") -> str:
    """
    Returns custom CSS for ICARE glassmorphic design system supporting both Dark and Light themes.
    """
    is_dark = (theme.lower() == "dark")

    # Theme color tokens
    bg_color = "#070D1E" if is_dark else "#F8FAFC"
    card_bg = "rgba(14, 23, 42, 0.75)" if is_dark else "rgba(255, 255, 255, 0.88)"
    card_solid = "#0E172A" if is_dark else "#FFFFFF"
    card_border = "1px solid rgba(255, 255, 255, 0.08)" if is_dark else "1px solid rgba(0, 0, 0, 0.08)"
    card_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)" if is_dark else "0 8px 32px 0 rgba(2, 132, 199, 0.08)"
    text_primary = "#F1F5F9" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"
    input_bg = "rgba(15, 23, 42, 0.6)" if is_dark else "#FFFFFF"
    input_border = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.12)"
    badge_bg = "rgba(2, 132, 199, 0.15)" if is_dark else "rgba(2, 132, 199, 0.10)"

    primary_blue = UNIVERSITY_CONFIG.get("primary_color", "#0284C7")
    gold_accent = UNIVERSITY_CONFIG.get("accent_color", "#F59E0B")
    cyan_accent = "#06B6D4"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global App Container */
    .stApp {{
        background-color: {bg_color} !important;
        background-image: {
            "radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.12) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(245, 158, 11, 0.08) 0px, transparent 50%)"
            if is_dark else
            "radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.06) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(245, 158, 11, 0.04) 0px, transparent 50%)"
        } !important;
        color: {text_primary} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Global Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        color: {text_primary} !important;
        letter-spacing: -0.02em;
    }}

    p, span, label, div {{
        color: {text_primary};
    }}

    /* Top Navigation Bar */
    .icare-topbar {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: {card_border};
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 20px;
        box-shadow: {card_shadow};
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}

    .icare-brand-group {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .icare-logo-pill {{
        background: linear-gradient(135deg, {primary_blue} 0%, #0369A1 100%);
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 16px;
        letter-spacing: 0.05em;
        padding: 6px 14px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}

    .icare-tag-cyan {{
        background: rgba(6, 182, 212, 0.15);
        color: {cyan_accent} !important;
        border: 1px solid rgba(6, 182, 212, 0.35);
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
    }}

    .icare-uni-meta {{
        font-size: 13px;
        font-weight: 600;
        color: {primary_blue} !important;
        letter-spacing: 0.02em;
    }}

    /* Hero Banner */
    .icare-hero {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: {card_border};
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}

    .icare-hero::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {primary_blue} 0%, {cyan_accent} 50%, {gold_accent} 100%);
    }}

    .badge-ribbon {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 16px;
    }}

    .icare-badge {{
        background: {badge_bg};
        color: {text_primary} !important;
        border: {card_border};
        font-size: 12px;
        font-weight: 500;
        padding: 5px 12px;
        border-radius: 30px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}

    .icare-badge-gold {{
        background: rgba(245, 158, 11, 0.15);
        color: {gold_accent} !important;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .icare-badge-blue {{
        background: rgba(2, 132, 199, 0.15);
        color: {primary_blue} !important;
        border: 1px solid rgba(2, 132, 199, 0.3);
    }}

    .hero-main-title {{
        font-size: 30px !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
        margin: 0 0 8px 0 !important;
        line-height: 1.25 !important;
    }}

    .hero-sub {{
        color: {text_secondary};
        font-size: 14px;
        margin: 0;
    }}

    .hero-stat-card {{
        background: {card_solid};
        border: {card_border};
        border-radius: 14px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}

    .hero-stat-number {{
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: {primary_blue} !important;
        line-height: 1.1;
    }}

    .hero-stat-number-gold {{
        color: {gold_accent} !important;
    }}

    .hero-stat-label {{
        font-size: 12px;
        font-weight: 500;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 16px;
        padding: 20px;
        box-shadow: {card_shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}

    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(2, 132, 199, 0.18);
        border-color: rgba(2, 132, 199, 0.35);
    }}

    .kpi-icon {{
        font-size: 22px;
        margin-bottom: 8px;
    }}

    .kpi-title {{
        font-size: 12px;
        font-weight: 600;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }}

    .kpi-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: {text_primary};
        line-height: 1.1;
        margin-bottom: 4px;
    }}

    .kpi-subtext {{
        font-size: 11px;
        color: {text_secondary};
    }}

    .kpi-delta-up {{
        color: #10B981;
        font-weight: 600;
        font-size: 11px;
    }}

    .kpi-delta-gold {{
        color: {gold_accent};
        font-weight: 600;
        font-size: 11px;
    }}

    /* Glass Container */
    .glass-container {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: {card_shadow};
    }}

    /* Streamlit Sidebar Customization */
    section[data-testid="stSidebar"] {{
        background-color: {card_solid} !important;
        border-right: {card_border} !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {text_primary} !important;
    }}

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {input_bg};
        padding: 6px;
        border-radius: 12px;
        border: {card_border};
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 18px;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 14px;
        color: {text_secondary};
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {primary_blue} !important;
        color: #FFFFFF !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {primary_blue} 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 20px !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25) !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* Dataframe styling */
    div[data-testid="stDataFrame"] {{
        border: {card_border};
        border-radius: 12px;
        overflow: hidden;
    }}

    /* Footer */
    .icare-footer {{
        text-align: center;
        padding: 24px 0;
        font-size: 12px;
        color: {text_secondary};
        border-top: {card_border};
        margin-top: 40px;
    }}
    </style>
    """


def render_icare_topbar(theme: str = "dark") -> str:
    """
    Renders the ICARE Top Navigation Bar with branding, portal intelligence badge,
    university metadata, and NIRF ID.
    """
    nirf_id = UNIVERSITY_CONFIG.get("nirf_id", "IR-P-U-0332")
    city = UNIVERSITY_CONFIG.get("city", "Nagpur, Maharashtra")
    full_name = UNIVERSITY_CONFIG.get("full_name", "Rashtrasant Tukadoji Maharaj Nagpur University")
    scopus_id = "60028250"

    html = f"""
    <div class="icare-topbar">
        <div class="icare-brand-group">
            <div class="icare-logo-pill">
                <span>⚡</span>
                <span>ICARE</span>
            </div>
            <div class="icare-tag-cyan">PORTAL INTELLIGENCE</div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 15px;">
                {full_name}
            </div>
        </div>
        <div class="icare-uni-meta">
            <b>NIRF: {nirf_id}</b> • <b>Scopus AF-ID: {scopus_id}</b> • <b>{city}</b>
        </div>
    </div>
    """
    return html


def render_icare_hero(total_pubs: int, total_cites: int, theme: str = "dark") -> str:
    """
    Renders the Hero banner with centenary university badges, NAAC A accreditation,
    NIRF university category ID, and highlight stat rank box.
    """
    full_name = UNIVERSITY_CONFIG.get("full_name", "Rashtrasant Tukadoji Maharaj Nagpur University")
    app_title = UNIVERSITY_CONFIG.get("app_title", "RTMNU Live Scopus Intelligence Dashboard")
    status_tag = UNIVERSITY_CONFIG.get("status_tag", "🏛 Centenary State University (Estd. 1923)")
    naac_badge = UNIVERSITY_CONFIG.get("naac_badge", "⭐ NAAC A (CGPA 3.01)")
    nirf_id = UNIVERSITY_CONFIG.get("nirf_id", "IR-P-U-0332")
    scopus_id = "60028250"

    html = f"""
    <div class="icare-hero">
        <div class="badge-ribbon">
            <span class="icare-badge icare-badge-gold">🏆 Scopus Research Dossier</span>
            <span class="icare-badge">{status_tag}</span>
            <span class="icare-badge icare-badge-blue">{naac_badge}</span>
            <span class="icare-badge">📜 NIRF ID: {nirf_id}</span>
            <span class="icare-badge">🔬 Scopus AF-ID: {scopus_id}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 20px;">
            <div style="flex: 1; min-width: 300px;">
                <h1 class="hero-main-title">🏛 {app_title}</h1>
                <p class="hero-sub">
                    Institutional Research Excellence & Scopus Bibliometric Intelligence for <b>{full_name}</b>.
                </p>
            </div>
            <div style="display: flex; gap: 14px;">
                <div class="hero-stat-card">
                    <div class="hero-stat-number">#{total_pubs:,}</div>
                    <div class="hero-stat-label">Scopus Indexed Output</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-number hero-stat-number-gold">{total_cites:,}</div>
                    <div class="hero-stat-label">Total Global Citations</div>
                </div>
            </div>
        </div>
    </div>
    """
    return html


def render_kpi_card(
    icon: str,
    title: str,
    value: str,
    subtext: str,
    delta: Optional[str] = None,
    delta_type: str = "up"
) -> str:
    """Helper to render a standalone glassmorphic KPI card."""
    delta_class = "kpi-delta-up" if delta_type == "up" else "kpi-delta-gold"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""

    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
        {delta_html}
    </div>
    """
