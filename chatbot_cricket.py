import random
import re
import threading
import webbrowser
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# ==============================================================================
# 1. COMPLETE CRICKET DATABASE
# ==============================================================================

TICKER_ITEMS = [
    {"label": "🔴 LIVE: AUS vs ENG 3rd ODI (Hobart) — Series 1-1 Decider", "query": "Current live matches today"},
    {"label": "🔴 LIVE/UPCOMING: NZ vs IND 1st Test (Wellington)", "query": "India vs New Zealand Test schedule"},
    {"label": "🔴 LIVE: Syed Mushtaq Ali Trophy (SMAT 2026)", "query": "Current live matches today"},
    {"label": "🏆 WTC 2025–27 Leaders: NZ (72.22%) & SA (71.43%)", "query": "Show WTC points table and ICC rankings"},
    {"label": "🚀 Upcoming: 2027 ODI World Cup & LA28 Olympic T20", "query": "Upcoming cricket formats and ICC events"},
]

CURRENT_MATCHES = [
    {
        "badge": "LIVE • DECIDER",
        "badge_type": "live",
        "format": "ODI",
        "title": "Australia vs England — 3rd ODI (Series tied 1-1)",
        "detail": "Bellerive Oval (Ninja Stadium), Hobart • Nov 18, 2026",
        "status": "England posted 321/9+ batting first (Ben Duckett 133). Series decider underway.",
    },
    {
        "badge": "STARTING • WTC",
        "badge_type": "live",
        "format": "TEST",
        "title": "New Zealand vs India — 1st Test (WTC 2025–27)",
        "detail": "Cello Basin Reserve, Wellington • Nov 18–23, 2026",
        "status": "Opening Test of the 2-match series following India's 22-run win in the 5th ODI.",
    },
    {
        "badge": "LIVE • DOMESTIC T20",
        "badge_type": "live",
        "format": "T20",
        "title": "Syed Mushtaq Ali Trophy (SMAT) 2026",
        "detail": "Across India • Nov 18, 2026",
        "status": "Bengal beat Jharkhand by 7 wkts (Easwaran 61*); Chhattisgarh beat Odisha (Vikalp Tiwari 119 off 56); Kerala vs Andhra & Delhi vs Bihar active.",
    },
    {
        "badge": "ONGOING GLOBAL",
        "badge_type": "live",
        "format": "MULTI",
        "title": "Active Global Series & Leagues (Nov 2026)",
        "detail": "WBBL 2026 • Abu Dhabi T10 2026 • SL in PAK • BAN in SA",
        "status": "Women's Big Bash League (T20), Abu Dhabi T10 (10-over format), Sri Lanka in Pakistan (Tests), and Bangladesh in South Africa.",
    },
]

UPCOMING_MATCHES = [
    {
        "badge": "NOV 20–23, 2026",
        "badge_type": "upcoming",
        "format": "ONE-DAY",
        "title": "India A — DP World Men's Asia Cup Rising Stars",
        "detail": "Doha, Qatar",
        "status": "vs Nepal (Nov 20) • vs Pakistan Shaheens (Nov 22) • vs UAE (Nov 23).",
    },
    {
        "badge": "NOV 21 – DEC 2, 2026",
        "badge_type": "upcoming",
        "format": "T20I",
        "title": "Australia vs England — 5-Match T20I Series",
        "detail": "MCG, Carrara, Brisbane, Sydney, Canberra",
        "status": "1st T20I: Nov 21 (MCG) • 2nd: Nov 24 • 3rd: Nov 27 • 4th: Nov 29 • 5th: Dec 2.",
    },
    {
        "badge": "NOV 26 – DEC 1, 2026",
        "badge_type": "upcoming",
        "format": "TEST",
        "title": "New Zealand vs India — 2nd Test",
        "detail": "Hagley Oval, Christchurch",
        "status": "Second and final Test of India's 2026 New Zealand tour.",
    },
    {
        "badge": "DEC 9, 2026 – JAN 8, 2027",
        "badge_type": "upcoming",
        "format": "T20",
        "title": "KFC Big Bash League (BBL|16)",
        "detail": "Australia",
        "status": "Australia's premier men's domestic T20 franchise tournament.",
    },
    {
        "badge": "DEC 13–27, 2026",
        "badge_type": "upcoming",
        "format": "ODI + T20I",
        "title": "Sri Lanka Tour of India 2026",
        "detail": "Delhi, Bengaluru, Ahmedabad, Rajkot, Cuttack, Pune",
        "status": "3 ODIs (Dec 13, 16, 19) followed by 3 T20Is (Dec 22, 24, 27).",
    },
    {
        "badge": "JAN 3–9, 2027",
        "badge_type": "upcoming",
        "format": "ODI",
        "title": "Zimbabwe Tour of India 2027",
        "detail": "India • 3-Match ODI Series",
        "status": "Early January white-ball series ahead of India's home Test block.",
    },
    {
        "badge": "JAN 21 – MAR 3, 2027",
        "badge_type": "upcoming",
        "format": "TEST",
        "title": "Border-Gavaskar Trophy: Australia in India",
        "detail": "India • 5-Match Test Series",
        "status": "Marquee 5-Test series closing India's 2025–27 World Test Championship cycle.",
    },
]

UPCOMING_FORMATS_AND_EVENTS = [
    {
        "badge": "FEB 2027 • INAUGURAL",
        "badge_type": "future",
        "format": "WOMEN'S T20",
        "title": "2027 ICC Women's Champions Trophy (India)",
        "detail": "Hosted by India • 6 Teams, 16 Matches",
        "status": "Brand-new global women's T20 Champions Trophy format making its debut.",
    },
    {
        "badge": "SPRING 2027",
        "badge_type": "future",
        "format": "FRANCHISE T20",
        "title": "WPL 2027 & IPL 2027 Seasons",
        "detail": "India • 20-Over Franchise Leagues",
        "status": "RCB Women & RCB Men enter 2027 as defending champions of both leagues.",
    },
    {
        "badge": "JUNE 2027",
        "badge_type": "future",
        "format": "TEST (WTC)",
        "title": "2027 ICC World Test Championship (WTC) Final",
        "detail": "The Oval, London • 5-Day Test Championship",
        "status": "Top 2 teams on the 2025–27 WTC standings compete for the Test Mace.",
    },
    {
        "badge": "OCT 2 – NOV 21, 2027",
        "badge_type": "future",
        "format": "ODI (50-OV)",
        "title": "2027 ICC Men's Cricket World Cup",
        "detail": "South Africa, Zimbabwe & Namibia • 14 Teams, 54 Matches",
        "status": "Returns to the 2-groups-of-7 + Super Six + Knockouts 50-over ODI format.",
    },
    {
        "badge": "JULY 2028 • OLYMPICS",
        "badge_type": "future",
        "format": "OLYMPIC T20",
        "title": "LA28 Summer Olympics — Olympic Cricket",
        "detail": "Los Angeles, USA • T20 Format",
        "status": "Cricket returns to the Olympic Games for the first time since 1900 in T20 format.",
    },
    {
        "badge": "OCT 12 – NOV 12, 2028",
        "badge_type": "future",
        "format": "T20I (20 TEAMS)",
        "title": "2028 ICC Men's T20 World Cup",
        "detail": "Australia & New Zealand • 20 Teams",
        "status": "4 groups of 5 leading into Super 8s and Knockouts (Women's T20 WC 2028 in Pakistan).",
    },
    {
        "badge": "SPECIALTY FORMATS",
        "badge_type": "future",
        "format": "T10 / 100-BALL",
        "title": "Ultra-Short Formats: Abu Dhabi T10 & The Hundred",
        "detail": "60-Ball T10 • 100-Ball Innings",
        "status": "Rapid-fire formats designed for high-intensity 90-to-150 minute broadcasts.",
    },
]

# ==============================================================================
# PLAYERS WITH COMPLETE BIODATA + STATS
# ==============================================================================

