"""
RTMNU Scopus Dashboard - Benchmark Mock Publication Generator
Rashtrasant Tukadoji Maharaj Nagpur University (Estd. 1923) | NIRF: IR-O-U-0320 | Scopus AF-ID: 60015668
Generates 2,500 realistic benchmark publications for RTMNU across all departments for offline mode.
"""

import os
import json
import random
import datetime
from typing import List, Dict, Any
import pandas as pd

# List of RTMNU Departments and Academic Units
DEPARTMENTS = [
    {"name": "Department of Pharmaceutical Sciences (UDPS)", "category": "Pharmacy & Health Sciences", "weight": 18},
    {"name": "Laxminarayan Institute of Technology (LIT / UDCT)", "category": "Chemical Technology & Engineering", "weight": 16},
    {"name": "Department of Physics", "category": "Physical Sciences", "weight": 12},
    {"name": "Department of Chemistry", "category": "Chemical Sciences", "weight": 14},
    {"name": "Department of Biotechnology", "category": "Life Sciences", "weight": 7},
    {"name": "Department of Biochemistry", "category": "Life Sciences", "weight": 5},
    {"name": "Department of Microbiology", "category": "Life Sciences", "weight": 5},
    {"name": "Department of Botany", "category": "Life Sciences", "weight": 4},
    {"name": "Department of Zoology", "category": "Life Sciences", "weight": 4},
    {"name": "Department of Computer Science & IT", "category": "Computer Science & Engineering", "weight": 9},
    {"name": "Department of Mathematics", "category": "Mathematical Sciences", "weight": 4},
    {"name": "Department of Geology & Earth Sciences", "category": "Earth & Environmental Sciences", "weight": 3},
    {"name": "Department of Environmental Science", "category": "Earth & Environmental Sciences", "weight": 3},
    {"name": "Department of Electronics Engineering", "category": "Engineering", "weight": 5},
    {"name": "Department of Mechanical Engineering", "category": "Engineering", "weight": 4},
    {"name": "Department of Civil Engineering", "category": "Engineering", "weight": 3},
    {"name": "Department of Business Management", "category": "Management & Commerce", "weight": 3},
    {"name": "Department of Commerce & Economics", "category": "Social Sciences & Humanities", "weight": 2},
]

