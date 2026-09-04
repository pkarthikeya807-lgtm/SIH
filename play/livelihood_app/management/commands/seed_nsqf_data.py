"""
Django management command to seed realistic NSQF Qualification Packs (QPs),
PM-AJAY Training Centers, and baseline trade mappings.
"""

from django.core.management.base import BaseCommand
from livelihood_app.models import NSQFTrade, SkillCenter


class Command(BaseCommand):
    help = "Seeds official NSQF Qualification Packs and PM-AJAY Training Centers into the SQL database."

    def handle(self, *args, **options):
        self.stdout.write("Seeding NSQF Trade Qualification Packs...")

        trades_data = [
            {
                "qp_code": "ELE/Q3102",
                "name": "Solar PV System Installer (Suryamitra)",
                "sector": "Green Jobs & Electronics",
                "nsqf_level": 4,
                "min_education": "10th Pass",
                "wage_vs_self_score": 0.65,
                "traditional_synergy_tags": ["electrician", "metalwork", "wiring", "welder", "carpentry", "maintenance"],
                "district_demand_tags": ["rural_agritech", "urban_solar", "green_energy", "rooftop_solar", "microgrid"],
                "avg_monthly_income_inr": 22000,
                "duration_hours": 300,
                "description": "Specialized in rooftop and ground-mounted Solar PV system civil mounting, electrical wiring, inverter synchronization, and safety testing under PM Surya Ghar Muft Bijli Yojana.",
                "key_modules": ["Solar Module Mounting", "Inverter & Battery Wiring", "Earthing & Lightning Protection", "Grid Synchronization", "Safety Protocols & Work at Heights"],
                "prerequisite_skills": ["Basic Tool Handling", "Color Coding of Wires"]
            },
            {
                "qp_code": "AMH/Q1201",
                "name": "Self-Employed Tailor & Master Craftsman",
                "sector": "Apparel, Made-Ups & Home Furnishing",
                "nsqf_level": 4,
                "min_education": "8th Pass",
                "wage_vs_self_score": 0.85,
                "traditional_synergy_tags": ["handloom", "weaving", "stitching", "tailor", "silai", "garment", "embroidery"],
                "district_demand_tags": ["handloom_cluster", "textile_market", "rural_agritech", "boutique_fashion"],
                "avg_monthly_income_inr": 20000,
                "duration_hours": 340,
                "description": "Performs measuring, drafting, pattern cutting, stitching, embellishment, and boutique micro-enterprise management for bespoke garments and commercial apparel batches.",
                "key_modules": ["Garment Drafting & Cutting", "Single Needle Lockstitch Operation", "Finishing & Pressing", "Client Measurements & Custom Fitting", "Micro-enterprise Costing & Billing"],
                "prerequisite_skills": ["Hand Dexterity", "Basic Visual Estimation"]
            },
            {
                "qp_code": "ELE/Q4601",
                "name": "Field Technician - Wireman & Home Appliances",
                "sector": "Electronics & Hardware",
                "nsqf_level": 3,
                "min_education": "8th Pass",
                "wage_vs_self_score": 0.70,
                "traditional_synergy_tags": ["electrician", "repair", "blacksmith", "carpentry", "lohar"],
                "district_demand_tags": ["urban_services", "semi_urban_retail", "rural_electrification"],
                "avg_monthly_income_inr": 19000,
                "duration_hours": 360,
                "description": "Installs domestic concealed wiring, distribution boards, lighting fixtures, and repairs consumer appliances like ceiling fans, water pumps, and mixer-grinders.",
                "key_modules": ["Domestic Conduit Wiring", "Switchboard & MCB Installation", "Motor & Pump Troubleshooting", "Multimeter & Insulation Testing", "Electrical Safety Standards"],
                "prerequisite_skills": ["Basic Hand Tool Operation"]
            },
            {
                "qp_code": "ASC/Q1411",
                "name": "Automotive Service Technician (Two & Three Wheelers / EV)",
                "sector": "Automotive Skill Development Council",
                "nsqf_level": 4,
                "min_education": "10th Pass",
                "wage_vs_self_score": 0.60,
                "traditional_synergy_tags": ["mechanic", "metalwork", "blacksmith", "lohar", "repair", "lathe"],
                "district_demand_tags": ["industrial_manufacturing", "semi_urban_retail", "highway_corridor", "transport_hub"],
                "avg_monthly_income_inr": 24000,
                "duration_hours": 400,
                "description": "Performs diagnostic scanning, engine overhauling, brake servicing, suspension repair, and lithium battery motor maintenance for 2/3 wheelers and Light Electric Vehicles.",
                "key_modules": ["Engine Mechanical Overhaul", "EV Battery Pack Diagnostics", "Hydraulic Brake Servicing", "Fuel Injection & Carburetor Tuning", "Workshop Customer Relations"],
                "prerequisite_skills": ["Mechanical Aptitude"]
            },
            {
                "qp_code": "HCS/Q7303",
                "name": "Terracotta & Ceramic Artisan (PM Vishwakarma Allied)",
                "sector": "Handicrafts & Carpet Sector",
                "nsqf_level": 3,
                "min_education": "None",
                "wage_vs_self_score": 0.90,
                "traditional_synergy_tags": ["pottery", "kumhar", "clay", "ceramic", "terracotta", "sculpture", "mitti"],
                "district_demand_tags": ["handicrafts_cluster", "heritage_tourism", "rural_artisan_hub", "odop_cluster"],
                "avg_monthly_income_inr": 18500,
                "duration_hours": 280,
                "description": "Integrates traditional wheel-thrown pottery with modern electric motorized wheels, pug-mill clay refinement, temperature-controlled kilns, and non-toxic glazing for export.",
                "key_modules": ["Clay Formulation & Pugging", "Electric Wheel Centering & Throwing", "Slip Casting & Mould Making", "Modern Kiln Firing & Glazing", "E-Commerce Onboarding & Packaging"],
                "prerequisite_skills": ["Clay Hand Moulding"]
            },
            {
                "qp_code": "AGR/Q0104",
                "name": "Micro-Irrigation & Agri-Drone Technician",
                "sector": "Agriculture & Allied",
                "nsqf_level": 4,
                "min_education": "10th Pass",
                "wage_vs_self_score": 0.75,
                "traditional_synergy_tags": ["farming", "kheti", "krishi", "irrigation", "pump_repair", "tractor"],
                "district_demand_tags": ["rural_agritech", "high_yield_farming", "horticulture_belt"],
                "avg_monthly_income_inr": 23000,
                "duration_hours": 320,
                "description": "Installs automated drip/sprinkler irrigation systems, solar agricultural pumps, and operates DGCA-certified drone sprayer systems for targeted nutrient application.",
                "key_modules": ["Drip Pipe Layout & Venturi Installation", "Solar Submersible Pump Setup", "Agri-Drone Flight Protocols", "Soil Moisture Sensor Calibration", "Farmer Advisory Communication"],
                "prerequisite_skills": ["Agricultural Field Familiarity"]
            },
            {
                "qp_code": "FIC/Q0103",
                "name": "Baking & Millet Food Processing Entrepreneur",
                "sector": "Food Processing Sector",
                "nsqf_level": 3,
                "min_education": "8th Pass",
                "wage_vs_self_score": 0.80,
                "traditional_synergy_tags": ["food_prep", "halwai", "mithai", "shg", "farming", "spices"],
                "district_demand_tags": ["food_processing_park", "rural_women_shg", "urban_bakery", "millet_mission"],
                "avg_monthly_income_inr": 21000,
                "duration_hours": 300,
                "description": "Prepares fortified millet baked snacks, dehydrated fruit/spice powders, preserves, and packaged ready-to-eat items complying with FSSAI hygiene standards.",
                "key_modules": ["Millet Flour Blending & Kneading", "Convection Oven Operation", "FSSAI Food Safety & Labeling", "Vacuum Packaging & Nitrogen Flush", "SHG Group Marketing & Branding"],
                "prerequisite_skills": ["Hygiene Maintenance"]
            },
            {
                "qp_code": "CON/Q0102",
                "name": "Assistant Mason & Modern Construction Technologist",
                "sector": "Construction Skill Development Council",
                "nsqf_level": 3,
                "min_education": "5th Pass",
                "wage_vs_self_score": 0.50,
                "traditional_synergy_tags": ["masonry", "rajmistri", "construction", "cement", "bricklaying", "plaster"],
                "district_demand_tags": ["infrastructure_boom", "pmay_housing", "smart_cities", "urban_construction"],
                "avg_monthly_income_inr": 21500,
                "duration_hours": 350,
                "description": "Executes precision brickwork, AAC block masonry, reinforcement bar bending, plumb-line leveling, and water-proofing for affordable housing projects.",
                "key_modules": ["AAC Block Laying & Polymer Mortar", "Spirit Level & Laser Plummeting", "Plastering & Water Curing", "Bar Bending & Structural Shuttering", "Scaffolding Safety"],
                "prerequisite_skills": ["Physical Stamina", "Trowel Work"]
            },
            {
                "qp_code": "LSC/Q0101",
                "name": "Warehouse Logistics Associate & Inventory Clerk",
                "sector": "Logistics Sector Skill Council",
                "nsqf_level": 3,
                "min_education": "10th Pass",
                "wage_vs_self_score": 0.20,
                "traditional_synergy_tags": ["labor", "helper", "vendor", "transport", "driving"],
                "district_demand_tags": ["logistics_hub", "ecommerce_fulfillment", "highway_corridor", "urban_metro"],
                "avg_monthly_income_inr": 20000,
                "duration_hours": 290,
                "description": "Handles barcoded inventory inbound/outbound receiving, pallet racking, handheld scanner logging, and order pick-and-pack in modern fulfillment centers.",
                "key_modules": ["Barcode Scanner & WMS Data Entry", "Pallet Truck (HPT) Operation", "Hazardous Material Labeling", "Order Pick & Cycle Count", "Safe Material Handling Techniques"],
                "prerequisite_skills": ["Basic English Reading", "Physical Mobility"]
            },
            {
                "qp_code": "SSC/Q2212",
                "name": "Domestic Data Entry Operator & CSC Digital Facilitator",
                "sector": "IT-ITeS Sector Skill Council",
                "nsqf_level": 4,
                "min_education": "10th Pass",
                "wage_vs_self_score": 0.65,
                "traditional_synergy_tags": ["digital", "computer", "typing", "shopkeeper", "csc", "office"],
                "district_demand_tags": ["digital_india", "csc_center", "gram_panchayat_office", "banking_correspondent"],
                "avg_monthly_income_inr": 19500,
                "duration_hours": 400,
                "description": "Delivers e-governance services, Aadhaar/DBT registrations, bilingual typing (Indic/English), document scanning, and Common Service Centre (CSC) micro-enterprise management.",
                "key_modules": ["30 WPM Touch Typing (English/Hindi)", "Spreadsheets & Government Portals", "Biometric Scanner Interfacing", "Cyber Safety & Data Privacy", "CSC Customer Service & Cash Handling"],
                "prerequisite_skills": ["Basic Computer Familiarity"]
            }
        ]

        created_trades = {}
        for t_data in trades_data:
            trade, created = NSQFTrade.objects.update_or_create(
                qp_code=t_data["qp_code"],
                defaults=t_data
            )
            created_trades[trade.qp_code] = trade
            status_text = "Created" if created else "Updated"
            self.stdout.write(f" - {status_text} NSQF Trade: {trade.qp_code} - {trade.name}")

        self.stdout.write("Seeding PM-AJAY Skill Centers...")

        centers_data = [
            {
                "center_id": "PMAJAY-TC-UP-VNS01",
                "name": "PM-AJAY Kaushal Kendra & Vishwakarma Center - Varanasi",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "address": "Industrial Estate, Chaukaghat, Near Handloom Facilitation Centre, Varanasi - 221002",
                "contact_person": "Er. R. K. Maurya",
                "contact_phone": "+91 94152 78391",
                "contact_email": "varanasi.pmajay@gov.in",
                "latitude": 25.3280,
                "longitude": 82.9860,
                "hostel_available": True,
                "pm_ajay_funded": True,
                "trade_codes": ["ELE/Q3102", "AMH/Q1201", "HCS/Q7303", "SSC/Q2212"]
            },
            {
                "center_id": "PMAJAY-TC-DL-STH01",
                "name": "Pradhan Mantri Kaushal Vikas Kendra - South Delhi",
                "state": "Delhi",
                "district": "South Delhi",
                "address": "Okhla Industrial Area Phase-II, Near Crown Plaza, New Delhi - 110020",
                "contact_person": "Ms. Sunita Sharma",
                "contact_phone": "+91 98110 33452",
                "contact_email": "delhi.south.pmajay@gov.in",
                "latitude": 28.5355,
                "longitude": 77.2612,
                "hostel_available": False,
                "pm_ajay_funded": True,
                "trade_codes": ["ELE/Q3102", "ASC/Q1411", "LSC/Q0101", "SSC/Q2212"]
            },
            {
                "center_id": "PMAJAY-TC-TN-MDU01",
                "name": "PM-AJAY Livelihood Training Center - Madurai",
                "state": "Tamil Nadu",
                "district": "Madurai",
                "address": "Kappalur SIDCO Industrial Estate, Thirumangalam Road, Madurai - 625008",
                "contact_person": "Mr. K. Senthil Kumar",
                "contact_phone": "+91 94433 11890",
                "contact_email": "madurai.pmajay@gov.in",
                "latitude": 9.9252,
                "longitude": 78.1198,
                "hostel_available": True,
                "pm_ajay_funded": True,
                "trade_codes": ["AMH/Q1201", "ELE/Q4601", "ASC/Q1411", "FIC/Q0103"]
            },
            {
                "center_id": "PMAJAY-TC-TS-HYD01",
                "name": "State SC/ST Livelihood Hub - Hyderabad Ranga Reddy",
                "state": "Telangana",
                "district": "Hyderabad",
                "address": "Cherlapally Industrial Development Area, ECIL Cross Roads, Hyderabad - 500051",
                "contact_person": "Dr. V. Prasad Rao",
                "contact_phone": "+91 98480 55671",
                "contact_email": "hyderabad.livelihood@gov.in",
                "latitude": 17.4589,
                "longitude": 78.6012,
                "hostel_available": True,
                "pm_ajay_funded": True,
                "trade_codes": ["ELE/Q3102", "ASC/Q1411", "LSC/Q0101", "SSC/Q2212", "AGR/Q0104"]
            },
            {
                "center_id": "PMAJAY-TC-MH-PUN01",
                "name": "Dr. Ambedkar Livelihood Mission Center - Pune",
                "state": "Maharashtra",
                "district": "Pune",
                "address": "Bhosari MIDC, General Block, Pimpri-Chinchwad, Pune - 411026",
                "contact_person": "Shri Vilas Kamble",
                "contact_phone": "+91 98220 44901",
                "contact_email": "pune.ambedkarcenter@gov.in",
                "latitude": 18.6298,
                "longitude": 73.8131,
                "hostel_available": False,
                "pm_ajay_funded": True,
                "trade_codes": ["ASC/Q1411", "CON/Q0102", "LSC/Q0101", "ELE/Q4601"]
            },
            {
                "center_id": "PMAJAY-TC-OR-SBP01",
                "name": "Western Odisha PM-AJAY Multi-Skilling Centre - Sambalpur",
                "state": "Odisha",
                "district": "Sambalpur",
                "address": "Remed Industrial Area, Bargarh Highway, Sambalpur - 768006",
                "contact_person": "Ms. Lipsa Pradhan",
                "contact_phone": "+91 94370 66213",
                "contact_email": "sambalpur.skills@gov.in",
                "latitude": 21.4669,
                "longitude": 83.9812,
                "hostel_available": True,
                "pm_ajay_funded": True,
                "trade_codes": ["AMH/Q1201", "HCS/Q7303", "AGR/Q0104", "CON/Q0102"]
            },
            {
                "center_id": "PMAJAY-TC-WB-KOL01",
                "name": "Netaji Subhash PM-AJAY Technical Hub - Kolkata",
                "state": "West Bengal",
                "district": "Kolkata",
                "address": "Taratala Industrial Area, Diamond Harbour Road, Kolkata - 700088",
                "contact_person": "Mr. Arijit Mukherjee",
                "contact_phone": "+91 98300 77129",
                "contact_email": "kolkata.pmajay@gov.in",
                "latitude": 22.5020,
                "longitude": 88.3075,
                "hostel_available": False,
                "pm_ajay_funded": True,
                "trade_codes": ["AMH/Q1201", "FIC/Q0103", "LSC/Q0101", "ELE/Q4601"]
            }
        ]

        for c_data in centers_data:
            trade_codes = c_data.pop("trade_codes")
            center, created = SkillCenter.objects.update_or_create(
                center_id=c_data["center_id"],
                defaults=c_data
            )
            # Associate trades
            for qp_code in trade_codes:
                if qp_code in created_trades:
                    center.trades_offered.add(created_trades[qp_code])

            status_text = "Created" if created else "Updated"
            self.stdout.write(f" - {status_text} Skill Center: {center.center_id} ({center.name})")

        self.stdout.write(self.style.SUCCESS("Successfully seeded all NSQF Trades and PM-AJAY Skill Centers!"))
