"""
RTMNU Scopus Dashboard - Institutional Configuration
Rashtrasant Tukadoji Maharaj Nagpur University (Estd. 1923)
NIRF ID: IR-O-U-0320 | Scopus AF-ID: 60015668 | NAAC A+ (CGPA 3.32)
"""

UNIVERSITY_CONFIG = {
    "full_name": "Rashtrasant Tukadoji Maharaj Nagpur University",
    "short_name": "RTMNU",
    "city": "Nagpur, Maharashtra",
    "status_tag": "🏛 Centenary State University (Estd. 1923)",
    "nirf_id": "IR-O-U-0320",
    "scopus_af_id": "60015668",
    "naac_badge": "⭐ NAAC A+ (CGPA 3.32)",
    "scopus_query": "AF-ID(60015668) OR AFFIL({Rashtrasant Tukadoji Maharaj Nagpur University}) OR AFFIL({Nagpur University}) OR AFFIL({RTMNU}) OR AFFIL({RTM Nagpur University})",
    "cache_file": "data/rtmnu_scopus_cache.json",
    "cache_ttl_seconds": 3600,  # Auto-refresh Scopus cache every 60 minutes
    "app_title": "RTMNU Live Scopus Intelligence Dashboard",
    "primary_color": "#0284C7",
    "accent_color": "#F59E0B"
}