# Real Journals associated with disciplines, typical CiteScore, SJR, and Quartile
JOURNAL_CATALOG = {
    "Pharmacy & Health Sciences": [
        {"journal": "European Journal of Medicinal Chemistry", "citescore": 10.8, "sjr": 1.45, "quartile": "Q1"},
        {"journal": "Bioorganic & Medicinal Chemistry Letters", "citescore": 5.4, "sjr": 0.78, "quartile": "Q2"},
        {"journal": "International Journal of Pharmaceutics", "citescore": 9.6, "sjr": 1.32, "quartile": "Q1"},
        {"journal": "Journal of Drug Delivery Science and Technology", "citescore": 8.1, "sjr": 0.95, "quartile": "Q1"},
        {"journal": "Phytomedicine", "citescore": 12.3, "sjr": 1.68, "quartile": "Q1"},
        {"journal": "Indian Journal of Pharmaceutical Sciences", "citescore": 1.8, "sjr": 0.28, "quartile": "Q3"},
        {"journal": "Journal of Ethnopharmacology", "citescore": 9.2, "sjr": 1.25, "quartile": "Q1"},
        {"journal": "Biomedicine & Pharmacotherapy", "citescore": 11.4, "sjr": 1.55, "quartile": "Q1"},
        {"journal": "Pharmaceutics", "citescore": 7.9, "sjr": 1.05, "quartile": "Q1"},
        {"journal": "Current Pharmaceutical Design", "citescore": 4.1, "sjr": 0.65, "quartile": "Q2"},
        {"journal": "Asian Journal of Pharmaceutics", "citescore": 1.2, "sjr": 0.19, "quartile": "Q4"},
    ],
    "Chemical Technology & Engineering": [
        {"journal": "Chemical Engineering Journal", "citescore": 23.5, "sjr": 3.12, "quartile": "Q1"},
        {"journal": "Industrial & Engineering Chemistry Research", "citescore": 7.3, "sjr": 0.98, "quartile": "Q1"},
        {"journal": "Fuel", "citescore": 12.7, "sjr": 1.74, "quartile": "Q1"},
        {"journal": "Separation and Purification Technology", "citescore": 14.1, "sjr": 1.88, "quartile": "Q1"},
        {"journal": "Journal of Cleaner Production", "citescore": 18.2, "sjr": 2.35, "quartile": "Q1"},
        {"journal": "Bioresource Technology", "citescore": 19.8, "sjr": 2.65, "quartile": "Q1"},
        {"journal": "Journal of Applied Polymer Science", "citescore": 5.6, "sjr": 0.68, "quartile": "Q2"},
        {"journal": "Process Safety and Environmental Protection", "citescore": 11.2, "sjr": 1.48, "quartile": "Q1"},
        {"journal": "Indian Journal of Chemical Technology", "citescore": 1.5, "sjr": 0.24, "quartile": "Q3"},
        {"journal": "Desalination and Water Treatment", "citescore": 2.2, "sjr": 0.32, "quartile": "Q3"},
    ],
    "Physical Sciences": [
        {"journal": "Applied Physics Letters", "citescore": 6.8, "sjr": 1.15, "quartile": "Q1"},
        {"journal": "Journal of Applied Physics", "citescore": 5.2, "sjr": 0.82, "quartile": "Q2"},
        {"journal": "Materials Science and Engineering: B", "citescore": 7.4, "sjr": 0.94, "quartile": "Q2"},
        {"journal": "Sensors and Actuators B: Chemical", "citescore": 14.8, "sjr": 1.95, "quartile": "Q1"},
        {"journal": "Journal of Alloys and Compounds", "citescore": 9.8, "sjr": 1.34, "quartile": "Q1"},
        {"journal": "Ceramics International", "citescore": 8.9, "sjr": 1.21, "quartile": "Q1"},
        {"journal": "Optical Materials", "citescore": 5.9, "sjr": 0.79, "quartile": "Q2"},
        {"journal": "Physica B: Condensed Matter", "citescore": 4.6, "sjr": 0.58, "quartile": "Q2"},
        {"journal": "Indian Journal of Pure & Applied Physics", "citescore": 1.4, "sjr": 0.22, "quartile": "Q3"},
        {"journal": "Radiation Physics and Chemistry", "citescore": 5.7, "sjr": 0.72, "quartile": "Q2"},
    ],
    "Chemical Sciences": [
        {"journal": "Journal of the American Chemical Society", "citescore": 25.4, "sjr": 6.10, "quartile": "Q1"},
        {"journal": "ACS Applied Materials & Interfaces", "citescore": 15.2, "sjr": 2.20, "quartile": "Q1"},
        {"journal": "RSC Advances", "citescore": 6.9, "sjr": 0.85, "quartile": "Q1"},
        {"journal": "Tetrahedron Letters", "citescore": 4.2, "sjr": 0.62, "quartile": "Q2"},
        {"journal": "Spectrochimica Acta Part A: Molecular Biomolecular Spectroscopy", "citescore": 7.8, "sjr": 0.96, "quartile": "Q1"},
        {"journal": "Journal of Molecular Liquids", "citescore": 9.3, "sjr": 1.18, "quartile": "Q1"},
        {"journal": "New Journal of Chemistry", "citescore": 5.8, "sjr": 0.74, "quartile": "Q2"},
        {"journal": "Synthetic Communications", "citescore": 3.4, "sjr": 0.44, "quartile": "Q3"},
        {"journal": "Journal of the Indian Chemical Society", "citescore": 1.7, "sjr": 0.25, "quartile": "Q3"},
        {"journal": "Journal of Coordination Chemistry", "citescore": 3.1, "sjr": 0.41, "quartile": "Q3"},
    ],
    "Life Sciences": [
        {"journal": "International Journal of Biological Macromolecules", "citescore": 13.9, "sjr": 1.78, "quartile": "Q1"},
        {"journal": "Biotechnology Advances", "citescore": 28.6, "sjr": 4.15, "quartile": "Q1"},
        {"journal": "Microbiological Research", "citescore": 10.4, "sjr": 1.42, "quartile": "Q1"},
        {"journal": "Enzyme and Microbial Technology", "citescore": 7.2, "sjr": 0.98, "quartile": "Q1"},
        {"journal": "Plant Physiology and Biochemistry", "citescore": 9.1, "sjr": 1.28, "quartile": "Q1"},
        {"journal": "Aquaculture", "citescore": 7.5, "sjr": 1.10, "quartile": "Q1"},
        {"journal": "Archives of Microbiology", "citescore": 4.8, "sjr": 0.64, "quartile": "Q2"},
        {"journal": "Indian Journal of Experimental Biology", "citescore": 1.6, "sjr": 0.26, "quartile": "Q3"},
        {"journal": "Current Microbiology", "citescore": 3.9, "sjr": 0.52, "quartile": "Q2"},
        {"journal": "Journal of Pure and Applied Microbiology", "citescore": 1.3, "sjr": 0.18, "quartile": "Q4"},
    ],
    "Computer Science & Engineering": [
        {"journal": "IEEE Transactions on Neural Networks and Learning Systems", "citescore": 21.2, "sjr": 3.85, "quartile": "Q1"},
        {"journal": "Expert Systems with Applications", "citescore": 16.4, "sjr": 2.15, "quartile": "Q1"},
        {"journal": "Applied Soft Computing", "citescore": 14.3, "sjr": 1.92, "quartile": "Q1"},
        {"journal": "Computers & Security", "citescore": 10.2, "sjr": 1.38, "quartile": "Q1"},
        {"journal": "IEEE Access", "citescore": 7.4, "sjr": 0.92, "quartile": "Q1"},
        {"journal": "Neural Computing and Applications", "citescore": 8.7, "sjr": 1.14, "quartile": "Q1"},
        {"journal": "Pattern Recognition Letters", "citescore": 8.0, "sjr": 1.05, "quartile": "Q2"},
        {"journal": "Multimedia Tools and Applications", "citescore": 5.9, "sjr": 0.74, "quartile": "Q2"},
        {"journal": "Concurrency and Computation: Practice and Experience", "citescore": 3.8, "sjr": 0.48, "quartile": "Q3"},
        {"journal": "International Journal of Information Technology", "citescore": 2.4, "sjr": 0.31, "quartile": "Q3"},
    ],
    "Mathematical Sciences": [
        {"journal": "Applied Mathematics and Computation", "citescore": 8.3, "sjr": 1.12, "quartile": "Q1"},
        {"journal": "Journal of Mathematical Analysis and Applications", "citescore": 3.2, "sjr": 0.89, "quartile": "Q1"},
        {"journal": "Nonlinear Analysis: Real World Applications", "citescore": 6.1, "sjr": 1.24, "quartile": "Q1"},
        {"journal": "Communications in Nonlinear Science and Numerical Simulation", "citescore": 7.5, "sjr": 1.18, "quartile": "Q1"},
        {"journal": "Filomat", "citescore": 1.8, "sjr": 0.42, "quartile": "Q2"},
        {"journal": "Indian Journal of Pure and Applied Mathematics", "citescore": 1.1, "sjr": 0.27, "quartile": "Q3"},
    ],
    "Earth & Environmental Sciences": [
        {"journal": "Science of The Total Environment", "citescore": 16.5, "sjr": 2.18, "quartile": "Q1"},
        {"journal": "Chemosphere", "citescore": 14.7, "sjr": 1.95, "quartile": "Q1"},
        {"journal": "Environmental Pollution", "citescore": 15.1, "sjr": 2.05, "quartile": "Q1"},
        {"journal": "Journal of Environmental Management", "citescore": 13.8, "sjr": 1.82, "quartile": "Q1"},
        {"journal": "Environmental Science and Pollution Research", "citescore": 8.4, "sjr": 1.08, "quartile": "Q1"},
        {"journal": "Journal of the Geological Society of India", "citescore": 2.5, "sjr": 0.38, "quartile": "Q3"},
        {"journal": "Arabian Journal of Geosciences", "citescore": 3.2, "sjr": 0.44, "quartile": "Q3"},
    ],
    "Engineering": [
        {"journal": "Mechanical Systems and Signal Processing", "citescore": 16.9, "sjr": 2.45, "quartile": "Q1"},
        {"journal": "Renewable and Sustainable Energy Reviews", "citescore": 32.4, "sjr": 4.80, "quartile": "Q1"},
        {"journal": "Energy", "citescore": 14.9, "sjr": 2.10, "quartile": "Q1"},
        {"journal": "Materials Today: Proceedings", "citescore": 3.5, "sjr": 0.45, "quartile": "Q2"},
        {"journal": "Measurement", "citescore": 9.8, "sjr": 1.35, "quartile": "Q1"},
        {"journal": "Engineering Science and Technology, an International Journal", "citescore": 8.9, "sjr": 1.15, "quartile": "Q1"},
        {"journal": "Sadhana - Academy Proceedings in Engineering Sciences", "citescore": 2.8, "sjr": 0.39, "quartile": "Q3"},
    ],
    "Management & Commerce": [
        {"journal": "Journal of Business Research", "citescore": 18.5, "sjr": 2.85, "quartile": "Q1"},
        {"journal": "Technological Forecasting and Social Change", "citescore": 19.2, "sjr": 3.10, "quartile": "Q1"},
        {"journal": "International Journal of Production Economics", "citescore": 17.6, "sjr": 2.70, "quartile": "Q1"},
        {"journal": "Benchmarking: An International Journal", "citescore": 7.4, "sjr": 0.98, "quartile": "Q1"},
        {"journal": "Vikalpa: The Journal for Decision Makers", "citescore": 2.1, "sjr": 0.35, "quartile": "Q3"},
    ],
    "Social Sciences & Humanities": [
        {"journal": "Telematics and Informatics", "citescore": 13.2, "sjr": 1.95, "quartile": "Q1"},
        {"journal": "Economic and Political Weekly", "citescore": 1.1, "sjr": 0.22, "quartile": "Q3"},
        {"journal": "Heliyon", "citescore": 6.2, "sjr": 0.82, "quartile": "Q1"},
        {"journal": "Social Science & Medicine", "citescore": 8.9, "sjr": 1.62, "quartile": "Q1"},
    ]
}