PLAYERS = [
    {
        "id": "kohli",
        "keywords": ["virat", "kohli", "king", "chiku", "cheeku"],
        "name": "Virat Kohli",
        "initials": "VK",
        "gradient": "linear-gradient(135deg, #dc2626, #991b1b)",
        "country": "India",
        "team": "RCB (IPL)",
        "role": "Top-Order Batter",
        "status": "Active: ODI & IPL",
        "biodata": {
            "full_name": "Virat Kohli",
            "dob": "5 November 1988 (Age 38)",
            "birthplace": "New Delhi, India",
            "height": "5 ft 9 in (175 cm)",
            "jersey": "#18",
            "nicknames": "Cheeku, King Kohli, Chase Master",
            "batting": "Right-handed",
            "bowling": "Right-arm medium",
            "debuts": "ODI: 18 Aug 2008 (v SL) • T20I: 12 Jun 2010 (v ZIM) • Test: 20 Jun 2011 (v WI)",
            "teams": "India, Delhi, Royal Challengers Bengaluru (2008–Present)",
            "family": "Parents: Prem Nath & Saroj Kohli • Spouse: Anushka Sharma (m. 2017)",
        },
        "stats": {
            "TEST": {"main": "9,230 Runs", "sub": "30x 100s | Avg 46.85"},
            "ODI": {"main": "15,100+ Runs", "sub": "55x 100s | Avg ~58"},
            "T20I": {"main": "4,188 Runs", "sub": "SR 137.0 | Ret. '24"},
            "IPL": {"main": "9,300+ Runs", "sub": "All-Time #1 | 2x Champ"},
        },
        "highlights": [
            "Only player in IPL history to represent one single franchise (RCB) since 2008, winning back-to-back titles in 2025 & 2026.",
            "Holds the all-time world record for most ODI centuries (surpassing Sachin Tendulkar's 49).",
            "Captained India to U-19 World Cup glory (2008) and led India in 68 Tests (most successful Indian Test skipper).",
        ],
    },
    {
        "id": "rohit",
        "keywords": ["rohit", "sharma", "hitman", "shana"],
        "name": "Rohit Sharma",
        "initials": "RS",
        "gradient": "linear-gradient(135deg, #2563eb, #1e40af)",
        "country": "India",
        "team": "Mumbai Indians (IPL)",
        "role": "Opening Batter",
        "status": "Active: ODI & IPL",
        "biodata": {
            "full_name": "Rohit Gurunath Sharma",
            "dob": "30 April 1987 (Age 39)",
            "birthplace": "Nagpur, Maharashtra, India",
            "height": "5 ft 8 in (173 cm)",
            "jersey": "#45",
            "nicknames": "Hitman, Ro, Shana",
            "batting": "Right-handed",
            "bowling": "Right-arm off-break",
            "debuts": "ODI: 23 Jun 2007 (v IRE) • T20I: 19 Sep 2007 (v ENG) • Test: 6 Nov 2013 (v WI)",
            "teams": "India, Mumbai, Deccan Chargers (2008–10), Mumbai Indians (2011–Present)",
            "family": "Parents: Gurunath & Purnima Sharma • Spouse: Ritika Sajdeh (m. 2015)",
        },
        "stats": {
            "TEST": {"main": "4,301 Runs", "sub": "12x 100s | Ret. '25"},
            "ODI": {"main": "12,150+ Runs", "sub": "3x 200s | HS 264"},
            "T20I": {"main": "4,231 Runs", "sub": "5x 100s | Ret. '24"},
            "IPL": {"main": "6,900+ Runs", "sub": "6x IPL Winner"},
        },
        "highlights": [
            "Only cricketer in history with three ODI double centuries, including the highest ODI score (264 vs SL).",
            "Captained India to undefeated ICC triumphs in the 2024 T20 World Cup & 2025 Champions Trophy.",
            "Led Mumbai Indians to 5 IPL titles (2013, 2015, 2017, 2019, 2020) plus 1 title with Deccan Chargers.",
        ],
    },
    {
        "id": "bumrah",
        "keywords": ["bumrah", "jasprit", "boom", "jassi"],
        "name": "Jasprit Bumrah",
        "initials": "JB",
        "gradient": "linear-gradient(135deg, #0ea5e9, #0369a1)",
        "country": "India",
        "team": "Mumbai Indians (IPL)",
        "role": "Right-Arm Fast Bowler",
        "status": "All-Format Spearhead",
        "biodata": {
            "full_name": "Jasprit Jasbir Singh Bumrah",
            "dob": "6 December 1993 (Age 32)",
            "birthplace": "Ahmedabad, Gujarat, India",
            "height": "5 ft 10 in (178 cm)",
            "jersey": "#93",
            "nicknames": "Boom Boom, Jassi",
            "batting": "Right-handed",
            "bowling": "Right-arm fast",
            "debuts": "ODI: 23 Jan 2016 (v AUS) • T20I: 26 Jan 2016 (v AUS) • Test: 5 Jan 2018 (v SA)",
            "teams": "India, Gujarat, Mumbai Indians (2013–Present)",
            "family": "Parents: Jasbir & Daljit Bumrah • Spouse: Sanjana Ganesan (m. 2021)",
        },
        "stats": {
            "TEST": {"main": "205+ Wkts", "sub": "Avg ~19.4 | Elite"},
            "ODI": {"main": "149+ Wkts", "sub": "Econ 4.59"},
            "T20I": {"main": "100+ Wkts", "sub": "2x T20 WC Champ"},
            "IPL": {"main": "165+ Wkts", "sub": "Econ ~7.3 | Lethal"},
        },
        "highlights": [
            "First bowler to reach ICC No. 1 across all 3 formats & first Indian bowler with 100+ wickets in Tests, ODIs, and T20Is.",
            "Player of the Match in the 2026 T20 World Cup Final & Player of the Tournament in 2024 T20 WC.",
            "Famous for his unique slingy action and pinpoint 145+ km/h death-over yorkers.",
        ],
    },
    {
        "id": "dhoni",
        "keywords": ["dhoni", "msd", "mahendra", "thala", "mahi"],
        "name": "MS Dhoni",
        "initials": "MSD",
        "gradient": "linear-gradient(135deg, #eab308, #ca8a04)",
        "country": "India",
        "team": "Chennai Super Kings (IPL)",
        "role": "Wicketkeeper-Batter",
        "status": "IPL Legend",
        "biodata": {
            "full_name": "Mahendra Singh Dhoni",
            "dob": "7 July 1981 (Age 45)",
            "birthplace": "Ranchi, Jharkhand (then Bihar), India",
            "height": "5 ft 9 in (175 cm)",
            "jersey": "#7",
            "nicknames": "Mahi, Captain Cool, Thala, MSD",
            "batting": "Right-handed",
            "bowling": "Right-arm medium",
            "debuts": "ODI: 23 Dec 2004 (v BAN) • Test: 2 Dec 2005 (v SL) • T20I: 1 Dec 2006 (v SA)",
            "teams": "India, Bihar/Jharkhand, Chennai Super Kings, Rising Pune Supergiant",
            "family": "Parents: Pan Singh & Devaki Devi • Spouse: Sakshi Singh Rawat (m. 2010)",
        },
        "stats": {
            "TEST": {"main": "4,876 Runs", "sub": "294 Dismissals | HS 224"},
            "ODI": {"main": "10,773 Runs", "sub": "Avg 50.57 | Finisher"},
            "T20I": {"main": "1,617 Runs", "sub": "SR 126.1 | 91 Dismissals"},
            "IPL": {"main": "5,439+ Runs", "sub": "5x IPL Titles (CSK)"},
        },
        "highlights": [
            "Only captain in cricket history to win all 3 ICC white-ball trophies (2007 T20 WC, 2011 ODI WC, 2013 CT).",
            "Led Chennai Super Kings to 5 IPL titles (2010, 2011, 2018, 2021, 2023).",
            "Holds the world record for most international stumpings (195) and iconic Helicopter Shot mastery.",
        ],
    },
    {
        "id": "mandhana",
        "keywords": ["smriti", "mandhana", "queen"],
        "name": "Smriti Mandhana",
        "initials": "SM",
        "gradient": "linear-gradient(135deg, #e11d48, #9f1239)",
        "country": "India (Women)",
        "team": "RCB Women (WPL)",
        "role": "Opening Batter & Captain",
        "status": "All-Format Captain",
        "biodata": {
            "full_name": "Smriti Shriniwas Mandhana",
            "dob": "18 July 1996 (Age 30)",
            "birthplace": "Mumbai, Maharashtra (Raised in Sangli), India",
            "height": "5 ft 4 in (163 cm)",
            "jersey": "#18",
            "nicknames": "Queen of Indian Cricket, Smriti",
            "batting": "Left-handed",
            "bowling": "Right-arm medium / off-break",
            "debuts": "T20I: 5 Apr 2013 (v BAN) • ODI: 10 Apr 2013 (v BAN) • Test: 13 Aug 2014 (v ENG)",
            "teams": "India Women, Maharashtra, RCB Women (WPL), Southern Brave, Adelaide Strikers",
            "family": "Parents: Shriniwas & Smita Mandhana • Brother: Shravan Mandhana",
        },
        "stats": {
            "TEST": {"main": "788+ Runs", "sub": "2x 100s | Avg 52.5"},
            "ODI": {"main": "5,443+ Runs", "sub": "14x 100s | Avg 47.3"},
            "T20I": {"main": "4,923+ Runs", "sub": "2x 100s | 37x 50s"},
            "WPL": {"main": "1,023+ Runs", "sub": "2x WPL Champ ('24,'26)"},
        },
        "highlights": [
            "Captained RCB Women to WPL titles in 2024 and 2026 (scoring 87 off 41 in the 2026 Final + Orange Cap).",
            "Key star of India's 2025 ICC Women's ODI World Cup triumph & scored the fastest ODI century by an Indian (50 balls).",
            "First Indian woman to score international centuries in Tests, ODIs, and T20Is.",
        ],
    },
    {
        "id": "gill",
        "keywords": ["shubman", "gill", "prince"],
        "name": "Shubman Gill",
        "initials": "SG",
        "gradient": "linear-gradient(135deg, #14b8a6, #0f766e)",
        "country": "India",
        "team": "Gujarat Titans (IPL)",
        "role": "Top-Order Batter & Captain",
        "status": "India Test & ODI Captain",
        "biodata": {
            "full_name": "Shubman Gill",
            "dob": "8 September 1999 (Age 27)",
            "birthplace": "Fazilka, Punjab, India",
            "height": "6 ft 1 in (185 cm)",
            "jersey": "#77 (India) / #7 (GT)",
            "nicknames": "Prince, Shubh",
            "batting": "Right-handed",
            "bowling": "Right-arm off-spin",
            "debuts": "ODI: 31 Jan 2019 (v NZ) • Test: 26 Dec 2020 (v AUS) • T20I: 3 Jan 2023 (v SL)",
            "teams": "India, Punjab, Kolkata Knight Riders (2018–21), Gujarat Titans (2022–Present)",
            "family": "Parents: Lakhwinder Singh Gill & Keart Gill • Sister: Shahneel Gill",
        },
        "stats": {
            "TEST": {"main": "2,500+ Runs", "sub": "HS 269 | Test Capt."},
            "ODI": {"main": "2,700+ Runs", "sub": "Avg ~59 | HS 208"},
            "T20I": {"main": "600+ Runs", "sub": "HS 126*"},
            "IPL": {"main": "4,200+ Runs", "sub": "Orange Cap '23 (890)"},
        },
        "highlights": [
            "Appointed India's Test & ODI Captain in 2025; smashed 269 & 161 in the same Test at Edgbaston.",
            "Youngest batter to score an ODI double century (208 vs New Zealand).",
            "Captained Gujarat Titans to the IPL 2026 Final (scoring 732 runs in IPL 2026).",
        ],
    },
    {
        "id": "cummins",
        "keywords": ["pat", "cummins"],
        "name": "Pat Cummins",
        "initials": "PC",
        "gradient": "linear-gradient(135deg, #f59e0b, #b45309)",
        "country": "Australia",
        "team": "Sunrisers Hyderabad (IPL)",
        "role": "Fast Bowler & Captain",
        "status": "Australia Test & ODI Capt.",
        "biodata": {
            "full_name": "Patrick James Cummins",
            "dob": "8 May 1993 (Age 33)",
            "birthplace": "Westmead, New South Wales, Australia",
            "height": "6 ft 4 in (192 cm)",
            "jersey": "#30",
            "nicknames": "Cummo, Silencer, Postman Pat",
            "batting": "Right-handed",
            "bowling": "Right-arm fast",
            "debuts": "T20I: 13 Oct 2011 (v SA) • ODI: 19 Oct 2011 (v SA) • Test: 17 Nov 2011 (v SA)",
            "teams": "Australia, New South Wales, KKR, Delhi Daredevils, Sunrisers Hyderabad (2024–Present)",
            "family": "Parents: Peter & Maria Cummins • Spouse: Becky Boston (m. 2022)",
        },
        "stats": {
            "TEST": {"main": "328+ Wkts", "sub": "Avg 22.51 | 14x 5w"},
            "ODI": {"main": "143+ Wkts", "sub": "2023 WC Winner"},
            "T20I": {"main": "66+ Wkts", "sub": "2x WC Hat-tricks"},
            "IPL": {"main": "65+ Wkts", "sub": "SRH Captain | 14-ball 50"},
        },
        "highlights": [
            "Captained Australia to both the 2023 World Test Championship & 2023 ODI World Cup titles.",
            "Took two consecutive hat-tricks in the 2024 ICC T20 World Cup.",
            "Joint-fastest IPL fifty (14 balls) and spearheaded SRH's aggressive batting revolution.",
        ],
    },
    {
        "id": "rashid",
        "keywords": ["rashid", "khan"],
        "name": "Rashid Khan",
        "initials": "RK",
        "gradient": "linear-gradient(135deg, #8b5cf6, #5b21b6)",
        "country": "Afghanistan",
        "team": "Gujarat Titans (IPL)",
        "role": "Leg-Spin All-Rounder",
        "status": "AFG T20I Captain",
        "biodata": {
            "full_name": "Rashid Khan Arman",
            "dob": "20 September 1998 (Age 28)",
            "birthplace": "Nangarhar Province, Afghanistan",
            "height": "5 ft 9 in (175 cm)",
            "jersey": "#19",
            "nicknames": "Rashid, Magician",
            "batting": "Right-handed",
            "bowling": "Right-arm leg-break googly",
            "debuts": "ODI: 18 Oct 2015 (v ZIM) • T20I: 26 Oct 2015 (v ZIM) • Test: 14 Jun 2018 (v IND)",
            "teams": "Afghanistan, Sunrisers Hyderabad (2017–21), Gujarat Titans (2022–Present), Adelaide Strikers",
            "family": "Grew up in a family of 11 siblings in Jalalabad / Nangarhar",
        },
        "stats": {
            "TEST": {"main": "45+ Wkts", "sub": "Avg ~20.4 | 4x 5w"},
            "ODI": {"main": "198+ Wkts", "sub": "Avg ~19.8 | Econ 4.2"},
            "T20I": {"main": "191+ Wkts", "sub": "All-Time T20I #1"},
            "IPL": {"main": "155+ Wkts", "sub": "Econ ~6.8 | 700+ T20 Wkts"},
        },
        "highlights": [
            "Became the first bowler in cricket history to reach 700 T20 wickets (during 2026 T20 WC).",
            "Captained Afghanistan to their maiden ICC World Cup semi-final in T20 WC 2024.",
            "Youngest Test captain in cricket history (aged 20) & fastest to 100 ODI wickets.",
        ],
    },
    {
        "id": "samson",
        "keywords": ["sanju", "samson"],
        "name": "Sanju Samson",
        "initials": "SS",
        "gradient": "linear-gradient(135deg, #ec4899, #9d174d)",
        "country": "India",
        "team": "Chennai Super Kings (IPL)",
        "role": "Wicketkeeper-Batter",
        "status": "2x T20 WC Champion",
        "biodata": {
            "full_name": "Sanju Viswanath Samson",
            "dob": "11 November 1994 (Age 32)",
            "birthplace": "Pulluvila, Thiruvananthapuram, Kerala, India",
            "height": "5 ft 7 in (170 cm)",
            "jersey": "#9",
            "nicknames": "Chettan, Sanju Baba",
            "batting": "Right-handed",
            "bowling": "Right-arm off-spin",
            "debuts": "T20I: 19 Jul 2015 (v ZIM) • ODI: 23 Jul 2021 (v SL) • Test: —",
            "teams": "India, Kerala, KKR, Delhi Daredevils, Rajasthan Royals (2013–25), CSK (2026–Present)",
            "family": "Parents: Samson Viswanath & Lijy Viswanath • Spouse: Charulatha Samson (m. 2018)",
        },
        "stats": {
            "TEST": {"main": "3,888 FC", "sub": "11x FC 100s | Kerala"},
            "ODI": {"main": "510 Runs", "sub": "Avg 56.66 | HS 108"},
            "T20I": {"main": "1,842+ Runs", "sub": "3x 100s | POTT WC '26"},
            "IPL": {"main": "5,000+ Runs", "sub": "3x 100s | Ex-RR Capt."},
        },
        "highlights": [
            "Player of the Tournament in India's 2026 T20 World Cup triumph (321 runs, avg 80.25, SR 199.37, incl. 89 in Final).",
            "First Indian wicketkeeper to score three T20I centuries (all in 2024).",
            "Moved to Chennai Super Kings in IPL 2026 after captaining Rajasthan Royals to the 2022 IPL Final.",
        ],
    },
]

