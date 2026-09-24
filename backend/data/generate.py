"""
Synthetic data generator for all 7 NCRB source types.

Produces unresolved, pre-extraction raw JSON files in backend/data/raw/.
These simulate fragmented real-world source data BEFORE entity extraction.

Seed=42 for reproducibility.

NCRB-aggregate-informed constants:
  - Crime-type frequency weights derived from NCRB 2022 "Crime in India" report
    (Table 3A: IPC heads by volume). Approximate percentages normalized to
    sum=1.0 for weighting random selection.
  - District Urban/Rural split ~ 35:65 national average (NCRB 2022 Table 1.2).
  - Crimes against women are ~14.5% of total IPC crimes (NCRB 2022 highlight).
  - Kidnapping & trafficking cases are ~1.2% of IPC but concentrated in
    specific corridors (Delhi, UP, Rajasthan, Maharashtra, AP/Telangana).
"""

from __future__ import annotations

import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED = 42
RAW_DIR = Path(__file__).resolve().parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

fake = Faker("en_IN")
Faker.seed(SEED)
random.seed(SEED)

# ---------------------------------------------------------------------------
# NCRB-aggregate-informed crime-type frequency weights (IPC heads, 2022)
# Source: NCRB "Crime in India" 2022, Table 3A — approximate share of total IPC crimes
# ---------------------------------------------------------------------------
CRIME_TYPE_WEIGHTS = {
    "Theft": 0.263,
    "Assault": 0.152,
    "Fraud": 0.128,
    "Domestic_violence": 0.118,
    "Robbery": 0.067,
    "Kidnapping": 0.012,
    "Trafficking": 0.004,
    "Murder": 0.011,
    "Cyber_crime": 0.089,
    "Drug_offences": 0.058,
    "Criminal_intimidation": 0.052,
    "Others": 0.046,
}

CRIME_TYPES = list(CRIME_TYPE_WEIGHTS.keys())
CRIME_PROBS = list(CRIME_TYPE_WEIGHTS.values())

# NCRB 2022 — top states by crime volume (approximate share for regional weighting)
STATE_WEIGHTS = {
    "Uttar Pradesh": 0.145,
    "Maharashtra": 0.095,
    "Madhya Pradesh": 0.088,
    "Delhi": 0.072,
    "Rajasthan": 0.068,
    "Bihar": 0.062,
    "Tamil Nadu": 0.055,
    "West Bengal": 0.050,
    "Karnataka": 0.042,
    "Telangana": 0.038,
}
STATES = list(STATE_WEIGHTS.keys())
STATE_PROBS = list(STATE_WEIGHTS.values())

# NCRB 2022 — urban/rural split (~35% urban, 65% rural nationally)
AREA_TYPES = ["urban", "rural"]
AREA_PROBS = [0.35, 0.65]

# NCRB 2022 — crimes against women share by type (approximate, within that category)
CAW_TYPES = [
    "Cruelty_by_husband_or_relatives",
    "Assault_on_women_with_intent_to_outrage_modesty",
    "Kidnapping_and_abduction_of_women",
    "Dowry_death",
    "Rape",
    "Sexual_harassment",
]
CAW_WEIGHTS = [0.322, 0.234, 0.128, 0.067, 0.112, 0.137]

# ---------------------------------------------------------------------------
# Ring members — the trafficking/kidnapping narrative
# These ~7 people appear across 4+ source types with consistent identifiers.
# ---------------------------------------------------------------------------
RING_MEMBERS = [
    {
        "name": "Vikram Patel",
        "phone": "9876543210",
        "alt_phones": ["9812345601"],
        "accounts": ["HDFC-XXXX-1122", "SBI-XXXX-3344"],
        "address": "45, Lajpat Nagar, New Delhi",
        "role": "ringleader",
    },
    {
        "name": "Anil Kumar",
        "phone": "9876543211",
        "alt_phones": ["9812345602"],
        "accounts": ["ICICI-XXXX-5566"],
        "address": "12, Model Town, Jaipur",
        "role": "recruiter",
    },
    {
        "name": "Deepak Singh",
        "phone": "9876543212",
        "alt_phones": [],
        "accounts": ["Axis-XXXX-7788"],
        "address": "78, Civil Lines, Lucknow",
        "role": "transporter",
    },
    {
        "name": "Sunita Devi",
        "phone": "9876543213",
        "alt_phones": ["9812345604"],
        "accounts": ["HDFC-XXXX-9900"],
        "address": "23, Nehru Nagar, Bhopal",
        "role": "handler",
    },
    {
        "name": "Ravi Sharma",
        "phone": "9876543214",
        "alt_phones": [],
        "accounts": ["SBI-XXXX-1123", "Kotak-XXXX-4455"],
        "address": "90, Andheri West, Mumbai",
        "role": "financier",
    },
    {
        "name": "Kavita Gupta",
        "phone": "9876543215",
        "alt_phones": ["9812345606"],
        "accounts": ["PNB-XXXX-6677"],
        "address": "56, Dharavi, Mumbai",
        "role": "facilitator",
    },
    {
        "name": "Mohan Yadav",
        "phone": "9876543216",
        "alt_phones": [],
        "accounts": ["BOB-XXXX-8899"],
        "address": "34, Agra Road, Jaipur",
        "role": "enforcer",
    },
]