# RTMNU Faculty & Researchers Names Pool
FACULTY_NAMES = [
    "Deshmukh, S.A.", "Sharma, P.K.", "Patil, V.R.", "Meshram, S.U.", "Bhadange, S.G.",
    "Kulkarni, M.S.", "Ghate, P.V.", "Wankhade, A.V.", "Thakur, S.D.", "Jadhav, R.K.",
    "Raut, R.W.", "Choudhary, R.B.", "Dumbre, D.K.", "Mahajan, P.G.", "Gawande, M.B.",
    "Kharat, P.B.", "Tupte, S.R.", "Bonde, C.G.", "Zade, S.B.", "Khobragade, B.G.",
    "Ingle, N.A.", "Dorle, A.K.", "Umathe, S.N.", "Mundhada, D.R.", "Chopde, C.T.",
    "Nandekar, S.S.", "Kashikar, S.G.", "Bodhankar, M.M.", "Pardhi, V.P.", "Gedam, R.S.",
    "Dhopte, P.R.", "Nandanwar, D.V.", "Joshi, P.B.", "Pethe, A.S.", "Bobde, R.S.",
    "Sawarkar, A.N.", "Wasewar, K.L.", "Pandey, A.K.", "Tembhurne, S.V.", "Kotwal, P.C.",
    "Shukla, S.K.", "Ghate, S.D.", "Meshram, J.S.", "Deshpande, V.K.", "Kalam, A.A.",
    "Umare, S.S.", "Kanoo, P.", "Mukhopadhyay, S.", "Sasmal, P.K.", "Bansod, S.M."
]