# ==============================================================================
# WTC STANDINGS, ICC RANKINGS, STADIUMS, RIVALRIES, GLOSSARY, QUIZ
# ==============================================================================

WTC_STANDINGS = [
    ["1", "New Zealand", "6", "52", "72.22%"],
    ["2", "South Africa", "7", "60", "71.43%"],
    ["3", "Australia", "13", "108", "69.23%"],
    ["4", "India", "11", "68", "51.52%"],
    ["5", "Bangladesh", "8", "44", "45.83%"],
    ["6", "England", "16", "74", "38.54%"],
    ["7", "Sri Lanka", "7", "28", "33.33%"],
    ["8", "West Indies", "14", "46", "27.38%"],
    ["9", "Pakistan", "10", "9", "7.50%"],
]

ICC_TEAM_RANKINGS = [
    ["1", "South Africa (124)", "India (116)", "England (269)"],
    ["2", "Australia (122)", "New Zealand (107)", "India (267)"],
    ["3", "New Zealand (106)", "South Africa (104)", "Australia (260)"],
    ["4", "India (105)", "Pakistan (104)", "New Zealand (248)"],
    ["5", "England (102)", "Australia (101)", "South Africa (243)"],
]

STADIUMS = [
    {
        "badge": "INDIA • 132,000 CAPACITY",
        "badge_type": "future",
        "format": "ALL FORMATS",
        "title": "Narendra Modi Stadium, Ahmedabad",
        "detail": "World's Largest Cricket Stadium • Avg T20 1st Inn: 175–185",
        "status": "True bounce & fast outfield; red-soil pitches help pacers/spinners, black-soil favors high chases. Hosted the 2026 T20 WC Final.",
    },
    {
        "badge": "INDIA • CHASING PARADISE",
        "badge_type": "upcoming",
        "format": "IPL / ODI / TEST",
        "title": "Wankhede Stadium, Mumbai",
        "detail": "Avg T20 1st Inn: 180–195 • Short Boundaries",
        "status": "Red-soil pitch offers early sea-breeze swing for pacers, then turns into a batting paradise with heavy evening dew.",
    },
    {
        "badge": "NEW ZEALAND • WINDY PACE",
        "badge_type": "live",
        "format": "TEST / ODI",
        "title": "Basin Reserve, Wellington",
        "detail": "Avg Test 1st Inn: ~315 • Hosting NZ vs IND 1st Test",
        "status": "Famous for strong crosswinds and green seam early on Day 1 before flattening out nicely on Days 2–4.",
    },
    {
        "badge": "AUSTRALIA • BOWL FIRST?",
        "badge_type": "live",
        "format": "ODI / T20",
        "title": "Bellerive Oval (Ninja Stadium), Hobart",
        "detail": "Avg ODI 1st Inn: ~275 • Hosting AUS vs ENG 3rd ODI",
        "status": "True Tasmanian bounce with crisp carry; seamers get movement under lights.",
    },
    {
        "badge": "ENGLAND • HOME OF CRICKET",
        "badge_type": "upcoming",
        "format": "TEST / ODI",
        "title": "Lord's Cricket Ground, London",
        "detail": "Famous 2.5m Slope • Hosted WTC 2025 Final",
        "status": "Overcast conditions assist lateral swing; the iconic slope forces batters & bowlers to adjust lines constantly.",
    },
    {
        "badge": "AUSTRALIA • BOXING DAY",
        "badge_type": "upcoming",
        "format": "TEST / T20I",
        "title": "Melbourne Cricket Ground (MCG)",
        "detail": "100,000+ Capacity • Hosting AUS vs ENG 1st T20I (Nov 21)",
        "status": "Massive square boundaries reward clever gaps & hard running; drop-in pitches offer fair pace and bounce.",
    },
]

RIVALRIES_AND_RECORDS = [
    ["India vs Australia (Tests)", "Border-Gavaskar Trophy • Next: 5 Tests in India (Jan–Mar 2027)"],
    ["India vs Pakistan (ICC Events)", "India holds dominant World Cup & Champions Trophy head-to-head record"],
    ["MI vs CSK (IPL El Clásico)", "5 IPL Titles each (10 combined championships); most iconic IPL rivalry"],
    ["Highest Individual ODI Score", "Rohit Sharma — 264 off 173 balls (vs Sri Lanka, Eden Gardens, 2014)"],
    ["Most ODI Centuries", "Virat Kohli — 55+ ODI hundreds (All-Time World Record)"],
    ["Most Test Runs / Wickets", "Sachin Tendulkar (15,921 runs) • Muttiah Muralitharan (800 wickets)"],
    ["Most T20 Wickets (All-Time)", "Rashid Khan — 700+ T20 wickets (first bowler ever to reach 700)"],
    ["2026 IPL / WPL Double", "Royal Challengers Bengaluru (RCB) became the 1st franchise to win both IPL & WPL in 2026"],
]

GLOSSARY = [
    ["Googly", "A leg-spinner's deceptive delivery that looks like a leg-break but spins inward like an off-break."],
    ["Yorker", "A full delivery pitched right at the batter's toes/creases, famously mastered by Jasprit Bumrah."],
    ["Powerplay", "Fielding restriction phase (Overs 1–6 in T20/IPL; Overs 1–10 in ODI) allowing only 2 fielders outside the 30-yard circle."],
    ["Free Hit", "Awarded after a foot/waist no-ball in white-ball cricket; the batter cannot be dismissed except by run-out."],
    ["Impact Player", "IPL rule allowing 1 tactical substitute from 5 named bench players to replace a starting XI player mid-match."],
    ["DRS", "Decision Review System using ball-tracking & UltraEdge to overturn umpiring errors (IPL allows reviewing wides & no-balls too)."],
    ["DLS Method", "Duckworth-Lewis-Stern formula recalculating rain-affected ODI/T20 targets based on overs & wickets left."],
    ["Super Over", "A 6-ball (2-wicket max) tiebreaker played when a T20 or knockout match finishes tied."],
]

QUIZ_QUESTIONS = [
    {
        "question": "Which franchise became the first in history to win BOTH the IPL and WPL titles in 2026?",
        "options": ["Mumbai Indians", "Royal Challengers Bengaluru", "Chennai Super Kings", "Gujarat Titans"],
        "answer": 1,
        "explain": "RCB Men (IPL 2026) and RCB Women (WPL 2026) completed an unprecedented double in 2026!",
    },
    {
        "question": "Who won Player of the Tournament in India's 2026 ICC Men's T20 World Cup triumph?",
        "options": ["Virat Kohli", "Jasprit Bumrah", "Sanju Samson", "Suryakumar Yadav"],
        "answer": 2,
        "explain": "Sanju Samson scored 321 runs at an average of 80.25 and strike rate of 199.37 (including 89 in the final)!",
    },
    {
        "question": "Which country won the 2025 ICC World Test Championship (WTC) Final at Lord's?",
        "options": ["Australia", "India", "New Zealand", "South Africa"],
        "answer": 3,
        "explain": "South Africa defeated Australia by 5 wickets at Lord's in June 2025 to lift their first WTC Mace.",
    },
    {
        "question": "Which cricketer became the first bowler ever to reach 700 T20 wickets in 2026?",
        "options": ["Jasprit Bumrah", "Rashid Khan", "Sunil Narine", "Yuzvendra Chahal"],
        "answer": 1,
        "explain": "Afghanistan's Rashid Khan reached 700 T20 wickets during the 2026 T20 World Cup.",
    },
    {
        "question": "In which city will cricket make its Olympic Games return at the 2028 Summer Olympics?",
        "options": ["Brisbane", "London", "Los Angeles", "Ahmedabad"],
        "answer": 2,
        "explain": "T20 cricket will return to the Olympics at LA28 (Los Angeles 2028) for the first time since 1900.",
    },
    {
        "question": "Which three countries will co-host the 2027 ICC Men's ODI Cricket World Cup?",
        "options": [
            "India, Sri Lanka & Bangladesh",
            "South Africa, Zimbabwe & Namibia",
            "Australia & New Zealand",
            "England, Ireland & Scotland",
        ],
        "answer": 1,
        "explain": "The 2027 ODI World Cup (Oct–Nov 2027) will be hosted by South Africa, Zimbabwe, and Namibia.",
    },
]