# Structuring pattern accounts (sub-threshold transfers)
STRUCT_ACCOUNTS = [
    ("HDFC-XXXX-1122", "Vikram Patel"),   # ring leader
    ("ICICI-XXXX-5566", "Anil Kumar"),     # recruiter
    ("SBI-XXXX-3344", "Vikram Patel"),     # ring leader alt
    ("Axis-XXXX-7788", "Deepak Singh"),    # transporter
]

# Circular transfer accounts (A→B→C→A)
CIRC_A = ("HDFC-XXXX-9900", "Sunita Devi")
CIRC_B = ("SBI-XXXX-1123", "Ravi Sharma")
CIRC_C = ("PNB-XXXX-6677", "Kavita Gupta")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _random_date(start_year: int = 2023, end_year: int = 2024) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def _random_datetime(start_year: int = 2023, end_year: int = 2024) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = int((end - start).total_seconds())
    dt = start + timedelta(seconds=random.randint(0, delta))
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _weighted_choice(items: list, weights: list):
    return random.choices(items, weights=weights, k=1)[0]


def _state() -> str:
    return _weighted_choice(STATES, STATE_PROBS)


def _area() -> str:
    return _weighted_choice(AREA_TYPES, AREA_PROBS)


def _crime_type() -> str:
    return _weighted_choice(CRIME_TYPES, CRIME_PROBS)