EXTERNAL_AUTHORS = [
    "Smith, J.R.", "Müller, H.K.", "Tanaka, K.", "Wang, Y.", "Zhang, L.",
    "Kim, D.H.", "Al-Ghamdi, A.A.", "Johnson, M.E.", "García, C.M.", "Dupont, P.",
    "Nakamura, H.", "Chen, X.", "Gupta, V.K.", "Kumar, A.", "Singh, R.P.",
    "Patel, H.N.", "Verma, S.K.", "Roy, P.C.", "Srivastava, R.", "Nair, C.K."
]

# Collaborating Countries
COLLABORATING_COUNTRIES = [
    "United States", "Germany", "United Kingdom", "Japan", "South Korea",
    "Australia", "Saudi Arabia", "France", "Canada", "Singapore",
    "Taiwan", "Malaysia", "Italy", "China", "Spain", "Brazil", "South Africa"
]

# Collaborating Industry Partners
INDUSTRY_PARTNERS = [
    "Sun Pharmaceutical Industries Ltd", "Cipla R&D Centre", "Lupin Research Park",
    "Reliance Industries Ltd", "Tata Chemicals Innovation Centre", "Dr. Reddy's Laboratories",
    "Pfizer Global R&D", "Intel Labs", "IBM Research", "Novartis Pharma AG",
    "Mahindra Research Valley", "Aurobindo Pharma", "Thermax Ltd"
]