FORMATS = {
    "IPL": {
        "title": "Indian Premier League (IPL)",
        "badge": "Franchise T20 • 20 Overs",
        "summary": "The world's premier franchise T20 league launched in 2008 by the BCCI, featuring 10 city-based teams.",
        "rows": [
            ["Match Duration", "20 overs per side (~3.5 hours)"],
            ["2026 Champions", "Royal Challengers Bengaluru (RCB) — beat Gujarat Titans by 5 wkts"],
            ["2026 Awards", "MVP & Orange Cap: Vaibhav Sooryavanshi (776) | Purple Cap: Kagiso Rabada (29)"],
            ["Most Titles", "Mumbai Indians (5) & Chennai Super Kings (5), KKR (3), RCB (2)"],
            ["Signature Rules", "Impact Player sub, 2 Bouncers/over, Strategic Timeout, DRS for wides/no-balls"],
        ],
    },
    "ODI": {
        "title": "One Day International (ODI)",
        "badge": "50 Overs • White Ball",
        "summary": "The classic 50-over international format blending tactical middle-over pacing with explosive death-over batting.",
        "rows": [
            ["Match Duration", "50 overs per side (~8 hours)"],
            ["Ball & Kit", "Two new white balls (one per end), colored team kits"],
            ["Powerplays", "PP1 (Overs 1–10: max 2 outside), PP2 (11–40: max 4), PP3 (41–50: max 5)"],
            ["Champions Trophy 2025", "India (won unbeaten, beating New Zealand by 4 wickets in Dubai)"],
            ["Next ODI World Cup", "Oct–Nov 2027 (South Africa, Zimbabwe & Namibia — 14 teams, 54 matches)"],
            ["All-Time Records", "Sachin Tendulkar (18,426 runs) | Virat Kohli (55+ 100s) | Rohit Sharma (264 HS)"],
        ],
    },
    "T20I": {
        "title": "Twenty20 International (T20I)",
        "badge": "20 Overs • Fast-Paced",
        "summary": "Cricket's fastest international format driving global expansion across 20+ World Cup nations & Olympic Games.",
        "rows": [
            ["Match Duration", "20 overs per side (~3 hours)"],
            ["Powerplay", "Overs 1–6 (maximum 2 fielders allowed outside the 30-yard circle)"],
            ["2026 T20 World Cup", "India beat New Zealand by 96 runs (255/5 vs 159) in Ahmedabad for 3rd title"],
            ["2026 WC Stars", "POTM (Final): Jasprit Bumrah | POTT: Sanju Samson | Most Runs: Sahibzada Farhan (383)"],
            ["Next T20 World Cup", "2028 (Australia & New Zealand, Oct–Nov 2028) + LA28 Olympics"],
        ],
    },
    "TEST": {
        "title": "Test Cricket",
        "badge": "5 Days • Red / Pink Ball",
        "summary": "The oldest and ultimate test of technique, endurance, and strategy across five days and two innings per side.",
        "rows": [
            ["Match Duration", "Up to 5 days, 90 overs/day, 2 innings per team"],
            ["Ball & Clothing", "Red ball (Pink ball for Day-Night Tests), traditional white kits"],
            ["WTC 2025 Champions", "South Africa beat Australia by 5 wickets at Lord's (June 2025)"],
            ["Current Cycle", "2025–27 World Test Championship (Final in June 2027 at The Oval)"],
            ["All-Time Records", "Sachin Tendulkar (15,921 runs) | Muttiah Muralitharan (800 wickets)"],
        ],
    },
    "WPL": {
        "title": "Women's Premier League (WPL)",
        "badge": "Women's Franchise T20",
        "summary": "India's flagship women's franchise T20 league featuring five powerhouse teams and record-breaking chases.",
        "rows": [
            ["Match Duration", "20 overs per side (5 franchises)"],
            ["2026 Champions", "Royal Challengers Bengaluru (RCB) — chased 204 vs Delhi Capitals (won by 6 wkts)"],
            ["Historic Double", "RCB became the first franchise to hold both IPL and WPL titles in 2026"],
            ["All WPL Winners", "Mumbai Indians (2023, 2025) & Royal Challengers Bengaluru (2024, 2026)"],
            ["WPL 2026 Star", "Smriti Mandhana (Orange Cap: 377 runs; 87 off 41 in Final)"],
        ],
    },
}

SUGGESTIONS_BY_FORMAT = {
    "ALL": [
        "Current live matches today",
        "Upcoming matches & India schedule",
        "Upcoming cricket formats & ICC events",
        "Show WTC points table & ICC rankings",
        "Stadium pitch & venue guide",
        "Start a cricket quiz",
    ],
    "IPL": [
        "Who won IPL 2026?",
        "Virat Kohli biodata & stats",
        "Explain Impact Player rule",
        "MS Dhoni biodata & legacy",
    ],
    "ODI": [
        "AUS vs ENG 3rd ODI live",
        "India vs Sri Lanka ODI schedule",
        "2027 ODI World Cup format",
        "Rohit Sharma biodata & records",
    ],
    "T20I": [
        "AUS vs ENG T20I schedule",
        "2026 T20 World Cup winner",
        "LA28 Olympics T20 cricket",
        "Sanju Samson biodata & stats",
    ],
    "TEST": [
        "Show WTC points table",
        "India vs New Zealand Test schedule",
        "Border-Gavaskar Trophy 2027",
        "Jasprit Bumrah biodata & stats",
    ],
    "WPL": [
        "Who won WPL 2026?",
        "Smriti Mandhana biodata & stats",
        "2027 Women's Champions Trophy",
    ],
}


# ==============================================================================
# 2. PYTHON AI RESPONSE ENGINE
# ==============================================================================

def find_matching_players(query: str):
    q_lower = query.lower()
    matches = []
    for player in PLAYERS:
        name_hit = player["name"].lower() in q_lower
        kw_hit = any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in player["keywords"])
        if name_hit or kw_hit:
            matches.append(player)
    return matches


def generate_ai_response(raw_query: str, active_format: str = "ALL") -> dict:
    q = raw_query.strip().lower()

    # 1. Interactive Quiz Mode
    if any(k in q for k in ["quiz", "trivia", "test my knowledge"]):
        return {
            "type": "quiz",
            "quiz": random.choice(QUIZ_QUESTIONS),
        }

    # 2. Current / Live Matches
    if any(k in q for k in ["current match", "current matches", "live match", "live matches", "live score", "today match", "today's match", "ongoing", "playing today", "smat", "aus vs eng"]):
        return {
            "type": "schedule",
            "title": "🔴 Current & Live Cricket Matches (Nov 18, 2026)",
            "intro": "Here are the live and active international & domestic cricket matches right now:",
            "items": CURRENT_MATCHES,
        }

    # 3. Upcoming Cricket Formats & ICC Roadmap
    if any(k in q for k in ["upcoming format", "upcoming cricket format", "future format", "upcoming tournament", "upcoming icc", "olympic", "la28", "new format", "t10", "hundred", "roadmap"]):
        return {
            "type": "schedule",
            "title": "🚀 Upcoming Cricket Formats & Major ICC Events (2027–2028)",
            "intro": "Here are the upcoming global cricket formats, debuting tournaments, and ICC event roadmaps:",
            "items": UPCOMING_FORMATS_AND_EVENTS,
        }

    # 4. Upcoming Matches & Schedules
    if any(k in q for k in ["upcoming match", "upcoming matches", "upcoming series", "next match", "schedule", "fixture", "fixtures", "border-gavaskar", "sri lanka", "zimbabwe", "bbl"]):
        return {
            "type": "schedule",
            "title": "📅 Upcoming Cricket Matches & Series (2026–2027)",
            "intro": "Here are the upcoming international & franchise cricket fixtures on the calendar:",
            "items": UPCOMING_MATCHES,
        }

    # 5. WTC Standings & ICC Rankings
    if any(k in q for k in ["wtc", "points table", "standings", "ranking", "rankings"]):
        return {
            "type": "rankings",
            "intro": "📊 Official ICC Team Rankings & WTC 2025–27 Championship Standings (Nov 2026):",
            "wtc_headers": ["Pos", "Team", "Pld", "Pts", "PCT%"],
            "wtc_rows": WTC_STANDINGS,
            "icc_headers": ["Rank", "Test Teams", "ODI Teams", "T20I Teams"],
            "icc_rows": ICC_TEAM_RANKINGS,
        }

    # 6. Stadium & Pitch Intelligence
    if any(k in q for k in ["stadium", "pitch", "venue", "ground", "ahmedabad", "wankhede", "lord", "mcg", "hobart", "wellington"]):
        return {
            "type": "schedule",
            "title": "🏟️ Stadium & Pitch Intelligence Guide",
            "intro": "Pitch behavior, average scores, and tactical conditions at iconic cricket grounds:",
            "items": STADIUMS,
        }

    # 7. Head-to-Head Rivalries & All-Time Records
    if any(k in q for k in ["rivalry", "rivalries", "head to head", "head-to-head", "record", "records", "auction"]):
        return {
            "type": "table",
            "intro": "🏆 Iconic Cricket Rivalries & All-Time Records:",
            "headers": ["Category", "Highlight / Record"],
            "rows": RIVALRIES_AND_RECORDS,
        }

    # 8. Cricket Glossary / Dictionary
    if any(k in q for k in ["glossary", "dictionary", "terms", "googly", "yorker", "free hit", "drs", "dls", "duckworth", "super over", "impact player", "rule"]):
        if "powerplay" in q:
            return {
                "type": "table",
                "intro": "🎯 Cricket Powerplay Rules by Format:",
                "headers": ["Format", "Overs", "Max Outside 30-Yard Circle"],
                "rows": [
                    ["T20I / IPL / WPL", "Overs 1–6", "2 fielders"],
                    ["ODI Powerplay 1", "Overs 1–10", "2 fielders"],
                    ["ODI Powerplay 2", "Overs 11–40", "4 fielders"],
                    ["ODI Powerplay 3", "Overs 41–50", "5 fielders"],
                ],
            }
        return {
            "type": "table",
            "intro": "📘 Cricket Glossary & Key Rules Dictionary:",
            "headers": ["Term / Rule", "Explanation"],
            "rows": GLOSSARY,
        }

    if "powerplay" in q:
        return {
            "type": "table",
            "intro": "🎯 Cricket Powerplay Rules by Format:",
            "headers": ["Format", "Overs", "Max Outside 30-Yard Circle"],
            "rows": [
                ["T20I / IPL / WPL", "Overs 1–6", "2 fielders"],
                ["ODI Powerplay 1", "Overs 1–10", "2 fielders"],
                ["ODI Powerplay 2", "Overs 11–40", "4 fielders"],
                ["ODI Powerplay 3", "Overs 41–50", "5 fielders"],
            ],
        }

    # 9. Player Biodata & Stats (1 or 2+ comparison)
    matched_players = find_matching_players(raw_query)
    if len(matched_players) >= 2:
        p1, p2 = matched_players[0], matched_players[1]
        return {
            "type": "players",
            "intro": f"Here is the complete Biodata & Head-to-Head Stats for {p1['name']} and {p2['name']}:",
            "players": [p1, p2],
        }

    if len(matched_players) == 1:
        p = matched_players[0]
        suffix = f" (highlighted for {active_format})" if active_format != "ALL" else ""
        return {
            "type": "players",
            "intro": f"Here is the complete {p['name']} Biodata, Career Stats & Scouting Report{suffix}:",
            "players": [p],
        }

    if "biodata" in q or "all players" in q:
        return {
            "type": "fallback",
            "text": "Tap any player below (or search in the sidebar) to view their full Personal Biodata, Debuts & Career Stats:",
            "chips": [f"{p['name']} biodata" for p in PLAYERS[:6]],
        }

    # 10. Format Comparison
    if "compare" in q or "difference" in q or "all format" in q or ("ipl" in q and "odi" in q):
        return {
            "type": "comparison",
            "intro": "Here is a side-by-side breakdown across every major cricket format:",
        }

    # 11. Specific Formats & Tournaments
    if "champions trophy" in q:
        return {
            "type": "format",
            "intro": "🏆 ICC Champions Trophy: India won the 2025 Men's edition unbeaten, and India will host the inaugural 2027 Women's Champions Trophy (T20) in Feb 2027.",
            "format": FORMATS["ODI"],
        }
    if "world cup" in q and ("odi" in q or "50" in q or "2027" in q):
        return {
            "type": "format",
            "intro": "🌍 ICC Men's ODI World Cup: The next edition runs Oct 2 – Nov 21, 2027 in South Africa, Zimbabwe & Namibia (14 teams).",
            "format": FORMATS["ODI"],
        }
    if "t20 world cup" in q or ("world cup" in q and "2026" in q):
        return {
            "type": "format",
            "intro": "🏆 2026 ICC Men's T20 World Cup: India defended their crown on home soil, beating New Zealand by 96 runs in Ahmedabad to become the first 3-time champions.",
            "format": FORMATS["T20I"],
        }
    if "ipl" in q:
        return {"type": "format", "intro": "Here is the complete IPL T20 intelligence briefing:", "format": FORMATS["IPL"]}
    if "odi" in q:
        return {"type": "format", "intro": "Here is your ODI (50-Over) format briefing:", "format": FORMATS["ODI"]}
    if "t20" in q:
        return {"type": "format", "intro": "Here is your T20 International briefing:", "format": FORMATS["T20I"]}
    if "test" in q or "pink ball" in q or "red ball" in q:
        return {"type": "format", "intro": "Here is your Test Cricket briefing:", "format": FORMATS["TEST"]}
    if "wpl" in q or "women" in q:
        return {"type": "format", "intro": "Here is your Women's Premier League (WPL) briefing:", "format": FORMATS["WPL"]}

    # 12. Greetings
    if re.match(r"^(hi|hello|hey|namaste|good morning|good evening)\b", q):
        return {
            "type": "text",
            "text": "Hey cricket fan! 👋 Welcome to CricMind AI. Ask me about Current Live Matches, Upcoming Matches, Upcoming Formats, WTC Standings, Stadium Pitches, Cricket Rules, or any Player's full Biodata & Stats!",
        }

    # 13. Smart Fallback
    return {
        "type": "fallback",
        "text": f'I did not find a direct match for "{raw_query}". Try one of these popular topics:',
        "chips": [
            "Current live matches today",
            "Upcoming matches",
            "Upcoming cricket formats",
            "Virat Kohli biodata",
            "Show WTC points table",
            "Start a cricket quiz",
        ],
    }