def _district(state: str) -> str:
    districts = {
        "Uttar Pradesh": ["Lucknow", "Noida", "Varanasi", "Agra", "Kanpur"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
        "Delhi": ["New Delhi", "Central Delhi", "South Delhi", "East Delhi", "North Delhi"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
        "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
        "Karnataka": ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belgaum"],
        "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam"],
    }
    return random.choice(districts.get(state, ["Unknown"]))


# ---------------------------------------------------------------------------
# Source generators — each produces a list of raw records
# ---------------------------------------------------------------------------

def _generate_fir(count: int) -> list[dict]:
    """FIR (First Information Report) records — narrative-heavy."""
    records = []

    # Inject ring-linked FIRs first (3 FIRs referencing ring members)
    ring_firs = [
        {
            "fir_number": "FIR/2024/DEL/00123",
            "date": "2024-03-15",
            "police_station": "Lajpat Nagar PS, New Delhi",
            "district": "South Delhi",
            "state": "Delhi",
            " complainant": "Ramesh Kumar (father of victim)",
            "accused": "Vikram Patel, Anil Kumar",
            "ipc_sections": "366-A, 370, 120-B IPC",
            "crime_type": "Kidnapping and Trafficking",
            "narrative": (
                "Complainant states that his daughter, aged 19, was lured by accused "
                "Anil Kumar on 10/03/2024 from Lajpat Nagar with false promise of "
                "employment in Mumbai. Accused Vikram Patel is the main organizer. "
                "Victim's phone last active at 9876543210. Multiple witnesses report "
                "seeing victim with accused near New Delhi railway station on 12/03/2024."
            ),
            "area_type": "urban",
            "status": "Under Investigation",
        },
        {
            "fir_number": "FIR/2024/RAJ/00456",
            "date": "2024-05-22",
            "police_station": "Civil Lines PS, Jaipur",
            "district": "Jaipur",
            "state": "Rajasthan",
            "complainant": "Sunita Devi (self)",
            "accused": "Unknown persons (2-3 male, 1 female)",
            "ipc_sections": "366-A, 376 IPC",
            "crime_type": "Kidnapping and Trafficking",
            "narrative": (
                "Victim (aged 22) reports she was held captive in a house in Model Town, "
                "Jaipur for 3 days starting 18/05/2024. Accused forced her to contact "
                "relatives to arrange money. Phone number 9876543211 used by primary "
                "accused. Victim escaped and reached Civil Lines PS. Accused persons "
                "mentioned names 'Deepak' and 'Vikram' during captivity."
            ),
            "area_type": "urban",
            "status": "Under Investigation",
        },
        {
            "fir_number": "FIR/2024/UP/00789",
            "date": "2024-07-10",
            "police_station": "Hazratganj PS, Lucknow",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "complainant": "Anti-Human Trafficking Unit, UP Police",
            "accused": "Vikram Patel, Deepak Singh, Mohan Yadav",
            "ipc_sections": "370, 371, 120-B, 34 IPC",
            "crime_type": "Trafficking",
            "narrative": (
                "AHTU acting on tip-off raided a warehouse in Industrial Area, Lucknow "
                "on 08/07/2024. Found 4 victims (2 minor). Accused Deepak Singh "
                "was apprehended at the site. Phone records show coordination with "
                "9876543212 (Deepak) and 9876543210 (Vikram). Financial trail shows "
                "transfers from account HDFC-XXXX-1122 to Axis-XXXX-7788."
            ),
            "area_type": "urban",
            "status": "Chargesheet Filed",
        },
    ]

    for rec in ring_firs:
        records.append(rec)

    # Fill remaining with random FIRs
    for _ in range(count - len(ring_firs)):
        state = _state()
        district = _district(state)
        crime = _crime_type()
        ps = f"{fake.city_suffix()} PS, {district}"
        ipc = f"{random.randint(100, 500)} IPC"

        if crime == "Kidnapping":
            narrative = (
                f"Complainant reports {random.choice(['son', 'daughter', 'wife', 'relative'])} "
                f"missing since {_random_date()}. Last seen near {fake.address()}. "
                f"Phone number {fake.msisdn()} not reachable. Suspected kidnapping."
            )
            ipc = "365, 366 IPC"
        elif crime == "Fraud":
            narrative = (
                f"Complainant reports cheating of ₹{random.randint(50000, 500000):,} "
                f"by accused {fake.name()} through {random.choice(['online fraud', 'fake investment', 'cheque bounce'])}. "
                f"Transaction via account {fake.swift()}_{random.randint(1000,9999)}."
            )
        else:
            narrative = (
                f"On {_random_date()}, at {fake.address()}, {crime.lower().replace('_', ' ')} "
                f"incident reported. {random.choice(['Victim', 'Complainant'])} states that "
                f"accused {fake.name()} {random.choice(['assaulted', 'threatened', 'cheated', 'attacked'])} "
                f"the victim. Witnesses present: {random.randint(0, 3)}. "
                f"Injury reported: {random.choice(['minor', 'major', 'none'])}."
            )

        records.append({
            "fir_number": f"FIR/2024/{state[:3].upper()}/{random.randint(10000,99999)}",
            "date": _random_date(),
            "police_station": ps,
            "district": district,
            "state": state,
            "complainant": fake.name(),
            "accused": fake.name(),
            "ipc_sections": ipc,
            "crime_type": crime,
            "narrative": narrative,
            "area_type": _area(),
            "status": random.choice(["Under Investigation", "Chargesheet Filed", "Pending", "Closed"]),
        })

    return records


def _generate_cdr(count: int) -> list[dict]:
    """Call Detail Records — telephonic communication metadata."""
    records = []

    # Inject ring CDRs — showing communication patterns within the ring
    ring_cdr_templates = [
        ("9876543210", "9876543211", "2024-03-10T09:15:00", 245, "Vikram-Anil coordination call"),
        ("9876543210", "9876543212", "2024-03-12T14:30:00", 180, "Vikram-Deepak transport planning"),
        ("9876543211", "9876543213", "2024-05-18T08:00:00", 312, "Anil-Sunita recruitment update"),
        ("9876543210", "9876543214", "2024-06-01T11:45:00", 95, "Vikram-Ravi payment instruction"),
        ("9876543214", "9876543215", "2024-06-05T16:20:00", 167, "Ravi-Kavita account setup"),
        ("9876543212", "9876543216", "2024-07-08T07:30:00", 420, "Deepak-Mohan logistics"),
        ("9876543213", "9876543210", "2024-07-09T22:10:00", 88, "Sunita-Vikram status report"),
        ("9876543210", "9876543216", "2024-07-10T06:00:00", 55, "Vikram-Mohan final instructions"),
        ("9812345601", "9812345604", "2024-05-20T13:00:00", 203, "Alt phone coordination"),
        ("9812345602", "9812345606", "2024-06-10T19:45:00", 142, "Alt phone Anil-Kavita"),
    ]

    for caller, callee, ts, dur, _ in ring_cdr_templates:
        records.append({
            "caller": caller,
            "callee": callee,
            "timestamp": ts,
            "duration_sec": dur,
            "cell_tower_id": f"CTR-{random.randint(1000,9999)}",
            "imei": f"86{random.randint(10**14, 10**15-1)}",
            "call_type": random.choice(["local", "std", "incoming", "outgoing"]),
            "note": _,
        })

    # Fill remaining with random CDRs
    for _ in range(count - len(ring_cdr_templates)):
        caller = fake.msisdn()
        callee = fake.msisdn()
        while callee == caller:
            callee = fake.msisdn()

        records.append({
            "caller": caller,
            "callee": callee,
            "timestamp": _random_datetime(),
            "duration_sec": random.randint(10, 900),
            "cell_tower_id": f"CTR-{random.randint(1000,9999)}",
            "imei": f"86{random.randint(10**14, 10**15-1)}",
            "call_type": random.choice(["local", "std", "incoming", "outgoing"]),
            "note": "",
        })

    return records


def _generate_financial(count: int) -> list[dict]:
    """Financial transaction records — bank transfers, UPI, cash deposits."""
    records = []

    # --- STRUCTURING PATTERN: several sub-threshold transfers (<₹2,00,000) ---
    # that sum to well above the threshold within a short window.
    # Under PMLA, cash transactions ≥₹10 lakh or suspicious structuring
    # triggers reporting. These are just under ₹2 lakh each.
    struct_amounts = [185000, 192000, 178000, 195000, 188000]  # total = 9,38,000
    struct_dates = [
        "2024-06-01", "2024-06-03", "2024-06-05", "2024-06-07", "2024-06-09"
    ]
    for i, (amt, dt) in enumerate(zip(struct_amounts, struct_dates)):
        src_acct, src_name = STRUCT_ACCOUNTS[i % len(STRUCT_ACCOUNTS)]
        dst_acct, dst_name = STRUCT_ACCOUNTS[(i + 1) % len(STRUCT_ACCOUNTS)]
        records.append({
            "transaction_id": f"TXN-STR-{i+1:04d}",
            "date": dt,
            "sender_account": src_acct,
            "sender_name": src_name,
            "receiver_account": dst_acct,
            "receiver_name": dst_name,
            "amount_inr": amt,
            "mode": random.choice(["NEFT", "RTGS", "IMPS"]),
            "remark": random.choice(["business payment", "loan repayment", "family support", ""]),
            "branch": fake.city_suffix(),
            "pattern_flag": "structuring_candidate",
        })

    # --- CIRCULAR TRANSFER: A→B→C→A ---
    circ_amounts = [350000, 280000, 310000]
    circ_dates = ["2024-07-15", "2024-07-18", "2024-07-22"]
    circ_accounts = [CIRC_A, CIRC_B, CIRC_C, CIRC_A]  # wraps back to A
    for i in range(3):
        src_acct, src_name = circ_accounts[i]
        dst_acct, dst_name = circ_accounts[i + 1]
        records.append({
            "transaction_id": f"TXN-CIRC-{i+1:04d}",
            "date": circ_dates[i],
            "sender_account": src_acct,
            "sender_name": src_name,
            "receiver_account": dst_acct,
            "receiver_name": dst_name,
            "amount_inr": circ_amounts[i],
            "mode": "RTGS",
            "remark": "investment return",
            "branch": fake.city_suffix(),
            "pattern_flag": "circular_transfer_candidate",
        })

    # --- Ring financial transfers ---
    ring_transfers = [
        ("9876543210", "Vikram Patel", "HDFC-XXXX-1122", "9876543214", "Ravi Sharma", "SBI-XXXX-1123", 250000, "2024-04-10"),
        ("9876543214", "Ravi Sharma", "SBI-XXXX-1123", "9876543215", "Kavita Gupta", "PNB-XXXX-6677", 180000, "2024-05-05"),
        ("9876543211", "Anil Kumar", "ICICI-XXXX-5566", "9876543212", "Deepak Singh", "Axis-XXXX-7788", 120000, "2024-06-20"),
    ]
    for i, (sp, sn, sa, rp, rn, ra, amt, dt) in enumerate(ring_transfers):
        records.append({
            "transaction_id": f"TXN-RING-{i+1:04d}",
            "date": dt,
            "sender_account": sa,
            "sender_name": sn,
            "receiver_account": ra,
            "receiver_name": rn,
            "amount_inr": amt,
            "mode": random.choice(["NEFT", "IMPS"]),
            "remark": "cash",
            "branch": fake.city_suffix(),
            "pattern_flag": "ring_linked",
        })

    # Fill remaining with random transactions
    needed = count - len(struct_amounts) - 3 - len(ring_transfers)
    for i in range(needed):
        amt = random.randint(5000, 800000)
        flag = ""
        if amt >= 200000:
            flag = "high_value"
        records.append({
            "transaction_id": f"TXN-{random.randint(100000,999999)}",
            "date": _random_date(),
            "sender_account": f"{random.choice(['HDFC','SBI','ICICI','Axis','PNB'])}-XXXX-{random.randint(1000,9999)}",
            "sender_name": fake.name(),
            "receiver_account": f"{random.choice(['HDFC','SBI','ICICI','Axis','PNB'])}-XXXX-{random.randint(1000,9999)}",
            "receiver_name": fake.name(),
            "amount_inr": amt,
            "mode": random.choice(["NEFT", "RTGS", "IMPS", "UPI", "Cash Deposit"]),
            "remark": random.choice(["", "rent", "salary", "loan", "business", "gift"]),
            "branch": fake.city_suffix(),
            "pattern_flag": flag,
        })

    return records


def _generate_surveillance(count: int) -> list[dict]:
    """Surveillance logs — physical tailing, stakeout notes."""
    records = []

    # Ring surveillance entries
    ring_surv = [
        {
            "date": "2024-03-20",
            "time": "14:00-18:30",
            "location": "Lajpat Nagar, New Delhi",
            "subject": "Vikram Patel",
            "description": (
                "Subject observed leaving residence at 14:12. Travelled to "
                "Anand Vihar ISBT by auto. Met with unidentified male (described as "
                "tall, lean, mustache, age ~30) near platform 4. Both boarded "
                "Lucknow-bound bus at 15:45. Tailed but lost at Noida flyover."
            ),
            "officer": "SI Rajesh Verma, AHTU Delhi",
            "vehicle_used": "DL-01-AB-1234 (white Swift Dzire)",
        },
        {
            "date": "2024-05-25",
            "time": "09:00-13:00",
            "location": "Model Town, Jaipur",
            "subject": "Anil Kumar",
            "description": (
                "Subject observed at tea stall near 12, Model Town at 09:15. "
                "Received phone call (9876543211) at 09:22, appeared agitated. "
                "Met with female (subject Sunita Devi, ref FIR/2024/RAJ/00456) "
                "at 10:30. Both walked to auto stand, took shared auto towards "
                "station area."
            ),
            "officer": "Insp. Meena Kumari, Jaipur AHTU",
            "vehicle_used": "RJ-14-CD-5678 (silver Alto)",
        },
        {
            "date": "2024-07-07",
            "time": "06:00-12:00",
            "location": "Industrial Area, Lucknow",
            "subject": "Deepak Singh",
            "description": (
                "Subject arrived at warehouse (Plot 47, Industrial Area) at 06:45 "
                "in a white Bolero (UP-32-XXXX). Opened rear shutter. Two unknown "
                "females and one male seen entering warehouse at 07:30. Subject "
                "made call to 9876543210 at 07:42. At 11:00, subject loaded "
                "cardboard boxes into vehicle. Followed to Charbagh station."
            ),
            "officer": "ASI Puneet Singh, UP AHTU",
            "vehicle_used": "UP-32-EF-9012 (unmarked)",
        },
    ]

    for rec in ring_surv:
        records.append(rec)

    # Fill remaining with random surveillance
    for _ in range(count - len(ring_surv)):
        records.append({
            "date": _random_date(),
            "time": f"{random.randint(5,20):02d}:00-{random.randint(6,23):02d}:{random.randint(0,59):02d}",
            "location": f"{fake.address()}, {_state()}",
            "subject": fake.name(),
            "description": (
                f"Subject observed at {fake.address()} at {random.randint(6,20):02d}:{random.randint(0,59):02d}. "
                f"{random.choice(['Travelled by foot', 'Used private vehicle', 'Used public transport', 'Met unknown individual'])}. "
                f"{random.choice(['No suspicious activity observed', 'Subject appeared to be scanning surroundings', 'Subject made multiple phone calls', 'Subject met with 2 unknown persons'])}."
            ),
            "officer": f"{'SI' if random.random()>0.5 else 'Insp.'} {fake.name()}, {random.choice(['AHTU', 'CID', 'Crime Branch'])} {_state()[:4]}",
            "vehicle_used": f"{random.choice(['DL','MH','UP','RJ','KA'])}-{random.randint(10,99)}-{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}-{random.randint(1000,9999)} ({random.choice(['white','silver','black','red'])} {random.choice(['Swift','i20','Innova','Bolero','Scorpio'])})",
        })

    return records


def _generate_social(count: int) -> list[dict]:
    """Social media profile / activity records."""
    records = []

    # Ring social media footprints
    ring_social = [
        {
            "platform": "WhatsApp",
            "phone_linked": "9876543210",
            "profile_name": "VikramP_45",
            "bio": "Businessman. Delhi.",
            "last_active": "2024-07-10T23:45:00",
            "groups": ["Business Network Delhi", "Lucknow Traders"],
            "notes": "Phone linked to FIR/2024/DEL/00123 accused. Group membership overlaps with Anil Kumar (9876543211).",
        },
        {
            "platform": "WhatsApp",
            "phone_linked": "9876543211",
            "profile_name": "Anil_K",
            "bio": "Marketing | Jaipur",
            "last_active": "2024-05-20T18:30:00",
            "groups": ["Business Network Delhi", "Jaipur Youth Club"],
            "notes": "Shares group 'Business Network Delhi' with Vikram Patel. Active during timeframe of FIR/2024/RAJ/00456.",
        },
        {
            "platform": "Instagram",
            "phone_linked": "9876543215",
            "profile_name": "kavita_g_90",
            "bio": "Mumbai | Fashion",
            "last_active": "2024-06-08T14:20:00",
            "followers": random.randint(200, 2000),
            "notes": "Followed by 9876543214 (Ravi Sharma). Posts location-tagged in Dharavi.",
        },
        {
            "platform": "Facebook",
            "phone_linked": "9876543216",
            "profile_name": "Mohan.Yadav.34",
            "bio": "Agra, Uttar Pradesh",
            "last_active": "2024-07-09T11:00:00",
            "friends_count": random.randint(100, 800),
            "notes": "Friend request sent to Vikram Patel on 2024-06-15. Profile photo matches surveillance description of 'Mohan' from FIR/2024/UP/00789.",
        },
    ]

    for rec in ring_social:
        records.append(rec)

    # Fill remaining
    platforms = ["WhatsApp", "Instagram", "Facebook", "Twitter", "Telegram"]
    for _ in range(count - len(ring_social)):
        records.append({
            "platform": random.choice(platforms),
            "phone_linked": fake.msisdn(),
            "profile_name": fake.user_name(),
            "bio": fake.sentence(nb_words=4),
            "last_active": _random_datetime(),
            "notes": random.choice(["", "Account flagged for suspicious activity", "Linked to multiple unknown numbers", ""]),
        })

    return records


def _generate_criminal_history(count: int) -> list[dict]:
    """Criminal history / antecedent verification records."""
    records = []

    # Ring criminal histories
    ring_history = [
        {
            "person_name": "Vikram Patel",
            "dob": "1988-04-12",
            "aadhaar_masked": "XXXX-XXXX-5678",
            "phone": "9876543210",
            "prior_cases": [
                {"fir": "FIR/2019/DEL/00321", "section": "420 IPC", "status": "Acquitted", "year": 2019},
                {"fir": "FIR/2021/UP/00654", "section": "370 IPC", "status": "Under Trial", "year": 2021},
            ],
            "blacklist_status": "Watch List",
            "notes": "Known associate of Anil Kumar. Previous involvement in fraud case (acquitted). Currently under investigation for trafficking (FIR/2024/DEL/00123, FIR/2024/UP/00789).",
        },
        {
            "person_name": "Anil Kumar",
            "dob": "1992-11-03",
            "aadhaar_masked": "XXXX-XXXX-9012",
            "phone": "9876543211",
            "prior_cases": [
                {"fir": "FIR/2020/RAJ/00112", "section": "366 IPC", "status": "Convicted (2 yr)", "year": 2020},
            ],
            "blacklist_status": "Active Offender",
            "notes": "Previously convicted for kidnapping. Linked to Vikram Patel through shared WhatsApp group and phone records.",
        },
        {
            "person_name": "Ravi Sharma",
            "dob": "1985-07-19",
            "aadhaar_masked": "XXXX-XXXX-3456",
            "phone": "9876543214",
            "prior_cases": [
                {"fir": "FIR/2022/MH/00887", "section": "420, 120B IPC", "status": "Acquitted", "year": 2022},
            ],
            "blacklist_status": "Watch List",
            "notes": "Known financial associate of Vikram Patel. Previous fraud case acquittal. Linked to circular transfer pattern with Sunita Devi and Kavita Gupta.",
        },
    ]

    for rec in ring_history:
        records.append(rec)

    # Fill remaining
    for _ in range(count - len(ring_history)):
        has_prior = random.random() < 0.35
        priors = []
        if has_prior:
            for _ in range(random.randint(1, 3)):
                priors.append({
                    "fir": f"FIR/{random.randint(2015,2023)}/{random.choice(['DL','MH','UP','RJ','KA','TN','WB'])}/{random.randint(100,9999):04d}",
                    "section": f"{random.randint(100,500)} IPC",
                    "status": random.choice(["Convicted", "Acquitted", "Under Trial", "Discharged"]),
                    "year": random.randint(2015, 2023),
                })

        records.append({
            "person_name": fake.name(),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
            "aadhaar_masked": f"XXXX-XXXX-{random.randint(1000,9999)}",
            "phone": fake.msisdn(),
            "prior_cases": priors,
            "blacklist_status": random.choice(["Clear", "Clear", "Clear", "Watch List"]),
            "notes": random.choice(["", "No adverse findings", "Flagged for verification", ""]),
        })

    return records


def _generate_intel(count: int) -> list[dict]:
    """Intelligence bureau / analyst notes — unstructured analytical reports."""
    records = []

    # Ring intelligence summaries
    ring_intel = [
        {
            "report_id": "IB/DEL/2024/INT-001",
            "date": "2024-04-15",
            "classification": "Confidential",
            "source_agency": "Delhi Police AHTU",
            "analyst": "Insp. Rajesh Verma",
            "title": "Organized Trafficking Network — Delhi-Lucknow-Jaipur Corridor",
            "narrative": (
                "Intelligence indicates an organized trafficking network operating "
                "between Delhi, Lucknow, and Jaipur. Key operatives identified: "
                "Vikram Patel (Delhi, 9876543210) —疑似ringleader; Anil Kumar "
                "(Jaipur, 9876543211) — recruiter; Deepak Singh (Lucknow, 9876543212) — "
                "transporter. Financial trail shows regular transfers between linked "
                "accounts. Ring uses multiple phone numbers and burner phones. "
                "Victims are predominantly young women from economically weaker sections. "
                "Estimated operational period: January 2024 onwards."
            ),
            "linked_firs": ["FIR/2024/DEL/00123", "FIR/2024/RAJ/00456", "FIR/2024/UP/00789"],
            "linked_phones": ["9876543210", "9876543211", "9876543212", "9876543213", "9876543214", "9876543215", "9876543216"],
        },
        {
            "report_id": "IB/DEL/2024/INT-002",
            "date": "2024-06-12",
            "classification": "Confidential",
            "source_agency": "Delhi Police AHTU / Financial Intelligence Unit",
            "analyst": "ASI Priya Nair",
            "title": "Financial Modus Operandi — Sub-threshold Structuring",
            "narrative": (
                "Analysis of financial transactions linked to Vikram Patel (HDFC-XXXX-1122) "
                "and associates reveals systematic structuring of transfers below ₹2,00,000 "
                "to avoid mandatory CTR filing. Five transfers between June 1-9, 2024, "
                "totalling ₹9,38,000, were routed through multiple accounts controlled by "
                "ring members. Additionally, a circular transfer pattern identified: "
                "Sunita Devi → Ravi Sharma → Kavita Gupta → Sunita Devi (₹3.5L → ₹2.8L → ₹3.1L). "
                "This pattern suggests layering of illicit funds."
            ),
            "linked_accounts": ["HDFC-XXXX-1122", "ICICI-XXXX-5566", "SBI-XXXX-3344", "Axis-XXXX-7788", "HDFC-XXXX-9900", "SBI-XXXX-1123", "PNB-XXXX-6677"],
            "linked_phones": [],
        },
        {
            "report_id": "IB/UP/2024/INT-003",
            "date": "2024-07-11",
            "classification": "Restricted",
            "source_agency": "UP AHTU / SOT",
            "analyst": "Insp. Amit Tripathi",
            "title": "Post-Raid Assessment — Lucknow Warehouse Operation",
            "narrative": (
                "Following the raid on Plot 47, Industrial Area, Lucknow on 08/07/2024 "
                "(ref FIR/2024/UP/00789), further analysis reveals the warehouse was rented "
                "by Deepak Singh (9876543212) using a fake ID. Financial records show rent "
                "of ₹25,000/month paid from Axis-XXXX-7788. Phone records indicate coordination "
                "with Vikram Patel and Mohan Yadav. Mohan Yadav (9876543216) was identified "
                "from surveillance as the person who loaded victims into vehicles. "
                "Victims rescued: 4 (2 minors). All from Rajasthan and UP."
            ),
            "linked_firs": ["FIR/2024/UP/00789"],
            "linked_phones": ["9876543212", "9876543210", "9876543216"],
        },
    ]

    for rec in ring_intel:
        records.append(rec)

    # Fill remaining with random intel
    for _ in range(count - len(ring_intel)):
        records.append({
            "report_id": f"IB/{random.choice(['DL','MH','UP','RJ','KA'])}/2024/INT-{random.randint(100,999):03d}",
            "date": _random_date(),
            "classification": random.choice(["Confidential", "Restricted", "Unclassified"]),
            "source_agency": random.choice(["Delhi Police CID", "Maharashtra ATS", "UP STF", "Rajasthan SOG", "NIA"]),
            "analyst": f"{'Insp.' if random.random()>0.5 else 'ASI'} {fake.name()}",
            "title": fake.sentence(nb_words=6),
            "narrative": (
                f"{fake.paragraph(nb_sentences=3)} "
                f"Phone records indicate communication with {fake.msisdn()}. "
                f"Financial trail shows transfer of ₹{random.randint(50000,500000):,} "
                f"on {_random_date()}. Further investigation recommended."
            ),
            "linked_firs": [f"FIR/2024/{random.choice(['DL','MH','UP','RJ'])}/{random.randint(1000,9999):04d}"],
            "linked_phones": [fake.msisdn() for _ in range(random.randint(1, 4))],
        })

    return records


# ---------------------------------------------------------------------------
# Main — generate all 7 source files
# ---------------------------------------------------------------------------
GENERATORS = {
    "fir": _generate_fir,
    "cdr": _generate_cdr,
    "financial": _generate_financial,
    "surveillance": _generate_surveillance,
    "social": _generate_social,
    "criminal_history": _generate_criminal_history,
    "intel": _generate_intel,
}

RECORD_COUNTS = {
    "fir": 18,
    "cdr": 25,
    "financial": 28,
    "surveillance": 18,
    "social": 20,
    "criminal_history": 18,
    "intel": 16,
}


def main():
    print("Generating synthetic data (seed=42)...")
    for name, gen_func in GENERATORS.items():
        n = RECORD_COUNTS[name]
        records = gen_func(n)
        out_path = RAW_DIR / f"{name}_records.json"
        out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {out_path.name}: {len(records)} records")
    print("Done.")


if __name__ == "__main__":
    main()