# Title generation templates
TOPIC_TEMPLATES = {
    "Pharmacy & Health Sciences": [
        "Formulation, optimization and pharmacokinetic evaluation of {nanocarrier} loaded with {drug_name} for targeted cancer therapy",
        "Design, synthesis, and molecular docking studies of novel {chemical_core} derivatives as potent anti-inflammatory agents",
        "Phytochemical profiling, antioxidant, and anti-diabetic potential of medicinal flora from Vidarbha region: {plant_name}",
        "Development and validation of a stability-indicating RP-HPLC method for simultaneous estimation of {drug_name} and {drug_name}",
        "Neuroprotective efficacy of {compound} against oxidative stress-induced neurodegeneration in experimental models",
        "Self-nanoemulsifying drug delivery systems (SNEDDS) of {drug_name}: Enhanced oral bioavailability and pharmacokinetic profiling"
    ],
    "Chemical Technology & Engineering": [
        "Hydrodynamic and mass transfer characteristics in {reactor_type} for sustainable wastewater treatment",
        "Catalytic pyrolysis of biomass over modified {catalyst} for high-yield biofuel production",
        "Process intensification and optimization of {chemical_process} using response surface methodology (RSM)",
        "Adsorption of heavy metal ions from industrial effluents using functionalized biopolymers: Isotherm and kinetic modeling",
        "Synthesis of bio-based polyurethane coatings with enhanced thermal and corrosion resistance properties",
        "Supercritical fluid extraction of bioactive compounds from agro-industrial waste: Scale-up and economic analysis"
    ],
    "Physical Sciences": [
        "Synthesis and characterization of {nanomaterial} thin films for high-performance gas sensing applications",
        "Dielectric, magnetic, and optical properties of multiferroic {ceramic_type} synthesized via sol-gel auto-combustion",
        "Enhanced photocatalytic degradation of organic pollutants using {nanomaterial} under visible-light irradiation",
        "Investigation of structural and electrical transport mechanisms in transition metal-doped {oxide_material}",
        "Luminescence behavior and energy transfer mechanism in rare-earth activated {phosphor_material} for solid-state lighting"
    ],
    "Chemical Sciences": [
        "Green synthesis of functionalized {chemical_core} via multi-component reaction catalyzed by magnetic nanoparticles",
        "Electrochemical sensing of hazardous biomolecules using electrode modified with {nanomaterial} nanocomposites",
        "Crystal structure, Hirshfeld surface analysis, and DFT computational investigation of {chemical_core} complexes",
        "Fluorescent probes based on {compound} for highly selective and sensitive detection of toxic metal ions in aqueous media",
        "Novel transition-metal catalyzed C-H activation and cross-coupling methodologies for heterocycle synthesis"
    ],
    "Life Sciences": [
        "Isolation, molecular identification, and enzymatic characterization of extracellular protease from halo-tolerant {bacterium}",
        "Biochemical characterization and anti-microbial evaluation of endophytic fungi isolated from regional flora",
        "CRISPR-Cas9 mediated gene editing approaches in enhancing abiotic stress tolerance in crops",
        "Bioremediation of textile dye effluent using consortium of indigenous bacterial isolates",
        "Assessment of biodiversity and ecological indices in wetland ecosystems of Central India"
    ],
    "Computer Science & Engineering": [
        "Deep convolutional neural networks and transformer architectures for automated medical image segmentation",
        "An optimized secure blockchain-enabled framework for Internet of Things (IoT) healthcare ecosystems",
        "Hybrid meta-heuristic optimization algorithm for multi-objective cloud resource scheduling",
        "Explainable Artificial Intelligence (XAI) models for early fraud detection and cyber-threat mitigation",
        "Sentiment analysis and natural language understanding using domain-adapted multilingual BERT embeddings"
    ],
    "Mathematical Sciences": [
        "Existence and uniqueness of solutions for non-linear fractional differential equations with impulsive boundary conditions",
        "Mathematical modeling and stability analysis of epidemic spread dynamics with vaccination and quarantine delays",
        "Topological data analysis and geometric algorithms in high-dimensional manifold learning",
        "Fixed point theorems in generalized metric spaces and their applications to integral equations"
    ],
    "Earth & Environmental Sciences": [
        "Hydrogeochemical assessment and spatial distribution of groundwater quality in Central Deccan basalt terrain",
        "Spatial-temporal analysis of land use and land cover dynamics using Sentinel-2 and Landsat remote sensing imagery",
        "Heavy metal contamination indices and ecological risk assessment in urban soil and riverine sediments",
        "Geological and petrogenetic evolution of Precambrian metamorphic complexes in Central Indian Tectonic Zone"
    ],
    "Engineering": [
        "Experimental investigation of heat transfer enhancement in solar thermal collector with twisted-tape inserts",
        "Vibration and fault diagnosis in rotating machinery using wavelet packet transform and machine learning",
        "Structural health monitoring and seismic vulnerability evaluation of reinforced concrete structures",
        "Optimization of EDM machining parameters for aerospace superalloys using Taguchi-Grey relational analysis"
    ],
    "Management & Commerce": [
        "Impact of digital transformation and FinTech adoption on consumer financial well-being in emerging markets",
        "Sustainable supply chain resilience during global disruptions: An empirical structural equation modeling approach",
        "Corporate governance, ESG compliance, and firm valuation: Evidence from Indian listed enterprises"
    ],
    "Social Sciences & Humanities": [
        "Socio-economic impact of rural development programs and micro-finance initiatives in Vidarbha region",
        "Public health infrastructure, digital literacy, and health disparities: A cross-sectional analytical study"
    ]
}

