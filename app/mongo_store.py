from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient

from app.auth import hash_password


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

MONGO_URI = os.getenv("MONGO_URI", "").strip()
raw_db = os.getenv("MONGO_DATABASE", "urbanpulse").strip()
if "://" in raw_db:
    from urllib.parse import urlparse
    parsed_path = urlparse(raw_db).path.strip("/")
    MONGO_DATABASE = parsed_path.split("?")[0] if parsed_path else "urbanpulse"
else:
    MONGO_DATABASE = raw_db or "urbanpulse"
if "." in MONGO_DATABASE or "/" in MONGO_DATABASE:
    MONGO_DATABASE = "urbanpulse"

AUTHORITY_ROUTING = (
    ("AUTH001", "Pothole Detection Municipal Authority (Mahesh)", "mahesh.p.170107@gmail.com"),
)
AUTHORITY_REGIONS = {
    "mahesh.p.170107@gmail.com": None,
    "mahesh.p.170107": None,
    "urbanpulseai23@gmail.com": None,
}


class MongoStore:
    """Single MongoDB repository for authorities, pincode routing, complaints, and GIS defects."""

    def __init__(self) -> None:
        self._memory: dict[str, list[dict[str, Any]]] = {
            "authorities": [], "contractors": [], "pincode_areas": [], "complaints": [], "defects": [],
        }
        self._next_id = 1
        try:
            self._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500) if MONGO_URI else None
            self._database = self._client[MONGO_DATABASE] if self._client else None
        except Exception:
            self._client = None
            self._database = None

    @property
    def demo_mode(self) -> bool:
        return self._database is None

    def collection(self, name: str):
        return self._database[name] if self._database is not None else _MemoryCollection(self._memory[name])

    def init(self) -> None:
        if self._database is not None:
            try:
                self._client.admin.command("ping")
            except Exception:
                self._client.close()
                self._client = None
                self._database = None
                return
            self.collection("authorities").create_index("email", unique=True)
            self.collection("pincode_areas").create_index("pincode", unique=True)
            self.collection("complaints").create_index("complaint_id", unique=True)
            self.collection("complaints").create_index([("pincode", 1), ("status", 1), ("created_at", -1)])
            self.collection("complaints").create_index([("location_point", "2dsphere")])
            self.collection("defects").create_index([("latitude", 1), ("longitude", 1)])

    def seed(self) -> dict:
        authorities = self.collection("authorities")
        if not authorities.find_one({"email": "roads.ward12@example.gov.in"}):
            authorities.insert_one({
                "authority_id": "AUTH001", "authority_name": "Vijayawada Municipal Corporation",
                "department": "Roads & Engineering", "contact_person": "Public Works Desk",
                "email": "roads.ward12@example.gov.in", "phone": "+91-866-000-0012",
                "office_address": "Vijayawada Municipal Office", "city": "Vijayawada",
                "district": "NTR", "state": "Andhra Pradesh", "active": True,
                "complaint_types": ["Pothole", "Road Damage", "Drainage", "Waterlogging", "Flooding"],
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })
        if not authorities.find_one({"email": "roads.ward12@example.gov.in"}):
            return {"status": "seed_failed"}
        contractors = self.collection("contractors")
        contractor_password = os.getenv("DEMO_CONTRACTOR_PASSWORD", "").strip()
        contractor_password_hash = hash_password(contractor_password) if contractor_password else ""
        contractor_record = {
            "contractor_id": "CONTRACTOR001", "company_name": "MetroFix Contractors",
            "email": "contact@metrofix.com", "phone": "+15551234567",
            "password_hash": contractor_password_hash, "active": True,
        }
        if not contractors.find_one({"email": "contact@metrofix.com"}):
            contractors.insert_one(contractor_record)
        else:
            contractors.find_one_and_update(
                {"email": "contact@metrofix.com"},
                {"$set": {"password_hash": contractor_password_hash}},
            )
        for index, (_, authority_name, email) in enumerate(AUTHORITY_ROUTING, start=1):
            account = authorities.find_one({"email": email})
            authority_record = {
                "authority_id": AUTHORITY_ROUTING[index - 1][0],
                "authority_name": authority_name,
                "department": "Roads & Engineering", "email": email,
                "active": True, "updated_at": datetime.now(timezone.utc),
            }
            if account:
                authorities.find_one_and_update({"email": email}, {"$set": authority_record})
            else:
                authority_record["created_at"] = datetime.now(timezone.utc)
                authorities.insert_one(authority_record)
        areas = self.collection("pincode_areas")
        area_seed = [
            ("520010", "Benz Circle", "12", "Vijayawada", "NTR", "Andhra Pradesh", "Vijayawada Municipal Corporation"),
            ("520007", "Moghalrajpuram", "7", "Vijayawada", "NTR", "Andhra Pradesh", "Vijayawada Municipal Corporation"),
            ("520008", "Governorpet", "8", "Vijayawada", "NTR", "Andhra Pradesh", "Vijayawada Municipal Corporation"),
            ("520009", "Patamata", "9", "Vijayawada", "NTR", "Andhra Pradesh", "Vijayawada Municipal Corporation"),
            ("520012", "Poranki", "13", "Vijayawada", "NTR", "Andhra Pradesh", "Vijayawada Municipal Corporation"),
            ("530001", "Dwaraka Nagar", "1", "Visakhapatnam", "Visakhapatnam", "Andhra Pradesh", "Greater Visakhapatnam Municipal Corporation"),
            ("530003", "MVP Colony", "3", "Visakhapatnam", "Visakhapatnam", "Andhra Pradesh", "Greater Visakhapatnam Municipal Corporation"),
            ("530016", "Seethammadhara", "16", "Visakhapatnam", "Visakhapatnam", "Andhra Pradesh", "Greater Visakhapatnam Municipal Corporation"),
            ("517501", "Tirupati Central", "1", "Tirupati", "Tirupati", "Andhra Pradesh", "Tirupati Municipal Corporation"),
            ("524003", "Gandhi Nagar", "3", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            # GUNTUR
            ("522001", "Guntur Central", "1", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522002", "Arundelpet", "2", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522003", "Brodipet", "3", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522004", "Nallapadu", "4", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522006", "Lalapet", "6", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522007", "Nagarampalem", "7", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            ("522034", "Gorantla", "34", "Guntur", "Guntur", "Andhra Pradesh", "Guntur Municipal Corporation"),
            # PALNADU
            ("522403", "Sattenapalle", "1", "Sattenapalle", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522413", "Piduguralla", "2", "Piduguralla", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522414", "Dachepalle", "3", "Dachepalle", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522415", "Gurazala", "4", "Gurazala", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522426", "Macherla", "5", "Macherla", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522601", "Narasaraopet", "6", "Narasaraopet", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522616", "Chilakaluripet", "7", "Chilakaluripet", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            ("522647", "Vinukonda", "8", "Vinukonda", "Palnadu", "Andhra Pradesh", "Palnadu District Administration"),
            #BAPATLA
            ("522101", "Bapatla", "1", "Bapatla", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522102", "Bapatla Engineering College", "2", "Bapatla", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522111", "Karlapalem", "1", "Karlapalem", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522256", "Bhattiprolu", "1", "Bhattiprolu", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522261", "Vemuru", "1", "Vemuru", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522265", "Repalle", "1", "Repalle", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522268", "Nagaram", "1", "Nagaram", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522309", "Cherukupalle", "1", "Cherukupalle", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522310", "Pittalavanipalem", "1", "Pittalavanipalem", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522314", "Nizampatnam", "1", "Nizampatnam", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522318", "Tsundur", "1", "Tsundur", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("522325", "Amruthalur", "1", "Amruthalur", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("523155", "Chirala", "1", "Chirala", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("523169", "Parchur", "1", "Parchur", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("523187", "Vetapalem", "1", "Vetapalem", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("523201", "Addanki", "1", "Addanki", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("523301", "Martur", "1", "Martur", "Bapatla", "Andhra Pradesh", "Bapatla District Administration"),
            ("600001", "Parrys", "1", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600002", "Egmore", "2", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600004", "Mylapore", "4", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600006", "Nungambakkam", "6", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600017", "T Nagar", "17", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600020", "Adyar", "20", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600028", "Raja Annamalaipuram", "28", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600034", "Thousand Lights", "34", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600040", "Anna Nagar", "40", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("600083", "Ashok Nagar", "83", "Chennai", "Chennai", "Tamil Nadu", "Greater Chennai Corporation"),
            ("682001", "Fort Kochi", "1", "Kochi", "Ernakulam", "Kerala", "Kochi Municipal Corporation"),
            ("682016", "Kaloor", "16", "Kochi", "Ernakulam", "Kerala", "Kochi Municipal Corporation"),
            ("682017", "Palarivattom", "17", "Kochi", "Ernakulam", "Kerala", "Kochi Municipal Corporation"),
            ("682018", "Vyttila", "18", "Kochi", "Ernakulam", "Kerala", "Kochi Municipal Corporation"),
            ("682020", "Kakkanad", "20", "Kochi", "Ernakulam", "Kerala", "Kochi Municipal Corporation"),
            ("695001", "Thiruvananthapuram Central", "1", "Thiruvananthapuram", "Thiruvananthapuram", "Kerala", "Thiruvananthapuram Corporation"),
            ("695003", "Pattom", "3", "Thiruvananthapuram", "Thiruvananthapuram", "Kerala", "Thiruvananthapuram Corporation"),
            ("673001", "Kozhikode Central", "1", "Kozhikode", "Kozhikode", "Kerala", "Kozhikode Corporation"),
            ("680001", "Thrissur Central", "1", "Thrissur", "Thrissur", "Kerala", "Thrissur Municipal Corporation"),
            ("691001", "Kollam Central", "1", "Kollam", "Kollam", "Kerala", "Kollam Corporation"),
            ("560001", "Bengaluru GPO", "1", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560034", "Koramangala", "34", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560038", "Indiranagar", "38", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560041", "Jayanagar", "41", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560048", "Mahadevapura", "48", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560056", "Nagarbhavi", "56", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560066", "Whitefield", "66", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("560076", "Bannerghatta Road", "76", "Bengaluru", "Bengaluru Urban", "Karnataka", "BBMP"),
            ("570001", "Mysuru Central", "1", "Mysuru", "Mysuru", "Karnataka", "Mysuru City Corporation"),
            ("580001", "Hubballi Central", "1", "Hubballi", "Dharwad", "Karnataka", "Hubballi-Dharwad Municipal Corporation"),
            ("452001", "Indore Central", "1", "Indore", "Indore", "Madhya Pradesh", "Indore Municipal Corporation"),
            ("452010", "Vijay Nagar", "10", "Indore", "Indore", "Madhya Pradesh", "Indore Municipal Corporation"),
            ("462001", "Bhopal Central", "1", "Bhopal", "Bhopal", "Madhya Pradesh", "Bhopal Municipal Corporation"),
            ("462016", "Kolar Road", "16", "Bhopal", "Bhopal", "Madhya Pradesh", "Bhopal Municipal Corporation"),
            ("474001", "Gwalior Central", "1", "Gwalior", "Gwalior", "Madhya Pradesh", "Gwalior Municipal Corporation"),
            ("482001", "Jabalpur Central", "1", "Jabalpur", "Jabalpur", "Madhya Pradesh", "Jabalpur Municipal Corporation"),
            ("485001", "Satna Central", "1", "Satna", "Satna", "Madhya Pradesh", "Satna Municipal Corporation"),
            ("456001", "Ujjain Central", "1", "Ujjain", "Ujjain", "Madhya Pradesh", "Ujjain Municipal Corporation"),
            ("452020", "Rau", "20", "Indore", "Indore", "Madhya Pradesh", "Indore Municipal Corporation"),
            ("462023", "Arera Colony", "23", "Bhopal", "Bhopal", "Madhya Pradesh", "Bhopal Municipal Corporation"),
            ("700001", "BBD Bagh", "1", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700019", "Park Street", "19", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700029", "Ballygunge", "29", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700032", "Jadavpur", "32", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700034", "Behala", "34", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700040", "Tollygunge", "40", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700054", "Phoolbagan", "54", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700075", "Garia", "75", "Kolkata", "Kolkata", "West Bengal", "Kolkata Municipal Corporation"),
            ("700091", "Salt Lake", "91", "Kolkata", "North 24 Parganas", "West Bengal", "Bidhannagar Municipal Corporation"),
            ("713101", "Durgapur Central", "1", "Durgapur", "Paschim Bardhaman", "West Bengal", "Durgapur Municipal Corporation"),
            ("SW1A 1AA", "Westminster", "1", "London", "Greater London", "United Kingdom", "Westminster City Council"),
            ("W1A 1AA", "Marylebone", "1", "London", "Greater London", "United Kingdom", "Westminster City Council"),
            ("M1 1AE", "Manchester Central", "1", "Manchester", "Greater Manchester", "United Kingdom", "Manchester City Council"),
            ("B1 1AA", "Birmingham Central", "1", "Birmingham", "West Midlands", "United Kingdom", "Birmingham City Council"),
            ("L1 1AA", "Liverpool Central", "1", "Liverpool", "Merseyside", "United Kingdom", "Liverpool City Council"),
            ("EH1 1YZ", "Edinburgh Old Town", "1", "Edinburgh", "Midlothian", "United Kingdom", "City of Edinburgh Council"),
            ("G1 1AA", "Glasgow Central", "1", "Glasgow", "Lanarkshire", "United Kingdom", "Glasgow City Council"),
            ("BS1 1AA", "Bristol Central", "1", "Bristol", "Bristol", "United Kingdom", "Bristol City Council"),
            ("CF10 1AA", "Cardiff Central", "1", "Cardiff", "South Glamorgan", "United Kingdom", "Cardiff Council"),
            ("BT1 1AA", "Belfast Central", "1", "Belfast", "County Antrim", "United Kingdom", "Belfast City Council"),
        ]
        krishna_area_seed = [
            ("521321", "Nandivada", "1", "Gudivada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521326", "Gunnanapudi", "1", "Gudivada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521325", "K.P. Agraharam", "1", "Mudinepalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521333", "Atapaka", "1", "Kaikaluru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521343", "Bomminampadu", "1", "Korukollu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521329", "Chinatummidi", "1", "Pedagonnuru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521345", "Korlapadu", "1", "Mandavalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521340", "Kottada", "1", "Pallevada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521324", "Lakshmipuram", "1", "Bantumilli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521344", "Mulaupparagudem", "1", "Kalidindi", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521148", "Edulamaddali", "1", "Elamarru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521390", "Addada", "1", "Pedamaddali", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521261", "Appikatla", "1", "Mudunuru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521330", "Bommuluru", "1", "Angaluru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521323", "Pedapalaparru", "1", "Moturu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521327", "Anamanapudi", "1", "Tamirisa", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521263", "Bushanagulla", "1", "Ventrapragada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521322", "Gandhiashramam", "1", "Golvepalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521260", "Komatiguntalock", "1", "Manikonda", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521312", "Koyyagurappadu", "1", "Vunguturu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521311", "Lankapalli Agraharam", "1", "Indupalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521215", "Annaraopet", "1", "Vissannapeta", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521202", "Boruvancha", "1", "APIIIT", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521214", "Janardhanavaram", "1", "Tsanubanda", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521111", "Kothapalli", "1", "Gollapalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521213", "Lopudi", "1", "Ramanakkapeta", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521106", "Aripirala", "1", "Kanumolu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521207", "Mukkollupadu", "1", "Musunuru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521105", "Perikeedubridge", "1", "Hanuman Junction", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521228", "Pinapaka", "1", "Kondapalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("520015", "Payakapuram", "1", "Vijayawada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521211", "Chopparametla", "1", "Aukiripalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521229", "Atkuru", "1", "Konduru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("520003", "Ramakrishnapuram", "1", "Vijayawada", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521107", "Savaragudem", "1", "Mustabad", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521212", "Adavinekkalam", "1", "Nunna", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521241", "Guntupalli", "1", "RLY Wagon Workshop", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521456", "Chilukuru", "1", "VTPS", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521104", "Gudavalli", "1", "Nidamanuru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521286", "Atkuru", "1", "Pedaautapalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521108", "Enikepadu", "1", "Ramavarappadu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521182", "Bobbellapadu", "1", "Chandarlapadu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521178", "Bandipalem", "1", "Chillakallu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521175", "Anumanchipalli", "1", "Jaggayyapeta", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521457", "Jayanthipuram", "1", "Kumararaja Swamy Nagar", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521183", "Chintalapadu", "1", "Muppalla", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521185", "Chandapuram", "1", "Nandigama", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521002", "Karagraharam", "1", "Machilipatnam", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521366", "Konkepudi", "1", "Pedana", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521003", "Kammavaricheruvu", "1", "Chintaguntapalem", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521369", "Satuluru", "1", "Munjuluru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521122", "Aswaraopalem", "1", "Gandhikshetram", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521138", "Ayyanki", "1", "Pedasanagallu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521132", "Chinakallepalli", "1", "Kodali", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521150", "Chitturu", "1", "Kaja", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521356", "Daggumilli", "1", "Gudlavalleru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521332", "Jakkamcherla", "1", "Dokiparru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521331", "Kongamcherla", "1", "Kavutaram", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521135", "Gudapadu", "1", "Movva", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521149", "Kankata", "1", "Guduru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521125", "Kokkiligadda", "1", "Mopidevi", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521157", "Kurumaddali", "1", "Pamarru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521162", "Mallavolu", "1", "Polavaram", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521158", "Nemmaluru", "1", "Nimmakuru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521156", "P.G. Lanka", "1", "Nidumolu", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521126", "Pagolu", "1", "Challapalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521328", "Swatantrapuram", "1", "Koduru", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521130", "Kummaripalem", "1", "Pedakallepalli", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521131", "Lankapalli", "1", "Lakshmipuram", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521120", "Bhavadevarapalli", "1", "Nagayalanka", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            ("521301", "Mandapadu", "1", "Satyanarayanapuram", "Krishna", "Andhra Pradesh", "Krishna District Administration"),
            # NELLORE / SPSR NELLORE
            ("524001", "Trunk Road", "1", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524002", "A.C. Nagar", "2", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524004", "Pottepalem", "4", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524005", "Polytechnic", "5", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),

            ("524101", "Gudur", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524121", "Akkampeta", "1", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524123", "Sullurpeta", "1", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524124", "Sullurpeta", "2", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524126", "Nelaballi", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),

            ("524127", "Aravapalem", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524129", "Akkagaripeta", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524131", "Alimili", "1", "Venkatagiri", "SPSR Nellore", "Andhra Pradesh", "Venkatagiri Municipal Administration"),
            ("524132", "Venkatagiri", "1", "Venkatagiri", "SPSR Nellore", "Andhra Pradesh", "Venkatagiri Municipal Administration"),
            ("524134", "Althurupadu", "1", "Venkatagiri", "SPSR Nellore", "Andhra Pradesh", "Venkatagiri Municipal Administration"),

            ("524137", "Pothireddypalem", "1", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524142", "Akkarajuvari Kandriga", "1", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524152", "Venkatesupalem", "1", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),

            # KAVALI
            ("524201", "Musunur", "1", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524203", "Anemadugu", "2", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524221", "Kothapeta", "3", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524222", "Rachavaripalli", "4", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524223", "Annavaram", "5", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524224", "Polampadu", "6", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524225", "Turupur", "7", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524226", "Balayapalli", "8", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524227", "Chinna Kaniyampadu", "9", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524228", "Yerikollu", "10", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524230", "Chinnamachanur", "11", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524234", "Kavali Yadavalli", "12", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524236", "Gudinarava", "13", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524239", "Kondapuram", "14", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),
            ("524240", "Chowtaputtedu", "15", "Kavali", "SPSR Nellore", "Andhra Pradesh", "Kavali Municipal Administration"),

            # NELLORE RURAL / OTHER AREAS
            ("524300", "Padamatikhambampadu", "1", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524302", "Mangupalli", "2", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524303", "Bandarupalli", "3", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524304", "Peddabbipuram", "4", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524305", "Chellayapalem", "5", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524306", "Panchedu", "6", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524307", "Mahimalur", "7", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524308", "Hasanapuram", "8", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524309", "Bathulapalli", "9", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524310", "Bodasi Idayapalli", "10", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524311", "Papireddypalem", "11", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524312", "Tikkavaram", "12", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524313", "Gangapatnam", "13", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524314", "Komarika", "14", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524315", "Batrakagallu", "15", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524316", "Damagunta", "16", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524317", "Turimerla", "17", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524318", "Alaganipadu", "18", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524319", "Kammapalem", "19", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524320", "Dontali", "20", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524321", "Idimepalli", "21", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524322", "Cherloyadavalli", "22", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524323", "Tirumalammapalem", "23", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524324", "Vikramasimhapuri University", "24", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),

            # GUDUR / VENKATAGIRI SIDE
            ("524341", "Perumallapadu", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524342", "Kollapanayunipalli", "2", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524343", "Kanupurpalli", "3", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524344", "Krishnapatnam", "4", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524345", "Ammavaripalem", "5", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524346", "Pidathapoluru", "6", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524347", "AP Genco Nelatur", "7", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),
            ("524366", "Yellayapalem", "8", "Nellore", "SPSR Nellore", "Andhra Pradesh", "Nellore Municipal Corporation"),

            # GUDUR DIVISION
            ("524401", "Gudur", "1", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524402", "Armenipadu", "2", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524403", "Gudur Rural", "3", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524404", "Bangarupeta", "4", "Venkatagiri", "SPSR Nellore", "Andhra Pradesh", "Venkatagiri Municipal Administration"),
            ("524405", "Akkampeta", "5", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
            ("524406", "Naidupeta", "6", "Naidupeta", "SPSR Nellore", "Andhra Pradesh", "Naidupeta Municipal Administration"),
            ("524407", "Daggavolu", "7", "Naidupeta", "SPSR Nellore", "Andhra Pradesh", "Naidupeta Municipal Administration"),
            ("524408", "Gilakapadu", "8", "Naidupeta", "SPSR Nellore", "Andhra Pradesh", "Naidupeta Municipal Administration"),
            ("524409", "Devaravemuru", "9", "Naidupeta", "SPSR Nellore", "Andhra Pradesh", "Naidupeta Municipal Administration"),
            ("524410", "Sullurpeta Rural", "10", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524411", "Tada", "11", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524412", "Tada Khandrika", "12", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524413", "Varadaiahpalem", "13", "Sullurpeta", "SPSR Nellore", "Andhra Pradesh", "Sullurpeta Municipal Administration"),
            ("524414", "Penubarthi", "14", "Gudur", "SPSR Nellore", "Andhra Pradesh", "Gudur Municipal Administration"),
                    ]
        area_seed.extend(krishna_area_seed)
        for pincode, area, ward_number, city, district, state, authority_name in area_seed:
            area_record = {
                "pincode": pincode, "area": area, "ward_number": ward_number,
                "city": city, "district": district, "state": state,
                "jurisdiction": authority_name, "department": "Roads & Engineering",
                "active": True,
            }
            existing_area = areas.find_one({"pincode": pincode})
            if existing_area:
                areas.find_one_and_update({"pincode": pincode}, {"$set": area_record})
            else:
                areas.insert_one(area_record)

        # Reassign the complete collection to Mahesh so all pincodes route to Mahesh
        for area in areas.find(sort=[("pincode", 1)]):
            areas.find_one_and_update(
                {"pincode": area["pincode"]},
                {"$set": {
                    "authority_id": "AUTH001",
                    "authority_name": "Pothole Detection Municipal Authority (Mahesh)",
                    "authority_email": "mahesh.p.170107@gmail.com",
                    "active": True,
                }},
            )
        complaints = self.collection("complaints")
        for complaint in complaints.find():
            complaints.find_one_and_update(
                {"complaint_id": complaint["complaint_id"]},
                {"$set": {
                    "authority_id": "AUTH001",
                    "authority_name": "Pothole Detection Municipal Authority (Mahesh)",
                    "authority_email": "mahesh.p.170107@gmail.com",
                }},
            )
        demo_area = areas.find_one({"pincode": "520010"})
        demo_complaint = complaints.find_one({"complaint_id": "CMP-2026-00001"})
        if demo_complaint is None:
            complaints.insert_one({
                "complaint_id": "CMP-2026-00001", "reporter_phone": "+15557654321",
                "citizen_name": "Demo Citizen", "complaint_type": "Pothole",
                "title": "Large pothole near MG Road", "description": "Demo complaint for dashboard testing.",
                "pincode": "520010", "area": "Benz Circle", "ward_number": "12",
                "city": "Vijayawada", "district": "NTR", "state": "Andhra Pradesh",
                "latitude": 16.4978, "longitude": 80.6498,
                "location_point": {"type": "Point", "coordinates": [80.6498, 16.4978]},
                "severity_level": "HIGH", "estimated_depth_cm": 18.5,
                "authority_id": demo_area["authority_id"], "authority_name": demo_area["authority_name"],
                "department": "Roads & Engineering", "authority_email": demo_area["authority_email"],
                "status": "PENDING_VERIFICATION", "email_status": "Demo",
                "duplicate_status": "New", "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
        else:
            complaints.find_one_and_update(
                {"complaint_id": "CMP-2026-00001"},
                {"$set": {
                    "authority_id": demo_area["authority_id"],
                    "authority_name": demo_area["authority_name"],
                    "authority_email": demo_area["authority_email"],
                }},
            )
        item = complaints.find_one({"complaint_id": "CMP-2026-00001"})
        return {"complaint_id": item["complaint_id"], "status": item["status"], "authority_email": item["authority_email"]}

    def next_complaint_id(self) -> str:
        year = datetime.now(timezone.utc).year
        count = self.collection("complaints").count_documents({}) + 1
        return f"CMP-{year}-{count:05d}"


class _MemoryCollection:
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self.records = records

    def find_one(self, query: dict) -> dict | None:
        return next((record for record in self.records if _matches_query(record, query)), None)

    def insert_one(self, record: dict) -> None:
        self.records.append(dict(record))

    def count_documents(self, query: dict) -> int:
        return sum(1 for record in self.records if _matches_query(record, query))

    def find(self, query: dict | None = None, sort=None):
        query = query or {}
        records = [record for record in self.records if _matches_query(record, query)]
        if sort:
            for key, direction in reversed(sort):
                records.sort(key=lambda item: _sort_value(item.get(key)), reverse=direction < 0)
        return records

    def find_one_and_update(self, query: dict, update: dict, return_document=None):
        record = self.find_one(query)
        if record:
            record.update(update.get("$set", {}))
        return record


def _matches_query(record: dict[str, Any], query: dict) -> bool:
    """Evaluate the small Mongo query subset used by the demo store."""
    for key, expected in query.items():
        if key == "$or":
            if not any(_matches_query(record, branch) for branch in expected):
                return False
            continue
        actual = record.get(key)
        if isinstance(expected, dict):
            if "$in" in expected and actual not in expected["$in"]:
                return False
            if "$eq" in expected and actual != expected["$eq"]:
                return False
            continue
        if actual != expected:
            return False
    return True


def _sort_value(value: Any) -> str:
    """Keep demo-mode sorting stable when old records use datetime values."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value or "")


store = MongoStore()