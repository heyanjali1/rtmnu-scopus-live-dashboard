"""
RTMNU Scopus Intelligence Dashboard - Scopus Search API Integration
Rashtrasant Tukadoji Maharaj Nagpur University (Estd. 1923) | NIRF: IR-O-U-0320 | Scopus AF-ID: 60015668
Handles live connectivity, multi-variant institutional querying, cursor pagination,
field extraction, journal ranking enrichment, local JSON caching, and auto-sync.
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Any, Optional, Tuple
import requests
import pandas as pd
from dotenv import load_dotenv

from config import UNIVERSITY_CONFIG
from mock_data import generate_mock_publications, seed_mock_cache_if_missing

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SCOPUS_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

# Known RTMNU department keyword mappings for affiliation & subject tagging
DEPT_KEYWORDS = {
    "Department of Pharmaceutical Sciences (UDPS)": [
        "pharm", "medicinal", "drug", "pharmacology", "pharmacognosy", "pharmaceutics", "udps"
    ],
    "Laxminarayan Institute of Technology (LIT / UDCT)": [
        "laxminarayan", "lit", "chemical technology", "udct", "polymer", "food tech", "oil tech", "petrochemical"
    ],
    "Department of Physics": [
        "physics", "nanomaterial", "condensed matter", "optics", "dielectric", "ferrite", "phosphor", "thin film"
    ],
    "Department of Chemistry": [
        "chemistry", "chemical", "synthesis", "spectroscopy", "organic", "inorganic", "coordination", "catalysis"
    ],
    "Department of Biotechnology": [
        "biotech", "genetic", "crispr", "molecular biology", "recombinant", "bioengineering"
    ],
    "Department of Biochemistry": [
        "biochem", "protein", "enzyme", "metabolism", "assay"
    ],
    "Department of Microbiology": [
        "microbiol", "bacteria", "fungal", "fermentation", "antimicrobial", "pathogen"
    ],
    "Department of Botany": [
        "botany", "plant", "flora", "herbal", "phytochem", "medicinal plant", "ethnobotany"
    ],
    "Department of Zoology": [
        "zoology", "animal", "aquaculture", "toxicology", "fishery", "entomology"
    ],
    "Department of Computer Science & IT": [
        "computer", "machine learning", "deep learning", "neural", "iot", "cloud", "artificial intelligence", "data science", "algorithm"
    ],
    "Department of Mathematics": [
        "mathematics", "differential equation", "metric space", "numerical", "fractional calculus"
    ],
    "Department of Geology & Earth Sciences": [
        "geology", "earth science", "hydrogeochem", "petrology", "mineral", "deccan basalt", "tectonic"
    ],
    "Department of Environmental Science": [
        "environment", "pollution", "wastewater", "ecological", "effluent", "bioremediation", "heavy metal"
    ],
    "Department of Electronics Engineering": [
        "electronics", "vlsi", "embedded", "signal processing", "telecom", "antenna", "sensor"
    ],
    "Department of Mechanical Engineering": [
        "mechanical", "thermal", "machining", "heat transfer", "vibration", "cad/cam", "tribology"
    ],
    "Department of Civil Engineering": [
        "civil", "concrete", "structural", "geotechnical", "hydrology", "seismic"
    ],
    "Department of Business Management": [
        "management", "business", "fintech", "supply chain", "marketing", "esg", "consumer"
    ],
    "Department of Commerce & Economics": [
        "commerce", "economics", "finance", "socio-economic", "banking", "econometrics"
    ]
}

# Industry indicators for collaboration analysis
INDUSTRY_INDICATORS = [
    "ltd", "limited", "corp", "inc", "gmbh", "pharma", "biotech", "industries",
    "laboratories", "research center", "innovation centre", "therapeutics", "technologies"
]


def infer_department(text: str, default_dept: str = "Department of Physics") -> Tuple[str, str]:
    """Infers the academic department and broad subject category based on text clues."""
    lower_text = text.lower()
    for dept, keywords in DEPT_KEYWORDS.items():
        if any(k in lower_text for k in keywords):
            if "Pharm" in dept:
                return dept, "Pharmacy & Health Sciences"
            elif "LIT" in dept or "Chemical Tech" in dept:
                return dept, "Chemical Technology & Engineering"
            elif "Physics" in dept:
                return dept, "Physical Sciences"
            elif "Chemistry" in dept:
                return dept, "Chemical Sciences"
            elif "Computer" in dept:
                return dept, "Computer Science & Engineering"
            elif "Math" in dept:
                return dept, "Mathematical Sciences"
            elif "Geology" in dept or "Environment" in dept:
                return dept, "Earth & Environmental Sciences"
            elif "Engineering" in dept:
                return dept, "Engineering"
            elif "Management" in dept:
                return dept, "Management & Commerce"
            elif "Commerce" in dept or "Economics" in dept:
                return dept, "Social Sciences & Humanities"
            else:
                return dept, "Life Sciences"
    return default_dept, "Physical Sciences"


def estimate_journal_metrics(journal_name: str, citations: int, year: int) -> Tuple[float, float, str]:
    """
    Estimates CiteScore, SJR, and Quartile (Q1-Q4) when not directly supplied in the raw search response.
    Uses journal title heuristics and citation velocity.
    """
    j_lower = journal_name.lower()
    age = max(1, 2026 - year + 1)
    cpa = citations / age  # citations per year

    if any(top in j_lower for top in ["nature", "science", "acs nano", "jacs", "chemical engineering journal", "applied soft computing", "expert systems", "biotechnology advances"]):
        citescore = round(max(15.0, cpa * 1.5 + 8.0), 1)
        sjr = round(max(2.5, citescore * 0.16), 2)
        quartile = "Q1"
    elif any(q1 in j_lower for q1 in ["ieee", "elsevier", "springer", "rsc advances", "bioorganic", "sensors and actuators", "materials science", "chemosphere", "journal of cleaner"]):
        citescore = round(max(6.5, cpa * 1.2 + 4.0), 1)
        sjr = round(max(0.95, citescore * 0.14), 2)
        quartile = "Q1"
    elif any(q2 in j_lower for q2 in ["letters", "proceedings", "applied", "bulletin", "current", "optical"]):
        citescore = round(max(4.0, cpa * 0.9 + 2.5), 1)
        sjr = round(max(0.55, citescore * 0.12), 2)
        quartile = "Q2"
    elif any(q3 in j_lower for q3 in ["indian journal", "asian journal", "society", "pure & applied"]):
        citescore = round(max(1.5, cpa * 0.6 + 1.0), 1)
        sjr = round(max(0.25, citescore * 0.10), 2)
        quartile = "Q3"
    else:
        # Based on citation velocity
        if cpa >= 5:
            citescore = round(cpa * 1.3, 1)
            sjr = round(citescore * 0.14, 2)
            quartile = "Q1"
        elif cpa >= 2.5:
            citescore = round(cpa * 1.1 + 1.5, 1)
            sjr = round(citescore * 0.12, 2)
            quartile = "Q2"
        elif cpa >= 1.0:
            citescore = round(cpa * 0.9 + 0.8, 1)
            sjr = round(citescore * 0.10, 2)
            quartile = "Q3"
        else:
            citescore = 1.2
            sjr = 0.18
            quartile = "Q4"

    return citescore, sjr, quartile


class ScopusAPIClient:
    """Elsevier Scopus API connector with cursor pagination and response normalization."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY", "").strip(' "[]')
        self.headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self.api_key,
            "User-Agent": "RTMNU-Live-Scopus-Dashboard/1.0"
        }

    def is_configured(self) -> bool:
        """Returns True if API key is present."""
        return bool(self.api_key and len(self.api_key) >= 16)

    def fetch_all_documents(
        self,
        query: Optional[str] = None,
        count_per_page: int = 25,
        max_records: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes cursor pagination query to Elsevier Scopus API to retrieve indexed documents.
        """
        if not self.is_configured():
            raise ValueError("Scopus API Key is not configured or invalid in .env")

        query = query or UNIVERSITY_CONFIG.get("scopus_query")
        logger.info(f"Connecting to Scopus API with query: {query}")

        records: List[Dict[str, Any]] = []
        cursor = "*"
        page_num = 1
        total_results = None

        while True:
            params = {
                "query": query,
                "count": count_per_page,
                "cursor": cursor,
                "view": "COMPLETE",
                "httpAccept": "application/json"
            }

            try:
                response = requests.get(
                    SCOPUS_SEARCH_URL,
                    headers=self.headers,
                    params=params,
                    timeout=25
                )

                if response.status_code == 401 or response.status_code == 403:
                    logger.error(f"Scopus API Authentication error {response.status_code}: {response.text}")
                    raise PermissionError(f"Scopus API Key unauthorized ({response.status_code}). Check subscription or key.")
                
                if response.status_code == 429:
                    logger.warning("Scopus API Rate Limit exceeded (429).")
                    break

                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Error making Scopus API request: {e}")
                raise

            search_results = data.get("search-results", {})
            if total_results is None:
                total_results = int(search_results.get("opensearch:totalResults", 0))
                logger.info(f"Scopus reported {total_results} total matching documents for RTMNU.")

            entries = search_results.get("entry", [])
            if not entries:
                break

            for entry in entries:
                # Filter out error entries
                if "error" in entry:
                    continue

                parsed = self._parse_scopus_entry(entry)
                if parsed:
                    records.append(parsed)

                if max_records and len(records) >= max_records:
                    break

            if max_records and len(records) >= max_records:
                break

            # Find next cursor
            next_cursor = None
            # Check cursor object in search-results
            cursor_info = search_results.get("cursor", {})
            if isinstance(cursor_info, dict):
                next_cursor = cursor_info.get("@next")

            # Check links for next rel
            if not next_cursor:
                links = search_results.get("link", [])
                for link in links:
                    if link.get("@ref") == "next":
                        href = link.get("@href", "")
                        if "cursor=" in href:
                            next_cursor = href.split("cursor=")[-1].split("&")[0]

            if not next_cursor or next_cursor == cursor:
                break

            cursor = next_cursor
            page_num += 1
            # Respect Scopus rate limit
            time.sleep(0.15)

        meta = {
            "total_found_in_api": total_results,
            "total_extracted": len(records),
            "pages_fetched": page_num,
            "synced_at": datetime.datetime.now().isoformat()
        }
        return records, meta

    def _parse_scopus_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts and normalizes all fields from a Scopus Search API JSON entry."""
        title = entry.get("dc:title", "Untitled Document")
        primary_author = entry.get("dc:creator", "Unknown Author")
        journal = entry.get("prism:publicationName", "Unknown Journal / Source")
        cover_date = entry.get("prism:coverDate", "")
        year_val = int(cover_date[:4]) if cover_date and len(cover_date) >= 4 and cover_date[:4].isdigit() else datetime.date.today().year
        citations = int(entry.get("citedby-count", 0))
        doi = entry.get("prism:doi", "")
        scopus_id = entry.get("dc:identifier", entry.get("eid", ""))

        # Authors string
        authors = primary_author
        author_list = entry.get("author", [])
        if isinstance(author_list, list) and len(author_list) > 0:
            names = [a.get("authname", a.get("given-name", "") + " " + a.get("surname", "")).strip() for a in author_list if isinstance(a, dict)]
            names = [n for n in names if n]
            if names:
                authors = ", ".join(names)
                primary_author = names[0]

        # Affiliations and countries
        affils = entry.get("affiliation", [])
        countries = set(["India"])
        has_intl = False
        has_industry = False
        affil_texts = []

        if isinstance(affils, list):
            for aff in affils:
                if isinstance(aff, dict):
                    affil_name = aff.get("affilname", "")
                    affil_city = aff.get("affiliation-city", "")
                    affil_country = aff.get("affiliation-country", "")
                    if affil_country and affil_country.lower() != "india":
                        countries.add(affil_country)
                        has_intl = True
                    affil_texts.append(f"{affil_name} {affil_city} {affil_country}")
                    # Check industry keywords
                    if any(ind in affil_name.lower() for ind in INDUSTRY_INDICATORS):
                        has_industry = True
        elif isinstance(affils, dict):
            c = affils.get("affiliation-country", "")
            if c and c.lower() != "india":
                countries.add(c)
                has_intl = True

        combined_text = f"{title} {journal} {' '.join(affil_texts)}"
        dept_name, category = infer_department(combined_text)

        # Estimate metrics
        citescore, sjr, quartile = estimate_journal_metrics(journal, citations, year_val)

        return {
            "scopus_id": scopus_id,
            "title": title,
            "authors": authors,
            "primary_author": primary_author,
            "department": dept_name,
            "category": category,
            "journal": journal,
            "year": year_val,
            "citations": citations,
            "citescore": citescore,
            "sjr": sjr,
            "quartile": quartile,
            "doi": doi,
            "document_type": entry.get("subtypeDescription", "Article"),
            "open_access": "Open Access" if entry.get("openaccessFlag") == "true" or entry.get("openaccess") == "1" else "Subscription",
            "is_international_collab": has_intl,
            "is_industry_collab": has_industry,
            "countries": list(countries),
            "affiliation": "Rashtrasant Tukadoji Maharaj Nagpur University, Nagpur, Maharashtra, India",
            "affiliation_id": "60028250"
        }


def get_rtmnu_scopus_data(
    force_refresh: bool = False,
    cache_path: Optional[str] = None,
    ttl_seconds: Optional[int] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Main entry point for loading RTMNU Scopus publications.
    Checks cache; if cache is expired (>3600s) or force_refresh is True, triggers API sync.
    Gracefully falls back to cached data or generated benchmark dataset if API is unreachable/offline.
    """
    cache_path = cache_path or UNIVERSITY_CONFIG.get("cache_file", "data/rtmnu_scopus_cache.json")
    ttl = ttl_seconds or UNIVERSITY_CONFIG.get("cache_ttl_seconds", 3600)
    client = ScopusAPIClient()

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    cache_exists = os.path.exists(cache_path)

    # 1. Check if valid fresh cache exists and force_refresh is False
    if cache_exists and not force_refresh:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            cached_time = cache_data.get("timestamp", 0)
            now = time.time()
            if (now - cached_time) < ttl:
                logger.info(f"Using fresh Scopus cache (age: {int(now - cached_time)}s / {ttl}s TTL)")
                df = pd.DataFrame(cache_data.get("data", []))
                meta = {
                    "source": cache_data.get("status", "cached"),
                    "last_synced": cache_data.get("last_synced"),
                    "total_records": len(df),
                    "cache_age_seconds": int(now - cached_time),
                    "cache_ttl": ttl
                }
                return df, meta
        except Exception as e:
            logger.warning(f"Failed to read existing cache: {e}")

    # 2. Attempt Live Sync via Scopus API
    if client.is_configured():
        try:
            logger.info("Attempting live auto-sync with Scopus API...")
            docs, sync_meta = client.fetch_all_documents()
            if docs:
                payload = {
                    "last_synced": datetime.datetime.now().isoformat(),
                    "timestamp": time.time(),
                    "status": "live_scopus_api",
                    "total_records": len(docs),
                    "query_used": UNIVERSITY_CONFIG.get("scopus_query"),
                    "data": docs
                }
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                df = pd.DataFrame(docs)
                meta = {
                    "source": "live_scopus_api",
                    "last_synced": payload["last_synced"],
                    "total_records": len(df),
                    "cache_age_seconds": 0,
                    "cache_ttl": ttl
                }
                logger.info(f"Scopus Live Sync successful: cached {len(df)} records.")
                return df, meta
        except Exception as api_err:
            logger.warning(f"Live Scopus API call could not be completed ({api_err}). Falling back to cached benchmark.")

    # 3. Fallback to existing cache if available
    if cache_exists:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            df = pd.DataFrame(cache_data.get("data", []))
            meta = {
                "source": f"{cache_data.get('status', 'cached')}_fallback",
                "last_synced": cache_data.get("last_synced"),
                "total_records": len(df),
                "cache_age_seconds": int(time.time() - cache_data.get("timestamp", 0)),
                "cache_ttl": ttl
            }
            return df, meta
        except Exception as e:
            logger.error(f"Error reading cache during fallback: {e}")

    # 4. Fallback to generating 2,500 realistic benchmark publications for RTMNU
    logger.info("Seeding realistic 2,500 publication benchmark dataset for RTMNU offline mode.")
    cache_payload = seed_mock_cache_if_missing(cache_path, count=2500)
    df = pd.DataFrame(cache_payload.get("data", []))
    meta = {
        "source": "benchmark_mock",
        "last_synced": cache_payload.get("last_synced"),
        "total_records": len(df),
        "cache_age_seconds": 0,
        "cache_ttl": ttl
    }
    return df, meta


if __name__ == "__main__":
    df, meta = get_rtmnu_scopus_data(force_refresh=True)
    print(f"Data Source: {meta['source']}")
    print(f"Total Publications: {len(df)}")
    print(df.head(2))