# Fill-in dictionaries
FILLINS = {
    "nanocarrier": ["polymeric nanoparticles", "liposomes", "mesoporous silica", "solid lipid nanoparticles (SLNs)", "dendrimers", "nanostructured lipid carriers"],
    "drug_name": ["Paclitaxel", "Curcumin", "Metformin", "Atorvastatin", "Doxorubicin", "Quercetin", "Resveratrol", "Ciprofloxacin"],
    "chemical_core": ["1,2,4-triazole", "coumarin", "benzimidazole", "pyrazoline", "quinoline", "thiazolidinedione", "chalcone"],
    "plant_name": ["Tinospora cordifolia", "Azadirachta indica", "Ocimum sanctum", "Withania somnifera", "Terminalia arjuna"],
    "compound": ["polyphenols", "flavonoid glycosides", "chitosan derivatives", "piperine derivatives", "berberine"],
    "reactor_type": ["fluidized bed bioreactor", "microchannel reactor", "cavitation hydrodynamic reactor", "membrane contactor"],
    "catalyst": ["zeolite ZSM-5", "mesoporous SBA-15", "sulfated zirconia", "graphene oxide-supported cobalt", "TiO2/ZnO nanocomposite"],
    "chemical_process": ["biodiesel transesterification", "phenol degradation", "furfural synthesis", "esterification of levulinic acid"],
    "nanomaterial": ["ZnO-rGO", "TiO2/SnO2", "Cu2O/g-C3N4", "Fe3O4@SiO2 core-shell", "MXene/polyaniline", "MoS2 nanosheets"],
    "ceramic_type": ["BiFeO3-BaTiO3 ceramics", "lead-free KNN piezoceramics", "strontium hexaferrite nanoparticles", "yttrium iron garnet"],
    "oxide_material": ["zinc oxide nanorods", "manganese ferrite", "cerium dioxide nanocrystals", "copper oxide thin films"],
    "phosphor_material": ["Eu3+/Tb3+ co-doped aluminate phosphor", "Dy3+ activated orthosilicate phosphors", "Sm3+ doped tellurite glass"],
    "bacterium": ["Bacillus subtilis", "Pseudomonas aeruginosa", "Streptomyces sp.", "Lactobacillus plantarum", "Halomonas sp."]
}