# ==============================================================================
# 3. PROFESSIONAL WEB DESIGN (HTML + CSS + JS)
# ==============================================================================

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CricMind AI — Complete Cricket Sports Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-app: #070b14;
      --bg-sidebar: #0c1220;
      --bg-surface: #111a2e;
      --bg-card: rgba(17, 26, 46, 0.88);
      --bg-glass: rgba(255, 255, 255, 0.04);
      --border: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.16);
      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.22);
      --gold: #f59e0b;
      --gold-glow: rgba(245, 158, 11, 0.18);
      --blue: #3b82f6;
      --red: #ef4444;
      --red-glow: rgba(239, 68, 68, 0.2);
      --purple: #a855f7;
      --purple-glow: rgba(168, 85, 247, 0.2);
      --radius-lg: 18px;
      --radius-md: 12px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      height: 100%; background: var(--bg-app); color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; overflow: hidden;
    }
    body::before {
      content: ""; position: fixed; top: -20%; right: -10%; width: 58vw; height: 58vw;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.09) 0%, transparent 65%); pointer-events: none;
    }

    .app-shell { position: relative; z-index: 1; display: flex; height: 100dvh; width: 100%; }

    /* SIDEBAR */
    .sidebar {
      width: 310px; background: var(--bg-sidebar); border-right: 1px solid var(--border);
      display: flex; flex-direction: column; padding: 16px 14px; gap: 14px;
      flex-shrink: 0; transition: transform 0.28s ease; z-index: 30; overflow-y: auto;
    }
    .sidebar::-webkit-scrollbar, .player-list::-webkit-scrollbar, .chat-feed::-webkit-scrollbar { width: 5px; }
    .sidebar::-webkit-scrollbar-thumb, .player-list::-webkit-scrollbar-thumb, .chat-feed::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.12); border-radius: 999px;
    }

    .brand { display: flex; align-items: center; justify-content: space-between; padding: 2px 4px; }
    .brand-left { display: flex; align-items: center; gap: 10px; }
    .brand-icon {
      width: 38px; height: 38px; border-radius: 11px;
      background: linear-gradient(135deg, var(--emerald), #059669);
      display: grid; place-items: center; box-shadow: 0 6px 20px var(--emerald-glow);
    }
    .brand-title { font-size: 1.04rem; font-weight: 800; display: flex; align-items: center; gap: 6px; }
    .pro-badge {
      font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
      background: var(--gold-glow); color: var(--gold);
      border: 1px solid rgba(245, 158, 11, 0.35); padding: 2px 6px; border-radius: 999px;
    }
    .brand-sub { font-size: 0.72rem; color: var(--text-secondary); }
    .close-sidebar-btn {
      display: none; background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; place-items: center;
    }

    .sidebar-section { display: flex; flex-direction: column; gap: 7px; }
    .section-label {
      font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--text-muted); padding: 0 4px; display: flex; justify-content: space-between;
    }

    .match-center-list { display: flex; flex-direction: column; gap: 6px; }
    .mode-btn {
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 11px; border-radius: var(--radius-md);
      background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-primary); font-family: inherit; font-size: 0.8rem; font-weight: 600;
      cursor: pointer; transition: 0.16s ease; text-align: left;
    }
    .mode-btn:hover { background: rgba(255,255,255,0.08); border-color: var(--border-strong); transform: translateY(-1px); }
    .mode-btn.live-btn { border-color: rgba(239, 68, 68, 0.35); background: rgba(239, 68, 68, 0.08); }
    .mode-btn.upcoming-btn { border-color: rgba(59, 130, 246, 0.35); background: rgba(59, 130, 246, 0.08); }
    .mode-btn.future-btn { border-color: rgba(168, 85, 247, 0.35); background: rgba(168, 85, 247, 0.08); }

    .hub-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
    .hub-btn {
      padding: 8px 8px; border-radius: 10px; background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); font-family: inherit; font-size: 0.75rem; font-weight: 600;
      cursor: pointer; text-align: left; transition: 0.16s ease;
    }
    .hub-btn:hover { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.4); color: #fff; }

    .format-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
    .format-pill {
      display: flex; align-items: center; gap: 7px; padding: 7px 10px;
      border-radius: 10px; background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); font-family: inherit; font-size: 0.78rem; font-weight: 600;
      cursor: pointer; transition: 0.16s ease;
    }
    .format-pill:hover { background: rgba(255,255,255,0.07); color: #fff; }
    .format-pill.active {
      background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05));
      border-color: rgba(16,185,129,0.55); color: #fff;
    }
    .format-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); }
    .format-pill.active .format-dot { background: var(--emerald); box-shadow: 0 0 8px var(--emerald); }

    /* Player Search Input */
    .player-search {
      width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      border-radius: 10px; padding: 7px 10px; color: #fff; font-family: inherit; font-size: 0.79rem; outline: none;
    }
    .player-search:focus { border-color: var(--emerald); }
    .player-search::placeholder { color: var(--text-muted); }

    .player-list { display: flex; flex-direction: column; gap: 4px; overflow-y: auto; max-height: 210px; padding-right: 2px; }
    .player-item {
      display: flex; align-items: center; justify-content: space-between; padding: 6px 8px;
      border-radius: 10px; background: transparent; border: 1px solid transparent; color: var(--text-primary);
      font-family: inherit; cursor: pointer; text-align: left; width: 100%; transition: 0.15s ease;
    }
    .player-item:hover { background: var(--bg-glass); border-color: var(--border); }
    .player-item-left { display: flex; align-items: center; gap: 9px; }
    .mini-avatar {
      width: 28px; height: 28px; border-radius: 8px; display: grid; place-items: center;
      font-size: 0.68rem; font-weight: 800; color: #fff; flex-shrink: 0;
    }
    .player-item-name { font-size: 0.8rem; font-weight: 600; display: block; }
    .player-item-meta { font-size: 0.67rem; color: var(--text-muted); }

    .sidebar-footer { margin-top: auto; display: flex; gap: 6px; padding-top: 8px; border-top: 1px solid var(--border); }
    .action-btn {
      flex: 1; display: flex; align-items: center; justify-content: center; gap: 5px; padding: 8px 8px;
      border-radius: 10px; background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); font-family: inherit; font-size: 0.74rem; font-weight: 600; cursor: pointer;
    }
    .action-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }

    /* MAIN STAGE */
    .main-stage { flex: 1; display: flex; flex-direction: column; min-width: 0; height: 100dvh; }
    .topbar {
      height: 58px; padding: 0 22px; border-bottom: 1px solid var(--border);
      background: rgba(7, 11, 20, 0.78); backdrop-filter: blur(14px);
      display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
    }
    .topbar-left { display: flex; align-items: center; gap: 10px; }
    .topbar-right { display: flex; align-items: center; gap: 8px; }
    .menu-btn {
      display: none; background: var(--bg-glass); border: 1px solid var(--border);
      color: #fff; width: 36px; height: 36px; border-radius: 10px; cursor: pointer; place-items: center;
    }
    .status-pill {
      display: inline-flex; align-items: center; gap: 7px; padding: 5px 11px; border-radius: 999px;
      background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.28);
      font-size: 0.75rem; font-weight: 600; color: #6ee7b7;
    }
    .pulse-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--emerald); animation: pulse 2s infinite; }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
      70% { box-shadow: 0 0 0 7px rgba(16,185,129,0); }
      100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    .context-chip {
      font-size: 0.73rem; font-weight: 700; color: var(--text-secondary);
      background: var(--bg-glass); border: 1px solid var(--border); padding: 5px 11px; border-radius: 999px;
    }
    .context-chip span { color: var(--gold); }

    /* SCROLLING LIVE TICKER */
    .ticker-bar {
      height: 34px; background: rgba(16, 185, 129, 0.08); border-bottom: 1px solid var(--border);
      overflow: hidden; display: flex; align-items: center; flex-shrink: 0; position: relative;
    }
    .ticker-track {
      display: flex; align-items: center; gap: 36px; white-space: nowrap;
      animation: tickerMove 34s linear infinite; padding-left: 100%;
    }
    .ticker-bar:hover .ticker-track { animation-play-state: paused; }
    @keyframes tickerMove {
      0% { transform: translateX(0); }
      100% { transform: translateX(-100%); }
    }
    .ticker-item {
      background: none; border: none; color: #cbd5e1; font-family: inherit;
      font-size: 0.75rem; font-weight: 600; cursor: pointer; transition: color 0.15s;
    }
    .ticker-item:hover { color: #fff; text-decoration: underline; }

    /* CHAT FEED */
    .chat-feed {
      flex: 1; overflow-y: auto; padding: 22px 24px 16px;
      display: flex; flex-direction: column; gap: 18px; scroll-behavior: smooth;
    }
    .message-row { display: flex; gap: 12px; max-width: 920px; width: 100%; margin: 0 auto; animation: fadeUp 0.25s ease; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .message-row.user { justify-content: flex-end; }
    .avatar {
      width: 35px; height: 35px; border-radius: 10px; display: grid; place-items: center;
      flex-shrink: 0; font-size: 0.75rem; font-weight: 800; color: #fff;
    }
    .avatar.ai { background: linear-gradient(135deg, var(--emerald), #047857); }
    .avatar.user { background: linear-gradient(135deg, var(--blue), #1d4ed8); order: 2; }
    .bubble { border-radius: var(--radius-lg); padding: 14px 18px; line-height: 1.58; font-size: 0.92rem; }
    .message-row.user .bubble {
      max-width: 76%; background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff; border-bottom-right-radius: 4px;
    }
    .message-row.ai .bubble {
      max-width: 88%; background: var(--bg-card); border: 1px solid var(--border);
      color: var(--text-primary); border-top-left-radius: 4px; box-shadow: 0 12px 32px rgba(0,0,0,0.35);
    }
    .msg-time { font-size: 0.67rem; color: var(--text-muted); margin-top: 6px; display: block; }
    .message-row.user .msg-time { color: rgba(255,255,255,0.72); text-align: right; }

    /* RICH CARDS */
    .feature-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .starter-btn {
      background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: #a7f3d0;
      padding: 7px 12px; border-radius: 999px; font-family: inherit; font-size: 0.78rem; font-weight: 600; cursor: pointer;
    }
    .starter-btn:hover { background: rgba(16,185,129,0.22); color: #fff; }

    .schedule-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
    .match-card {
      background: rgba(7, 11, 20, 0.72); border: 1px solid var(--border-strong);
      border-radius: var(--radius-md); padding: 12px 15px; display: flex; flex-direction: column; gap: 5px;
    }
    .match-badges { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .badge-pill { font-size: 0.67rem; font-weight: 800; padding: 3px 9px; border-radius: 999px; }
    .badge-live { background: var(--red-glow); color: #fca5a5; border: 1px solid rgba(239,68,68,0.45); }
    .badge-upcoming { background: rgba(59,130,246,0.18); color: #93c5fd; border: 1px solid rgba(59,130,246,0.4); }
    .badge-future { background: var(--purple-glow); color: #d8b4fe; border: 1px solid rgba(168,85,247,0.4); }
    .badge-fmt {
      font-family: 'JetBrains Mono', monospace; font-size: 0.67rem; font-weight: 700;
      padding: 3px 8px; border-radius: 6px; background: var(--emerald-glow); color: #6ee7b7;
      border: 1px solid rgba(16,185,129,0.35);
    }
    .match-title { font-size: 0.95rem; font-weight: 800; color: #fff; }
    .match-venue { font-size: 0.77rem; color: var(--gold); font-weight: 600; }
    .match-status { font-size: 0.82rem; color: var(--text-secondary); }

    /* Player Card + Biodata */
    .player-card {
      margin-top: 12px; background: rgba(7,11,20,0.68); border: 1px solid var(--border-strong);
      border-radius: var(--radius-md); overflow: hidden;
    }
    .player-card-header {
      padding: 14px 16px;
      background: linear-gradient(135deg, rgba(16,185,129,0.14), rgba(59,130,246,0.08));
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
    }
    .player-identity { display: flex; align-items: center; gap: 12px; }
    .player-badge-avatar {
      width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center;
      font-weight: 800; font-size: 1rem; color: #fff;
    }
    .player-sub { font-size: 0.77rem; color: var(--text-secondary); }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      font-size: 0.69rem; font-weight: 700; padding: 3px 9px; border-radius: 999px;
      background: var(--bg-glass); border: 1px solid var(--border); color: var(--text-secondary);
    }
    .tag.gold { background: var(--gold-glow); border-color: rgba(245,158,11,0.35); color: #fcd34d; }
    .tag.emerald { background: var(--emerald-glow); border-color: rgba(16,185,129,0.35); color: #6ee7b7; }

    .biodata-section {
      padding: 12px 16px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.02);
    }
    .biodata-title {
      font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em;
      color: #93c5fd; margin-bottom: 8px;
    }
    .biodata-grid {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 14px;
    }
    .bio-item { font-size: 0.79rem; color: var(--text-secondary); }
    .bio-label { color: var(--text-muted); font-weight: 700; font-size: 0.7rem; text-transform: uppercase; display: block; }
    .bio-value { color: #f8fafc; font-weight: 600; }
    .bio-item.full-span { grid-column: 1 / -1; }

    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid var(--border); }
    .stat-box { padding: 11px 8px; text-align: center; border-right: 1px solid var(--border); }
    .stat-box:last-child { border-right: none; }
    .stat-format { font-size: 0.68rem; font-weight: 700; color: var(--emerald); margin-bottom: 4px; }
    .stat-main { font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 700; color: #fff; }
    .stat-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.69rem; color: var(--text-secondary); margin-top: 2px; }

    .highlights-box { padding: 12px 16px; }
    .highlights-title { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--gold); margin-bottom: 6px; }
    .highlights-list { list-style: none; display: flex; flex-direction: column; gap: 5px; }
    .highlights-list li { font-size: 0.82rem; color: var(--text-secondary); padding-left: 14px; position: relative; }
    .highlights-list li::before { content: "▸"; position: absolute; left: 0; color: var(--emerald); }

    .table-wrap { margin-top: 10px; overflow-x: auto; border-radius: var(--radius-md); border: 1px solid var(--border-strong); background: rgba(7,11,20,0.65); }
    table.cric-table { width: 100%; border-collapse: collapse; font-size: 0.81rem; text-align: left; }
    table.cric-table th { background: rgba(16,185,129,0.12); color: #6ee7b7; padding: 9px 11px; border-bottom: 1px solid var(--border); }
    table.cric-table td { padding: 8px 11px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
    table.cric-table tr:last-child td { border-bottom: none; }
    table.cric-table td strong { color: #fff; }
    .mono { font-family: 'JetBrains Mono', monospace; color: #fff; }

    /* Quiz Card */
    .quiz-options { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
    .quiz-opt-btn {
      padding: 10px 12px; border-radius: 10px; background: rgba(255,255,255,0.05);
      border: 1px solid var(--border-strong); color: #fff; font-family: inherit;
      font-size: 0.83rem; font-weight: 600; cursor: pointer; text-align: left; transition: 0.16s;
    }
    .quiz-opt-btn:hover:not(:disabled) { border-color: var(--emerald); background: rgba(16,185,129,0.14); }
    .quiz-opt-btn.correct { background: rgba(16,185,129,0.28); border-color: var(--emerald); }
    .quiz-opt-btn.wrong { background: rgba(239,68,68,0.28); border-color: var(--red); }
    .quiz-feedback { margin-top: 10px; font-size: 0.83rem; color: #a7f3d0; font-weight: 600; }

    .typing-dots { display: inline-flex; gap: 5px; padding: 6px 2px; }
    .typing-dots span { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); animation: bounce 1.3s infinite ease-in-out; }
    .typing-dots span:nth-child(2) { animation-delay: 0.16s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.32s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1.1); opacity: 1; } }

    /* COMPOSER */
    .composer-area { padding: 8px 24px 16px; background: linear-gradient(to top, var(--bg-app) 80%, transparent); flex-shrink: 0; }
    .composer-inner { max-width: 920px; margin: 0 auto; display: flex; flex-direction: column; gap: 8px; }
    .input-format-bar { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .quick-mode-pill {
      padding: 4px 10px; border-radius: 999px; border: 1px solid var(--border-strong);
      background: var(--bg-surface); color: var(--text-primary); font-family: inherit;
      font-size: 0.73rem; font-weight: 700; cursor: pointer;
    }
    .quick-mode-pill:hover { border-color: var(--emerald); }
    .quick-mode-pill.q-live { border-color: rgba(239,68,68,0.45); color: #fca5a5; }
    .quick-mode-pill.q-up { border-color: rgba(59,130,246,0.45); color: #93c5fd; }
    .quick-mode-pill.q-fut { border-color: rgba(168,85,247,0.45); color: #d8b4fe; }

    .suggestion-bar { display: flex; gap: 7px; overflow-x: auto; scrollbar-width: none; }
    .suggestion-bar::-webkit-scrollbar { display: none; }
    .suggestion-chip {
      white-space: nowrap; padding: 5px 11px; border-radius: 999px; background: var(--bg-glass);
      border: 1px solid var(--border); color: var(--text-secondary); font-family: inherit;
      font-size: 0.74rem; font-weight: 600; cursor: pointer;
    }
    .suggestion-chip:hover { background: rgba(16,185,129,0.14); border-color: rgba(16,185,129,0.4); color: #fff; }

    .input-box {
      display: flex; align-items: center; gap: 8px; background: var(--bg-surface);
      border: 1px solid var(--border-strong); border-radius: 16px; padding: 7px 8px 7px 12px;
    }
    .input-box:focus-within { border-color: var(--emerald); box-shadow: 0 0 0 3px var(--emerald-glow); }
    .input-prefix-select {
      background: rgba(255,255,255,0.06); color: #a7f3d0; border: 1px solid var(--border);
      border-radius: 10px; padding: 7px 9px; font-family: inherit; font-size: 0.76rem; font-weight: 700; outline: none;
    }
    .input-prefix-select option { background: #0c1220; color: #fff; }
    .chat-input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-family: inherit; font-size: 0.93rem; padding: 6px 0; min-width: 100px; }
    .chat-input::placeholder { color: var(--text-muted); }
    .mic-btn {
      width: 38px; height: 38px; border-radius: 10px; border: 1px solid var(--border);
      background: var(--bg-glass); color: var(--text-secondary); display: grid; place-items: center; cursor: pointer;
    }
    .mic-btn.listening { background: var(--red-glow); border-color: var(--red); color: #fca5a5; animation: pulse 1s infinite; }
    .send-btn {
      width: 40px; height: 40px; border-radius: 11px; border: none;
      background: linear-gradient(135deg, var(--emerald), #059669); color: #fff; display: grid; place-items: center; cursor: pointer;
    }

    .backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 25; }
    @media (max-width: 860px) {
      .sidebar { position: fixed; top: 0; left: 0; bottom: 0; transform: translateX(-100%); }
      .sidebar.open { transform: translateX(0); }
      .backdrop.open { display: block; }
      .menu-btn, .close-sidebar-btn { display: grid; }
      .stats-grid, .biodata-grid, .quiz-options { grid-template-columns: 1fr 1fr; }
      .quiz-options { grid-template-columns: 1fr; }
      .biodata-grid { grid-template-columns: 1fr; }
      .stat-box:nth-child(2) { border-right: none; }
      .stat-box:nth-child(1), .stat-box:nth-child(2) { border-bottom: 1px solid var(--border); }
      .message-row.ai .bubble, .bubble { max-width: 94%; }
      .input-prefix-select { display: none; }
    }
  </style>
</head>
<body>
  <div class="backdrop" id="backdrop"></div>
  <div class="app-shell">
    <aside class="sidebar" id="sidebar">
      <div class="brand">
        <div class="brand-left">
          <div class="brand-icon">🏏</div>
          <div>
            <div class="brand-title">CricMind <span class="pro-badge">Pro AI</span></div>
            <div class="brand-sub">Live • Biodata • Rankings</div>
          </div>
        </div>
        <button class="close-sidebar-btn" id="closeSidebarBtn">✕</button>
      </div>

      <div class="sidebar-section">
        <div class="section-label"><span>Match Center</span><span style="color:var(--emerald)">Nov 2026</span></div>
        <div class="match-center-list">
          <button class="mode-btn live-btn" data-q="Current live matches today"><span>🔴 Current Live Matches</span><span>›</span></button>
          <button class="mode-btn upcoming-btn" data-q="Upcoming matches and schedule"><span>📅 Upcoming Matches</span><span>›</span></button>
          <button class="mode-btn future-btn" data-q="Upcoming cricket formats and ICC events"><span>🚀 Upcoming Formats & ICC</span><span>›</span></button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-label"><span>Intelligence Hubs</span></div>
        <div class="hub-grid">
          <button class="hub-btn mode-btn" data-q="Show WTC points table and ICC rankings">📊 WTC & Rankings</button>
          <button class="hub-btn mode-btn" data-q="Stadium pitch and venue guide">🏟️ Pitch Guide</button>
          <button class="hub-btn mode-btn" data-q="Cricket rivalries and all-time records">🏆 Records</button>
          <button class="hub-btn mode-btn" data-q="Cricket glossary and rules">📘 Glossary</button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-label"><span>Cricket Formats</span></div>
        <div class="format-grid" id="formatGrid">
          <button class="format-pill active" data-format="ALL"><span class="format-dot"></span>All Formats</button>
          <button class="format-pill" data-format="IPL"><span class="format-dot"></span>IPL T20</button>
          <button class="format-pill" data-format="ODI"><span class="format-dot"></span>ODI 50-Ov</button>
          <button class="format-pill" data-format="T20I"><span class="format-dot"></span>T20I</button>
          <button class="format-pill" data-format="TEST"><span class="format-dot"></span>Test Match</button>
          <button class="format-pill" data-format="WPL"><span class="format-dot"></span>WPL</button>
        </div>
      </div>

      <div class="sidebar-section" style="flex:1; min-height:0;">
        <div class="section-label"><span>Player Biodata</span><span>Tap Any</span></div>
        <input type="text" class="player-search" id="playerSearch" placeholder="🔍 Search player, country, or team..." />
        <div class="player-list" id="playerList"></div>
      </div>

      <div class="sidebar-footer">
        <button class="action-btn" id="quizBtn">🧠 Quiz (<span id="quizScoreLabel">0</span>)</button>
        <button class="action-btn" id="compareBtn">📊 Compare</button>
        <button class="action-btn" id="clearChatBtn">🗑️ Clear</button>
      </div>
    </aside>

    <main class="main-stage">
      <header class="topbar">
        <div class="topbar-left">
          <button class="menu-btn" id="openSidebarBtn">☰</button>
          <div class="status-pill"><span class="pulse-dot"></span>Python AI Online</div>
        </div>
        <div class="topbar-right">
          <div class="context-chip">Format: <span id="activeFormatLabel">ALL</span></div>
        </div>
      </header>

      <!-- Scrolling Live Ticker -->
      <div class="ticker-bar">
        <div class="ticker-track" id="tickerTrack"></div>
      </div>

      <section class="chat-feed" id="chatFeed"></section>

      <footer class="composer-area">
        <div class="composer-inner">
          <div class="input-format-bar">
            <button type="button" class="quick-mode-pill q-live" data-q="Current live matches today">🔴 Current Matches</button>
            <button type="button" class="quick-mode-pill q-up" data-q="Upcoming matches and schedule">📅 Upcoming Matches</button>
            <button type="button" class="quick-mode-pill q-fut" data-q="Upcoming cricket formats and ICC events">🚀 Upcoming Formats</button>
            <button type="button" class="quick-mode-pill" data-q="Show WTC points table and ICC rankings">📊 Rankings</button>
            <button type="button" class="quick-mode-pill" data-q="Stadium pitch and venue guide">🏟️ Pitch Guide</button>
            <button type="button" class="quick-mode-pill" data-q="Start a cricket quiz">🧠 Quiz</button>
          </div>

          <div class="suggestion-bar" id="suggestionBar"></div>

          <form class="input-box" id="chatForm">
            <select class="input-prefix-select" id="queryPreset" title="Quick input mode">
              <option value="">💬 Free Ask</option>
              <option value="live">🔴 Current Matches</option>
              <option value="upcoming">📅 Upcoming Matches</option>
              <option value="formats">🚀 Upcoming Formats</option>
              <option value="bio">👤 Player Biodata</option>
              <option value="wtc">📊 WTC & Rankings</option>
              <option value="pitch">🏟️ Stadium Pitch</option>
            </select>
            <input type="text" class="chat-input" id="userInput" placeholder="Ask about live matches, upcoming formats, WTC table, pitches, or any player's biodata..." required autocomplete="off" />
            <button type="button" class="mic-btn" id="micBtn" title="Voice Input">🎙️</button>
            <button type="submit" class="send-btn" aria-label="Send">➤</button>
          </form>
        </div>
      </footer>
    </main>
  </div>

  <script>
    let activeFormat = "ALL";
    let allPlayers = [];
    let suggestionsMap = {};
    let quizScore = 0;

    const chatFeed = document.getElementById("chatFeed");
    const suggestionBar = document.getElementById("suggestionBar");
    const playerListEl = document.getElementById("playerList");
    const playerSearch = document.getElementById("playerSearch");
    const activeFormatLabel = document.getElementById("activeFormatLabel");
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.getElementById("backdrop");
    const queryPreset = document.getElementById("queryPreset");
    const userInput = document.getElementById("userInput");
    const micBtn = document.getElementById("micBtn");

    async function init() {
      const res = await fetch("/api/init");
      const data = await res.json();
      allPlayers = data.players;
      suggestionsMap = data.suggestions;

      renderTicker(data.ticker);
      renderPlayerSidebar(allPlayers);
      renderSuggestions();
      showWelcomeMessage();

      document.getElementById("openSidebarBtn").addEventListener("click", () => {
        sidebar.classList.add("open"); backdrop.classList.add("open");
      });
      const closeMenu = () => { sidebar.classList.remove("open"); backdrop.classList.remove("open"); };
      document.getElementById("closeSidebarBtn").addEventListener("click", closeMenu);
      backdrop.addEventListener("click", closeMenu);

      playerSearch.addEventListener("input", () => {
        const term = playerSearch.value.trim().toLowerCase();
        const filtered = allPlayers.filter(p =>
          p.name.toLowerCase().includes(term) ||
          p.country.toLowerCase().includes(term) ||
          p.team.toLowerCase().includes(term)
        );
        renderPlayerSidebar(filtered);
      });

      document.querySelectorAll(".mode-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          if (window.innerWidth <= 860) closeMenu();
          sendQuery(btn.dataset.q);
        });
      });

      document.querySelectorAll(".quick-mode-pill").forEach(btn => {
        btn.addEventListener("click", () => sendQuery(btn.dataset.q));
      });

      queryPreset.addEventListener("change", () => {
        const map = {
          live: "Current live matches today",
          upcoming: "Upcoming matches and schedule",
          formats: "Upcoming cricket formats and ICC events",
          bio: "Virat Kohli biodata and stats",
          wtc: "Show WTC points table and ICC rankings",
          pitch: "Stadium pitch and venue guide"
        };
        if (map[queryPreset.value]) {
          userInput.value = map[queryPreset.value];
          userInput.focus();
        }
      });

      document.getElementById("formatGrid").addEventListener("click", (e) => {
        const pill = e.target.closest(".format-pill");
        if (!pill) return;
        setActiveFormat(pill.dataset.format);
        if (window.innerWidth <= 860) closeMenu();
      });

      document.getElementById("quizBtn").addEventListener("click", () => {
        if (window.innerWidth <= 860) closeMenu();
        sendQuery("Start a cricket quiz");
      });

      document.getElementById("compareBtn").addEventListener("click", () => {
        if (window.innerWidth <= 860) closeMenu();
        sendQuery("Compare all cricket formats");
      });

      document.getElementById("clearChatBtn").addEventListener("click", () => {
        chatFeed.innerHTML = "";
        showWelcomeMessage();
        if (window.innerWidth <= 860) closeMenu();
      });

      document.getElementById("chatForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;
        userInput.value = "";
        queryPreset.value = "";
        sendQuery(text);
      });

      chatFeed.addEventListener("click", (e) => {
        const inlineBtn = e.target.closest(".inline-q");
        if (inlineBtn) sendQuery(inlineBtn.dataset.q);

        const quizBtn = e.target.closest(".quiz-opt-btn");
        if (quizBtn) handleQuizAnswer(quizBtn);
      });

      setupVoiceInput();
    }

    function renderTicker(items) {
      const track = document.getElementById("tickerTrack");
      const html = items.map(it => `<button class="ticker-item" data-q="${escapeHtml(it.query)}">${escapeHtml(it.label)}</button>`).join("");
      track.innerHTML = html + html;
      track.addEventListener("click", (e) => {
        const btn = e.target.closest(".ticker-item");
        if (btn) sendQuery(btn.dataset.q);
      });
    }

    function renderPlayerSidebar(players) {
      if (!players.length) {
        playerListEl.innerHTML = `<div style="font-size:0.78rem; color:var(--text-muted); padding:8px;">No matching players found.</div>`;
        return;
      }
      playerListEl.innerHTML = players.map(p => `
        <button class="player-item" data-name="${escapeHtml(p.name)}">
          <span class="player-item-left">
            <span class="mini-avatar" style="background:${p.gradient}">${p.initials}</span>
            <span>
              <span class="player-item-name">${escapeHtml(p.name)}</span>
              <span class="player-item-meta">${escapeHtml(p.country)} • ${escapeHtml(p.team)}</span>
            </span>
          </span>
          <span>›</span>
        </button>
      `).join("");

      playerListEl.querySelectorAll(".player-item").forEach(btn => {
        btn.addEventListener("click", () => {
          if (window.innerWidth <= 860) {
            sidebar.classList.remove("open"); backdrop.classList.remove("open");
          }
          sendQuery(`${btn.dataset.name} biodata and stats`);
        });
      });
    }

    function setupVoiceInput() {
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRec) {
        micBtn.addEventListener("click", () => alert("Voice input is supported in Chrome or Edge browsers."));
        return;
      }
      const recognition = new SpeechRec();
      recognition.lang = "en-IN";
      recognition.interimResults = false;

      micBtn.addEventListener("click", () => {
        micBtn.classList.add("listening");
        recognition.start();
      });
      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        userInput.value = transcript;
        micBtn.classList.remove("listening");
        sendQuery(transcript);
      };
      recognition.onerror = () => micBtn.classList.remove("listening");
      recognition.onend = () => micBtn.classList.remove("listening");
    }

    function setActiveFormat(fmt) {
      activeFormat = fmt;
      document.querySelectorAll(".format-pill").forEach(b => b.classList.toggle("active", b.dataset.format === fmt));
      activeFormatLabel.textContent = fmt;
      renderSuggestions();
      if (fmt !== "ALL") sendQuery(`Tell me about ${fmt} format`);
    }

    function renderSuggestions() {
      const list = suggestionsMap[activeFormat] || suggestionsMap.ALL || [];
      suggestionBar.innerHTML = list.map(q => `<button class="suggestion-chip" type="button">${escapeHtml(q)}</button>`).join("");
      suggestionBar.querySelectorAll(".suggestion-chip").forEach(chip => {
        chip.addEventListener("click", () => sendQuery(chip.textContent));
      });
    }

    function showWelcomeMessage() {
      appendAI(`
        <h2 style="font-size:1.15rem; font-weight:800; margin-bottom:6px;">🏏 Welcome to CricMind AI Pro</h2>
        <p style="color:var(--text-secondary); font-size:0.9rem;">
          Your all-in-one cricket assistant for <strong>Live & Upcoming Matches</strong>, <strong>Upcoming Formats</strong>,
          <strong>Full Player Biodata & Career Stats</strong>, <strong>WTC Standings & ICC Rankings</strong>,
          <strong>Stadium Pitch Guides</strong>, and <strong>Interactive Quizzes</strong>.
        </p>
        <div class="feature-pills">
          <button class="starter-btn inline-q" data-q="Current live matches today">🔴 Live Matches</button>
          <button class="starter-btn inline-q" data-q="Upcoming matches and schedule">📅 Upcoming Matches</button>
          <button class="starter-btn inline-q" data-q="Upcoming cricket formats and ICC events">🚀 Upcoming Formats</button>
          <button class="starter-btn inline-q" data-q="Virat Kohli biodata and stats">👤 Virat Kohli Biodata</button>
          <button class="starter-btn inline-q" data-q="Show WTC points table and ICC rankings">📊 WTC & Rankings</button>
          <button class="starter-btn inline-q" data-q="Start a cricket quiz">🧠 Play Quiz</button>
        </div>
      `);
    }

    async function sendQuery(text) {
      appendUser(text);
      const typingId = showTyping();
      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, format: activeFormat }),
        });
        const data = await res.json();
        removeTyping(typingId);
        appendAI(buildResponseHTML(data));
      } catch (err) {
        removeTyping(typingId);
        appendAI("<p>Connection error talking to Python server.</p>");
      }
    }

    function buildResponseHTML(data) {
      if (data.type === "schedule") return renderScheduleCards(data);
      if (data.type === "players") return `<p>${escapeHtml(data.intro)}</p>` + data.players.map(renderPlayerCard).join("");
      if (data.type === "rankings") return renderRankingsCard(data);
      if (data.type === "quiz") return renderQuizCard(data.quiz);
      if (data.type === "format") return renderFormatCard(data.format, data.intro);
      if (data.type === "comparison") return `<p>${escapeHtml(data.intro)}</p>` + renderComparisonTable();
      if (data.type === "table") {
        return `
          <p><strong>${escapeHtml(data.intro)}</strong></p>
          <div class="table-wrap">
            <table class="cric-table">
              <thead><tr>${data.headers.map(h => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead>
              <tbody>${data.rows.map(r => `<tr>${r.map((c, i) => `<td>${i === 0 ? `<strong>${escapeHtml(c)}</strong>` : escapeHtml(c)}</td>`).join("")}</tr>`).join("")}</tbody>
            </table>
          </div>
        `;
      }
      if (data.type === "fallback") {
        return `
          <p>${escapeHtml(data.text)}</p>
          <div class="feature-pills">${data.chips.map(c => `<button class="starter-btn inline-q" data-q="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join("")}</div>
        `;
      }
      return `<p>${escapeHtml(data.text)}</p>`;
    }

    function renderScheduleCards(data) {
      const badgeClass = (t) => t === "live" ? "badge-live" : (t === "future" ? "badge-future" : "badge-upcoming");
      return `
        <p><strong>${escapeHtml(data.title)}</strong></p>
        <p style="color:var(--text-secondary); font-size:0.85rem; margin-top:4px;">${escapeHtml(data.intro)}</p>
        <div class="schedule-grid">
          ${data.items.map(item => `
            <div class="match-card">
              <div class="match-badges">
                <span class="badge-pill ${badgeClass(item.badge_type)}">${escapeHtml(item.badge)}</span>
                <span class="badge-fmt">${escapeHtml(item.format)}</span>
              </div>
              <div class="match-title">${escapeHtml(item.title)}</div>
              <div class="match-venue">${escapeHtml(item.detail)}</div>
              <div class="match-status">${escapeHtml(item.status)}</div>
            </div>
          `).join("")}
        </div>
      `;
    }

    function renderRankingsCard(data) {
      return `
        <p><strong>${escapeHtml(data.intro)}</strong></p>
        <div class="player-card">
          <div class="player-card-header">
            <div><h3 style="font-size:0.98rem; font-weight:800;">ICC World Test Championship (2025–27)</h3></div>
            <span class="tag emerald">Top 2 Reach 2027 Final</span>
          </div>
          <div class="table-wrap" style="margin-top:0; border:none; border-radius:0;">
            <table class="cric-table">
              <thead><tr>${data.wtc_headers.map(h => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead>
              <tbody>${data.wtc_rows.map(r => `<tr>${r.map((c, i) => `<td class="${i !== 1 ? 'mono' : ''}">${i === 1 ? `<strong>${escapeHtml(c)}</strong>` : escapeHtml(c)}</td>`).join("")}</tr>`).join("")}</tbody>
            </table>
          </div>
        </div>
        <div class="player-card">
          <div class="player-card-header">
            <div><h3 style="font-size:0.98rem; font-weight:800;">ICC Men's Top 5 Team Rankings</h3></div>
            <span class="tag gold">Nov 2026</span>
          </div>
          <div class="table-wrap" style="margin-top:0; border:none; border-radius:0;">
            <table class="cric-table">
              <thead><tr>${data.icc_headers.map(h => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead>
              <tbody>${data.icc_rows.map(r => `<tr>${r.map((c, i) => `<td class="${i === 0 ? 'mono' : ''}">${escapeHtml(c)}</td>`).join("")}</tr>`).join("")}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    function renderPlayerCard(p) {
      const b = p.biodata;
      return `
        <div class="player-card">
          <div class="player-card-header">
            <div class="player-identity">
              <div class="player-badge-avatar" style="background:${p.gradient}">${p.initials}</div>
              <div>
                <h3>${escapeHtml(p.name)}</h3>
                <div class="player-sub">${escapeHtml(p.country)} • ${escapeHtml(p.role)}</div>
              </div>
            </div>
            <div class="tag-row">
              <span class="tag gold">${escapeHtml(p.team)}</span>
              <span class="tag emerald">${escapeHtml(p.status)}</span>
            </div>
          </div>

          <!-- COMPLETE BIODATA SECTION -->
          <div class="biodata-section">
            <div class="biodata-title">📋 Personal & Career Biodata</div>
            <div class="biodata-grid">
              <div class="bio-item"><span class="bio-label">Full Name</span><span class="bio-value">${escapeHtml(b.full_name)}</span></div>
              <div class="bio-item"><span class="bio-label">Born / Age</span><span class="bio-value">${escapeHtml(b.dob)}</span></div>
              <div class="bio-item"><span class="bio-label">Birthplace</span><span class="bio-value">${escapeHtml(b.birthplace)}</span></div>
              <div class="bio-item"><span class="bio-label">Height & Jersey</span><span class="bio-value">${escapeHtml(b.height)} • ${escapeHtml(b.jersey)}</span></div>
              <div class="bio-item"><span class="bio-label">Batting / Bowling</span><span class="bio-value">${escapeHtml(b.batting)} / ${escapeHtml(b.bowling)}</span></div>
              <div class="bio-item"><span class="bio-label">Nicknames</span><span class="bio-value">${escapeHtml(b.nicknames)}</span></div>
              <div class="bio-item full-span"><span class="bio-label">International Debuts</span><span class="bio-value">${escapeHtml(b.debuts)}</span></div>
              <div class="bio-item full-span"><span class="bio-label">Major Teams Played</span><span class="bio-value">${escapeHtml(b.teams)}</span></div>
              <div class="bio-item full-span"><span class="bio-label">Family & Background</span><span class="bio-value">${escapeHtml(b.family)}</span></div>
            </div>
          </div>

          <div class="stats-grid">
            ${Object.entries(p.stats).map(([fmt, d]) => `
              <div class="stat-box" style="${activeFormat === fmt ? 'background:rgba(16,185,129,0.12);' : ''}">
                <div class="stat-format">${fmt}</div>
                <div class="stat-main">${escapeHtml(d.main)}</div>
                <div class="stat-sub">${escapeHtml(d.sub)}</div>
              </div>
            `).join("")}
          </div>

          <div class="highlights-box">
            <div class="highlights-title">Career Milestones & Achievements</div>
            <ul class="highlights-list">${p.highlights.map(h => `<li>${escapeHtml(h)}</li>`).join("")}</ul>
          </div>
        </div>
      `;
    }

    function renderQuizCard(q) {
      const qid = "quiz-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
      return `
        <div class="player-card" id="${qid}" data-ans="${q.answer}" data-exp="${escapeHtml(q.explain)}">
          <div class="player-card-header">
            <div><h3 style="font-size:0.98rem; font-weight:800;">🧠 CricMind Cricket Quiz</h3></div>
            <span class="tag gold">Test Your Knowledge</span>
          </div>
          <div style="padding:14px 16px;">
            <p style="font-weight:700; color:#fff;">${escapeHtml(q.question)}</p>
            <div class="quiz-options">
              ${q.options.map((opt, idx) => `
                <button class="quiz-opt-btn" data-qid="${qid}" data-idx="${idx}">${escapeHtml(opt)}</button>
              `).join("")}
            </div>
            <div class="quiz-feedback" id="${qid}-fb"></div>
          </div>
        </div>
      `;
    }

    function handleQuizAnswer(btn) {
      const qid = btn.dataset.qid;
      const chosen = Number(btn.dataset.idx);
      const card = document.getElementById(qid);
      if (!card || card.dataset.answered) return;
      card.dataset.answered = "1";

      const correctIdx = Number(card.dataset.ans);
      const btns = card.querySelectorAll(".quiz-opt-btn");
      btns.forEach((b, i) => {
        b.disabled = true;
        if (i === correctIdx) b.classList.add("correct");
        else if (i === chosen) b.classList.add("wrong");
      });

      const fb = document.getElementById(`${qid}-fb`);
      if (chosen === correctIdx) {
        quizScore += 1;
        document.getElementById("quizScoreLabel").textContent = quizScore;
        fb.textContent = "✅ Correct! " + card.dataset.exp;
      } else {
        fb.style.color = "#fca5a5";
        fb.textContent = "❌ Not quite! " + card.dataset.exp;
      }
    }

    function renderFormatCard(fmt, intro) {
      return `
        ${intro ? `<p style="margin-bottom:8px;">${escapeHtml(intro)}</p>` : ""}
        <div class="player-card">
          <div class="player-card-header">
            <div>
              <h3 style="font-size:1.02rem; font-weight:800;">${escapeHtml(fmt.title)}</h3>
              <div class="player-sub">${escapeHtml(fmt.summary)}</div>
            </div>
            <span class="tag emerald">${escapeHtml(fmt.badge)}</span>
          </div>
          <div class="table-wrap" style="margin-top:0; border:none; border-radius:0;">
            <table class="cric-table">
              <tbody>${fmt.rows.map(([k, v]) => `<tr><td style="width:34%;"><strong>${escapeHtml(k)}</strong></td><td>${escapeHtml(v)}</td></tr>`).join("")}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    function renderComparisonTable() {
      return `
        <div class="table-wrap">
          <table class="cric-table">
            <thead><tr><th>Format</th><th>Overs / Duration</th><th>Ball</th><th>Powerplay</th><th>Recent / Next Champion</th></tr></thead>
            <tbody>
              <tr><td><strong>Test</strong></td><td class="mono">5 Days (90 ov/day)</td><td>Red / Pink</td><td>None</td><td>South Africa (WTC 2025) • Next: June 2027</td></tr>
              <tr><td><strong>ODI</strong></td><td class="mono">50 Overs/side</td><td>White</td><td>1–10, 11–40, 41–50</td><td>India (CT '25) • Next WC: Oct 2027</td></tr>
              <tr><td><strong>T20I</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6</td><td>India (T20 WC 2026) • Next: 2028 + LA28</td></tr>
              <tr><td><strong>IPL</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6 + Impact Sub</td><td>RCB (2025 & 2026) • Next: IPL 2027</td></tr>
              <tr><td><strong>WPL</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6</td><td>RCB Women (2026) • Next: WPL 2027</td></tr>
            </tbody>
          </table>
        </div>
      `;
    }

    function appendUser(text) {
      const row = document.createElement("div");
      row.className = "message-row user";
      row.innerHTML = `<div class="avatar user">YOU</div><div class="bubble">${escapeHtml(text)}<span class="msg-time">${now()}</span></div>`;
      chatFeed.appendChild(row);
      chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    function appendAI(html) {
      const row = document.createElement("div");
      row.className = "message-row ai";
      row.innerHTML = `<div class="avatar ai">CM</div><div class="bubble">${html}<span class="msg-time">CricMind Pro AI • ${now()}</span></div>`;
      chatFeed.appendChild(row);
      chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    function showTyping() {
      const id = "t-" + Date.now();
      const row = document.createElement("div");
      row.id = id;
      row.className = "message-row ai";
      row.innerHTML = `<div class="avatar ai">CM</div><div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
      chatFeed.appendChild(row);
      chatFeed.scrollTop = chatFeed.scrollHeight;
      return id;
    }

    function removeTyping(id) {
      const el = document.getElementById(id);
      if (el) el.remove();
    }

    function now() { return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }
    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, m => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[m]));
    }

    init();
  </script>
</body>
</html>
"""


# ==============================================================================
# 4. FLASK ROUTES
# ==============================================================================

@app.route("/")
def index():
    return Response(HTML_PAGE, mimetype="text/html")


@app.route("/api/init")
def api_init():
    sidebar_players = [
        {
            "id": p["id"],
            "name": p["name"],
            "initials": p["initials"],
            "gradient": p["gradient"],
            "country": p["country"],
            "team": p["team"],
        }
        for p in PLAYERS
    ]
    return jsonify({
        "players": sidebar_players,
        "suggestions": SUGGESTIONS_BY_FORMAT,
        "ticker": TICKER_ITEMS,
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "")
    active_format = payload.get("format", "ALL")
    ai_reply = generate_ai_response(user_message, active_format)
    return jsonify(ai_reply)


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    print(f"🏏 CricMind AI Pro Server running at {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(debug=False, port=5000)