def _fill_title(template: str) -> str:
    """Fills a template with randomized realistic scientific vocabulary."""
    title = template
    for key, values in FILLINS.items():
        placeholder = "{" + key + "}"
        while placeholder in title:
            title = title.replace(placeholder, random.choice(values), 1)
    return title


def generate_mock_publications(count: int = 2500, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generates a deterministic, highly realistic benchmark list of publications for RTMNU.
    """
    random.seed(seed)
    publications = []

    # Calculate department weights
    dept_weights = [d["weight"] for d in DEPARTMENTS]
    
    # Year distribution (2012 - 2026), heavily weighted towards recent years
    years = list(range(2012, 2027))
    year_weights = [2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 19, 21, 23, 20]  # total 15 years

    for i in range(count):
        # Select department
        dept_info = random.choices(DEPARTMENTS, weights=dept_weights, k=1)[0]
        dept_name = dept_info["name"]
        dept_category = dept_info["category"]

        # Select journal catalog based on category
        available_journals = JOURNAL_CATALOG.get(dept_category, JOURNAL_CATALOG["Physical Sciences"])
        journal_info = random.choice(available_journals)

        # Select Year
        year = random.choices(years, weights=year_weights, k=1)[0]

        # Generate Title
        templates = TOPIC_TEMPLATES.get(dept_category, TOPIC_TEMPLATES["Physical Sciences"])
        template = random.choice(templates)
        title = _fill_title(template)

        # Generate Authors
        num_authors = random.choices([2, 3, 4, 5, 6, 7], weights=[15, 30, 30, 15, 7, 3], k=1)[0]
        rtmnu_primary = random.choice(FACULTY_NAMES)
        authors_list = [rtmnu_primary]

        # Collaborations
        is_international = random.random() < 0.23  # 23% international collab
        is_industry = random.random() < 0.12       # 12% industry collab

        countries = ["India"]
        if is_international:
            collab_country = random.choice(COLLABORATING_COUNTRIES)
            countries.append(collab_country)
            # Add external co-author
            authors_list.append(random.choice(EXTERNAL_AUTHORS))

        # Add more authors
        for _ in range(num_authors - len(authors_list)):
            candidate = random.choice(FACULTY_NAMES)
            if candidate not in authors_list:
                authors_list.append(candidate)
            else:
                authors_list.append(random.choice(EXTERNAL_AUTHORS))

        # Randomize order occasionally but keep RTMNU faculty as primary or corresponding
        primary_author = authors_list[0]
        authors_str = ", ".join(authors_list)

        # Citations based on paper age and journal citescore
        age_years = max(1, 2026 - year + 1)
        base_rate = journal_info["citescore"] * 0.75
        # Lognormal citation distribution
        citation_factor = random.expovariate(1.0 / (age_years * base_rate))
        citations = min(int(citation_factor * 2.2), 650)
        # Give seminal top papers a bump
        if i % 85 == 0:
            citations = int(citations * 3.5) + random.randint(50, 200)

        # Document Type
        doc_type = random.choices(["Article", "Review", "Conference Paper", "Book Chapter"], weights=[78, 12, 8, 2], k=1)[0]

        # Open Access status
        is_oa = random.random() < 0.38
        oa_status = random.choice(["Gold Open Access", "Green Open Access", "Hybrid"]) if is_oa else "Subscription"

        # Unique IDs
        scopus_id = f"2-s2.0-85{10000000 + i}"
        doi_suffix = f"{year}.{100000 + i}"
        doi = f"10.1016/j.{dept_category[:4].lower()}.{doi_suffix}"

        pub_record = {
            "scopus_id": scopus_id,
            "title": title,
            "authors": authors_str,
            "primary_author": primary_author,
            "author_count": len(authors_list),
            "department": dept_name,
            "category": dept_category,
            "journal": journal_info["journal"],
            "year": int(year),
            "citations": int(citations),
            "citescore": float(journal_info["citescore"]),
            "sjr": float(journal_info["sjr"]),
            "quartile": journal_info["quartile"],
            "doi": doi,
            "document_type": doc_type,
            "open_access": oa_status,
            "is_international_collab": is_international,
            "is_industry_collab": is_industry,
            "countries": countries,
            "affiliation": "Rashtrasant Tukadoji Maharaj Nagpur University, Nagpur, Maharashtra, India",
            "affiliation_id": "60028250"
        }
        publications.append(pub_record)

    return publications


def get_mock_dataframe(count: int = 2500) -> pd.DataFrame:
    """Returns the benchmark dataset as a pandas DataFrame."""
    pubs = generate_mock_publications(count)
    return pd.DataFrame(pubs)


def seed_mock_cache_if_missing(cache_file_path: str = "data/rtmnu_scopus_cache.json", count: int = 2500) -> Dict[str, Any]:
    """
    Creates and populates the cache file with benchmark data if not present.
    """
    os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
    if not os.path.exists(cache_file_path):
        data = generate_mock_publications(count=count)
        payload = {
            "last_synced": datetime.datetime.now().isoformat(),
            "timestamp": datetime.datetime.now().timestamp(),
            "status": "benchmark_mock",
            "total_records": len(data),
            "query_used": "AF-ID(60028250) OR AFFIL({Rashtrasant Tukadoji Maharaj Nagpur University}) OR AFFIL({Nagpur University}) OR AFFIL({RTMNU}) OR AFFIL({RTM Nagpur University})",
            "data": data
        }
        with open(cache_file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload
    else:
        with open(cache_file_path, "r", encoding="utf-8") as f:
            return json.load(f)


if __name__ == "__main__":
    df = get_mock_dataframe(2500)
    print(f"Generated {len(df)} mock publications.")
    print("Sample record:")
    print(df.iloc[0].to_dict())
