import re
import threading
import webbrowser
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# ==============================================================================
# 1. CRICKET KNOWLEDGE BASE (Players, Formats, Rules, Records)
# ==============================================================================

PLAYERS = [
    {
        "id": "kohli",
        "keywords": ["virat", "kohli", "king", "chiku"],
        "name": "Virat Kohli",
        "initials": "VK",
        "gradient": "linear-gradient(135deg, #dc2626, #991b1b)",
        "country": "India",
        "team": "RCB (IPL)",
        "role": "Top-Order Batter",
        "status": "Active: ODI & IPL",
        "stats": {
            "TEST": {"main": "9,230 Runs", "sub": "30x 100s | Ret. '25"},
            "ODI": {"main": "14,000+ Runs", "sub": "51+ 100s | Avg ~58"},
            "T20I": {"main": "4,188 Runs", "sub": "SR 137.0 | Ret. '24"},
            "IPL": {"main": "8,600+ Runs", "sub": "All-Time #1 | 2x Champ"},
        },
        "highlights": [
            "Helped Royal Challengers Bengaluru (RCB) win back-to-back IPL titles in 2025 & 2026.",
            "Holds the all-time world record for the most ODI centuries (surpassing Sachin Tendulkar's 49).",
            "Retired from T20Is after winning the 2024 T20 World Cup and from Test cricket in 2025.",
        ],
    },
    {
        "id": "rohit",
        "keywords": ["rohit", "sharma", "hitman"],
        "name": "Rohit Sharma",
        "initials": "RS",
        "gradient": "linear-gradient(135deg, #2563eb, #1e40af)",
        "country": "India",
        "team": "Mumbai Indians (IPL)",
        "role": "Opening Batter",
        "status": "Active: ODI & IPL",
        "stats": {
            "TEST": {"main": "4,301 Runs", "sub": "12x 100s | Ret. '25"},
            "ODI": {"main": "11,000+ Runs", "sub": "3x 200s | HS 264"},
            "T20I": {"main": "4,231 Runs", "sub": "5x 100s | Ret. '24"},
            "IPL": {"main": "6,600+ Runs", "sub": "6x IPL Winner"},
        },
        "highlights": [
            "Only cricketer in history with three ODI double centuries, including the highest ODI score (264).",
            "Captained India to undefeated ICC trophies in the 2024 T20 WC & 2025 Champions Trophy.",
            "5-time IPL-winning captain with Mumbai Indians (plus 1 title with Deccan Chargers).",
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
        "stats": {
            "TEST": {"main": "205+ Wkts", "sub": "Avg ~19.4 | Elite"},
            "ODI": {"main": "149+ Wkts", "sub": "Econ 4.59"},
            "T20I": {"main": "100+ Wkts", "sub": "2x T20 WC Champ"},
            "IPL": {"main": "165+ Wkts", "sub": "Econ ~7.3 | Lethal"},
        },
        "highlights": [
            "Player of the Match in the 2026 T20 World Cup Final & joint-highest wicket-taker (14 wickets).",
            "Also named Player of the Tournament in the 2024 T20 World Cup.",
            "Renowned for pinpoint death-over yorkers and a sub-20 Test bowling average.",
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
        "stats": {
            "TEST": {"main": "4,876 Runs", "sub": "294 Dismissals"},
            "ODI": {"main": "10,773 Runs", "sub": "Avg 50.57 | Finisher"},
            "T20I": {"main": "1,617 Runs", "sub": "SR 126.1"},
            "IPL": {"main": "5,200+ Runs", "sub": "5x IPL Titles (CSK)"},
        },
        "highlights": [
            "Only captain in cricket history to win all 3 ICC white-ball trophies (2007 T20 WC, 2011 ODI WC, 2013 CT).",
            "Led Chennai Super Kings to 5 IPL championships with iconic last-over finishing.",
            "Lightning-fast glovework with 195 international stumpings.",
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
        "status": "All-Format Star",
        "stats": {
            "TEST": {"main": "629+ Runs", "sub": "2x 100s | Avg 57+"},
            "ODI": {"main": "4,500+ Runs", "sub": "Fastest IND 100"},
            "T20I": {"main": "3,800+ Runs", "sub": "Most WT20I Runs"},
            "WPL": {"main": "1,023+ Runs", "sub": "2x WPL Champ ('24,'26)"},
        },
        "highlights": [
            "Captained RCB Women to WPL titles in 2024 and 2026 (smashing 87 off 41 in the 2026 final).",
            "Won the WPL 2026 Orange Cap (377 runs) and holds multiple ICC Cricketer of the Year awards.",
            "First Indian woman to score international centuries across Tests, ODIs, and T20Is.",
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
        "status": "All-Format Leader",
        "stats": {
            "TEST": {"main": "2,000+ Runs", "sub": "5+ 100s"},
            "ODI": {"main": "2,700+ Runs", "sub": "Avg ~59 | HS 208"},
            "T20I": {"main": "600+ Runs", "sub": "HS 126*"},
            "IPL": {"main": "3,500+ Runs", "sub": "Orange Cap '23 (890)"},
        },
        "highlights": [
            "Youngest batter in history to score an ODI double century (208 vs New Zealand).",
            "Captained Gujarat Titans to the IPL 2026 Final.",
            "Core pillar of India's modern batting lineup across all three international formats.",
        ],
    },
    {
        "id": "cummins",
        "keywords": ["pat", "cummins"],
        "name": "Pat Cummins",
        "initials": "PC",
        "gradient": "linear-gradient(135deg, #f59e0b, #b45309)",
        "country": "Australia",
        "team": "SRH (IPL)",
        "role": "Fast Bowler & Captain",
        "status": "All-Format Star",
        "stats": {
            "TEST": {"main": "290+ Wkts", "sub": "Avg ~22.4 | WTC '23"},
            "ODI": {"main": "145+ Wkts", "sub": "2023 WC Winner"},
            "T20I": {"main": "65+ Wkts", "sub": "2x WC Hat-tricks"},
            "IPL": {"main": "65+ Wkts", "sub": "SRH Captain"},
        },
        "highlights": [
            "Captained Australia to the 2023 World Test Championship & 2023 ODI World Cup titles.",
            "Recorded two consecutive hat-tricks during the 2024 ICC T20 World Cup.",
            "Led Sunrisers Hyderabad to an ultra-aggressive batting revolution as IPL captain.",
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
        "status": "White-Ball Superstar",
        "stats": {
            "TEST": {"main": "45+ Wkts", "sub": "5 Tests | 4x 5w"},
            "ODI": {"main": "198+ Wkts", "sub": "Avg ~19.8 | Econ 4.2"},
            "T20I": {"main": "160+ Wkts", "sub": "All-Time T20 Wkts #1"},
            "IPL": {"main": "155+ Wkts", "sub": "Econ ~6.8 | Finisher"},
        },
        "highlights": [
            "Captained Afghanistan to their historic first ICC World Cup semi-final in T20 WC 2024.",
            "Fastest bowler to 100 ODI wickets and all-time leading wicket-taker in T20 cricket.",
            "Explosive lower-order hitter with a T20 strike rate above 145.",
        ],
    },
    {
        "id": "samson",
        "keywords": ["sanju", "samson"],
        "name": "Sanju Samson",
        "initials": "SS",
        "gradient": "linear-gradient(135deg, #ec4899, #9d174d)",
        "country": "India",
        "team": "Rajasthan Royals (IPL)",
        "role": "Wicketkeeper-Batter",
        "status": "White-Ball Specialist",
        "stats": {
            "TEST": {"main": "—", "sub": "White-Ball Focus"},
            "ODI": {"main": "510+ Runs", "sub": "Avg 56.6 | 1x 100"},
            "T20I": {"main": "1,100+ Runs", "sub": "POTM T20 WC '26"},
            "IPL": {"main": "4,400+ Runs", "sub": "RR Captain | 3x 100s"},
        },
        "highlights": [
            "Named Player of the Tournament in the 2026 ICC T20 World Cup (321 runs at avg 80.25, SR 199.37).",
            "First Indian wicketkeeper-batter to score three T20I centuries.",
            "Dynamic top-order stroke-maker and long-time Rajasthan Royals captain.",
        ],
    },
]

FORMATS = {
    "IPL": {
        "title": "Indian Premier League (IPL)",
        "badge": "Franchise T20 • 20 Overs",
        "summary": "The world's premier franchise T20 league launched in 2008 by the BCCI, featuring 10 city-based teams across 74 matches.",
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
            ["World Cup Leaders", "Australia (6 titles, incl. 2023) | Next ODI WC: 2027 (South Africa/Zimbabwe/Namibia)"],
            ["All-Time Records", "Sachin Tendulkar (18,426 runs) | Virat Kohli (51+ 100s) | Rohit Sharma (264 HS)"],
        ],
    },
    "T20I": {
        "title": "Twenty20 International (T20I)",
        "badge": "20 Overs • Fast-Paced",
        "summary": "Cricket's fastest international format driving global expansion across 20+ World Cup nations.",
        "rows": [
            ["Match Duration", "20 overs per side (~3 hours)"],
            ["Powerplay", "Overs 1–6 (maximum 2 fielders allowed outside the 30-yard circle)"],
            ["2026 T20 World Cup", "India beat New Zealand by 96 runs (255/5 vs 159) in Ahmedabad for 3rd title"],
            ["2026 WC Stars", "POTM (Final): Jasprit Bumrah | POTT: Sanju Samson | Most Runs: Sahibzada Farhan (383)"],
            ["Most T20 World Cups", "India (3: 2007, 2024, 2026), England (2), West Indies (2)"],
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
            ["Past WTC Winners", "New Zealand (2021), Australia (2023), South Africa (2025)"],
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
        "Who won IPL 2026?",
        "Tell me about Virat Kohli",
        "Compare IPL vs ODI vs Test",
        "Who won T20 World Cup 2026?",
        "Explain Powerplay & DRS rules",
        "Jasprit Bumrah stats",
    ],
    "IPL": [
        "Who won IPL 2026?",
        "Virat Kohli IPL stats",
        "Explain Impact Player rule",
        "MS Dhoni IPL legacy",
    ],
    "ODI": [
        "Explain ODI Powerplay rules",
        "Rohit Sharma ODI records",
        "Who won Champions Trophy 2025?",
        "When is the next ODI World Cup?",
    ],
    "T20I": [
        "2026 T20 World Cup winner",
        "Sanju Samson T20 stats",
        "Rashid Khan T20I records",
        "Super Over rules explained",
    ],
    "TEST": [
        "Who won WTC 2025 Final?",
        "Pat Cummins Test stats",
        "Jasprit Bumrah Test average",
    ],
    "WPL": [
        "Who won WPL 2026?",
        "Smriti Mandhana stats",
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
    matched_players = find_matching_players(raw_query)

    # 1. Player profiles (1 or head-to-head comparison of 2+)
    if len(matched_players) >= 2:
        p1, p2 = matched_players[0], matched_players[1]
        return {
            "type": "players",
            "intro": f"Here is a head-to-head statistical breakdown of {p1['name']} and {p2['name']} across formats:",
            "players": [p1, p2],
        }

    if len(matched_players) == 1:
        p = matched_players[0]
        suffix = f" (highlighted for your {active_format} focus)" if active_format != "ALL" else ""
        return {
            "type": "players",
            "intro": f"Here is the complete {p['name']} scouting report{suffix}:",
            "players": [p],
        }

    # 2. Format comparison
    if "compare" in q or "difference" in q or "all format" in q or ("ipl" in q and "odi" in q):
        return {
            "type": "comparison",
            "intro": "Here is a side-by-side breakdown across every major cricket format:",
        }

    # 3. Specific Rules
    if "impact player" in q:
        return {
            "type": "bullets",
            "title": "⚡ IPL Impact Player Rule Explained",
            "intro": "Each IPL side names 5 substitutes at the toss and may deploy 1 Impact Player at any point (start of an innings, end of an over, or fall of a wicket) to replace a member of the playing XI.",
            "bullets": [
                "Tactical Edge: Teams sub in an extra specialist batter while chasing, or an extra death bowler while defending.",
                "Overseas Cap: If a team starts with 4 overseas players, their Impact Player must be an Indian cricketer.",
            ],
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

    if any(word in q for word in ["drs", "dls", "duckworth", "super over", "rule"]):
        return {
            "type": "bullets",
            "title": "📘 Pro Cricket Rules Breakdown",
            "intro": "Key officiating and tie-breaker systems used in modern professional cricket:",
            "bullets": [
                "DRS (Decision Review System): Combines Hawk-Eye ball-tracking & UltraEdge to review umpiring calls. In the IPL, teams can also review wides and no-balls.",
                "DLS (Duckworth-Lewis-Stern): Adjusts target scores in rain-interrupted ODI/T20 matches using remaining overs and wickets in hand.",
                "Super Over: A 1-over (6-ball, 2-wicket max) tiebreaker used in T20s and ICC knockouts until a winner is decided.",
            ],
        }

    # 4. Tournaments & Formats
    if "champions trophy" in q:
        return {
            "type": "format",
            "intro": "🏆 ICC Champions Trophy 2025: India won their 3rd title unbeaten, defeating New Zealand by 4 wickets in Dubai (Rohit Sharma: POTM with 76 off 83).",
            "format": FORMATS["ODI"],
        }

    if "world cup" in q and ("odi" in q or "50" in q or "next" in q):
        return {
            "type": "format",
            "intro": "🌍 ICC Men's ODI World Cup: Australia leads with 6 titles (incl. 2023). The next edition takes place in 2027 across South Africa, Zimbabwe, and Namibia.",
            "format": FORMATS["ODI"],
        }

    if "t20 world cup" in q or ("world cup" in q and "2026" in q):
        return {
            "type": "format",
            "intro": "🏆 2026 ICC Men's T20 World Cup: India defended their crown on home soil, beating New Zealand by 96 runs in Ahmedabad to become the first 3-time champions. Sanju Samson won Player of the Tournament.",
            "format": FORMATS["T20I"],
        }

    if "wtc" in q or "world test" in q:
        return {
            "type": "format",
            "intro": "🏆 ICC World Test Championship (WTC): South Africa defeated Australia by 5 wickets at Lord's in June 2025 to lift their maiden WTC Mace.",
            "format": FORMATS["TEST"],
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

    # 5. Greetings
    if re.match(r"^(hi|hello|hey|namaste|good morning|good evening)\b", q):
        return {
            "type": "text",
            "text": "Hey cricket fan! 👋 I'm CricMind AI (powered by Python). Ask me about IPL 2026, ODI World Cup history, Test cricket, WPL, rules, or star players like Virat Kohli, Rohit Sharma, Jasprit Bumrah, and Smriti Mandhana!",
        }

    # 6. Smart Fallback
    return {
        "type": "fallback",
        "text": f'I did not find a direct match for "{raw_query}" in my local cricket engine yet, but you can explore these topics:',
        "chips": ["Virat Kohli stats", "Who won IPL 2026?", "ODI format rules", "Compare all formats", "Smriti Mandhana stats"],
    }


# ==============================================================================
# 3. PROFESSIONAL WEB DESIGN (HTML + CSS + JS)
# ==============================================================================

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CricMind AI — Python Cricket Sports Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-app: #070b14;
      --bg-sidebar: #0c1220;
      --bg-surface: #111a2e;
      --bg-card: rgba(17, 26, 46, 0.86);
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
      --radius-lg: 18px;
      --radius-md: 12px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    html, body {
      height: 100%;
      background: var(--bg-app);
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      top: -20%;
      right: -10%;
      width: 58vw;
      height: 58vw;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.09) 0%, transparent 65%);
      pointer-events: none;
    }

    .app-shell {
      position: relative;
      z-index: 1;
      display: flex;
      height: 100dvh;
      width: 100%;
    }

    /* SIDEBAR */
    .sidebar {
      width: 300px;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 20px 16px;
      gap: 20px;
      flex-shrink: 0;
      transition: transform 0.28s ease;
      z-index: 30;
    }

    .brand { display: flex; align-items: center; justify-content: space-between; padding: 4px 6px; }
    .brand-left { display: flex; align-items: center; gap: 12px; }
    .brand-icon {
      width: 40px; height: 40px; border-radius: 12px;
      background: linear-gradient(135deg, var(--emerald), #059669);
      display: grid; place-items: center;
      box-shadow: 0 6px 20px var(--emerald-glow);
    }
    .brand-title { font-size: 1.06rem; font-weight: 800; display: flex; align-items: center; gap: 6px; }
    .pro-badge {
      font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
      background: var(--gold-glow); color: var(--gold);
      border: 1px solid rgba(245, 158, 11, 0.35);
      padding: 2px 6px; border-radius: 999px;
    }
    .brand-sub { font-size: 0.74rem; color: var(--text-secondary); margin-top: 1px; }

    .close-sidebar-btn {
      display: none; background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); width: 34px; height: 34px; border-radius: 8px; cursor: pointer; place-items: center;
    }

    .sidebar-section { display: flex; flex-direction: column; gap: 10px; }
    .section-label {
      font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--text-muted); padding: 0 6px; display: flex; justify-content: space-between;
    }

    .format-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
    .format-pill {
      display: flex; align-items: center; gap: 8px; padding: 9px 11px;
      border-radius: var(--radius-md); background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); font-family: inherit; font-size: 0.82rem; font-weight: 600;
      cursor: pointer; transition: all 0.18s ease;
    }
    .format-pill:hover { background: rgba(255,255,255,0.07); color: #fff; }
    .format-pill.active {
      background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05));
      border-color: rgba(16,185,129,0.55); color: #fff;
    }
    .format-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--text-muted); }
    .format-pill.active .format-dot { background: var(--emerald); box-shadow: 0 0 8px var(--emerald); }

    .player-list { display: flex; flex-direction: column; gap: 6px; overflow-y: auto; max-height: 290px; padding-right: 4px; }
    .player-list::-webkit-scrollbar, .chat-feed::-webkit-scrollbar { width: 5px; }
    .player-list::-webkit-scrollbar-thumb, .chat-feed::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.12); border-radius: 999px;
    }

    .player-item {
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 10px; border-radius: var(--radius-md);
      background: transparent; border: 1px solid transparent; color: var(--text-primary);
      font-family: inherit; cursor: pointer; text-align: left; width: 100%; transition: 0.18s ease;
    }
    .player-item:hover { background: var(--bg-glass); border-color: var(--border); }
    .player-item-left { display: flex; align-items: center; gap: 10px; }
    .mini-avatar {
      width: 32px; height: 32px; border-radius: 9px; display: grid; place-items: center;
      font-size: 0.72rem; font-weight: 800; color: #fff; flex-shrink: 0;
    }
    .player-item-name { font-size: 0.83rem; font-weight: 600; display: block; }
    .player-item-meta { font-size: 0.7rem; color: var(--text-muted); }

    .sidebar-footer {
      margin-top: auto; display: flex; flex-direction: column; gap: 8px;
      padding-top: 12px; border-top: 1px solid var(--border);
    }
    .action-btn {
      display: flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 12px;
      border-radius: var(--radius-md); background: var(--bg-glass); border: 1px solid var(--border);
      color: var(--text-secondary); font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer;
    }
    .action-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }

    /* MAIN STAGE */
    .main-stage { flex: 1; display: flex; flex-direction: column; min-width: 0; height: 100dvh; }
    .topbar {
      height: 66px; padding: 0 24px; border-bottom: 1px solid var(--border);
      background: rgba(7, 11, 20, 0.75); backdrop-filter: blur(14px);
      display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
    }
    .topbar-left { display: flex; align-items: center; gap: 12px; }
    .menu-btn {
      display: none; background: var(--bg-glass); border: 1px solid var(--border);
      color: #fff; width: 38px; height: 38px; border-radius: 10px; cursor: pointer; place-items: center;
    }
    .status-pill {
      display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px;
      background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.28);
      font-size: 0.78rem; font-weight: 600; color: #6ee7b7;
    }
    .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); animation: pulse 2s infinite; }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
      70% { box-shadow: 0 0 0 7px rgba(16,185,129,0); }
      100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    .context-chip {
      font-size: 0.76rem; font-weight: 700; color: var(--text-secondary);
      background: var(--bg-glass); border: 1px solid var(--border); padding: 6px 12px; border-radius: 999px;
    }
    .context-chip span { color: var(--gold); }

    /* CHAT FEED */
    .chat-feed {
      flex: 1; overflow-y: auto; padding: 26px 24px 18px;
      display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth;
    }
    .message-row { display: flex; gap: 14px; max-width: 900px; width: 100%; margin: 0 auto; animation: fadeUp 0.25s ease; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .message-row.user { justify-content: flex-end; }
    .avatar {
      width: 36px; height: 36px; border-radius: 11px; display: grid; place-items: center;
      flex-shrink: 0; font-size: 0.78rem; font-weight: 800; color: #fff;
    }
    .avatar.ai { background: linear-gradient(135deg, var(--emerald), #047857); }
    .avatar.user { background: linear-gradient(135deg, var(--blue), #1d4ed8); order: 2; }
    .bubble { border-radius: var(--radius-lg); padding: 15px 18px; line-height: 1.6; font-size: 0.93rem; }
    .message-row.user .bubble {
      max-width: 76%; background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff; border-bottom-right-radius: 4px;
    }
    .message-row.ai .bubble {
      max-width: 85%; background: var(--bg-card); border: 1px solid var(--border);
      color: var(--text-primary); border-top-left-radius: 4px; box-shadow: 0 12px 32px rgba(0,0,0,0.35);
    }
    .msg-time { font-size: 0.68rem; color: var(--text-muted); margin-top: 6px; display: block; }
    .message-row.user .msg-time { color: rgba(255,255,255,0.72); text-align: right; }

    /* CARDS */
    .feature-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .starter-btn {
      background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: #a7f3d0;
      padding: 7px 12px; border-radius: 999px; font-family: inherit; font-size: 0.79rem; font-weight: 600; cursor: pointer;
    }
    .starter-btn:hover { background: rgba(16,185,129,0.22); color: #fff; }

    .player-card {
      margin-top: 12px; background: rgba(7,11,20,0.65); border: 1px solid var(--border-strong);
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
    .player-sub { font-size: 0.78rem; color: var(--text-secondary); }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      font-size: 0.7rem; font-weight: 700; padding: 3px 9px; border-radius: 999px;
      background: var(--bg-glass); border: 1px solid var(--border); color: var(--text-secondary);
    }
    .tag.gold { background: var(--gold-glow); border-color: rgba(245,158,11,0.35); color: #fcd34d; }
    .tag.emerald { background: var(--emerald-glow); border-color: rgba(16,185,129,0.35); color: #6ee7b7; }

    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid var(--border); }
    .stat-box { padding: 12px 10px; text-align: center; border-right: 1px solid var(--border); }
    .stat-box:last-child { border-right: none; }
    .stat-format { font-size: 0.68rem; font-weight: 700; color: var(--emerald); margin-bottom: 4px; }
    .stat-main { font-family: 'JetBrains Mono', monospace; font-size: 0.92rem; font-weight: 700; color: #fff; }
    .stat-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-secondary); margin-top: 2px; }

    .highlights-box { padding: 12px 16px; }
    .highlights-title { font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: var(--gold); margin-bottom: 6px; }
    .highlights-list { list-style: none; display: flex; flex-direction: column; gap: 5px; }
    .highlights-list li { font-size: 0.83rem; color: var(--text-secondary); padding-left: 14px; position: relative; }
    .highlights-list li::before { content: "▸"; position: absolute; left: 0; color: var(--emerald); }

    .table-wrap { margin-top: 12px; overflow-x: auto; border-radius: var(--radius-md); border: 1px solid var(--border-strong); background: rgba(7,11,20,0.65); }
    table.cric-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: left; }
    table.cric-table th { background: rgba(16,185,129,0.12); color: #6ee7b7; padding: 10px 12px; border-bottom: 1px solid var(--border); }
    table.cric-table td { padding: 9px 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
    table.cric-table tr:last-child td { border-bottom: none; }
    table.cric-table td strong { color: #fff; }
    .mono { font-family: 'JetBrains Mono', monospace; color: #fff; }

    .typing-dots { display: inline-flex; gap: 5px; padding: 6px 2px; }
    .typing-dots span { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); animation: bounce 1.3s infinite ease-in-out; }
    .typing-dots span:nth-child(2) { animation-delay: 0.16s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.32s; }
    @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1.1); opacity: 1; } }

    /* COMPOSER */
    .composer-area { padding: 10px 24px 20px; background: linear-gradient(to top, var(--bg-app) 75%, transparent); flex-shrink: 0; }
    .composer-inner { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }
    .suggestion-bar { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }
    .suggestion-bar::-webkit-scrollbar { display: none; }
    .suggestion-chip {
      white-space: nowrap; padding: 6px 12px; border-radius: 999px; background: var(--bg-glass);
      border: 1px solid var(--border); color: var(--text-secondary); font-family: inherit;
      font-size: 0.76rem; font-weight: 600; cursor: pointer;
    }
    .suggestion-chip:hover { background: rgba(16,185,129,0.14); border-color: rgba(16,185,129,0.4); color: #fff; }

    .input-box {
      display: flex; align-items: center; gap: 10px; background: var(--bg-surface);
      border: 1px solid var(--border-strong); border-radius: 16px; padding: 8px 8px 8px 16px;
    }
    .input-box:focus-within { border-color: var(--emerald); box-shadow: 0 0 0 3px var(--emerald-glow); }
    .chat-input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-family: inherit; font-size: 0.94rem; padding: 6px 0; }
    .chat-input::placeholder { color: var(--text-muted); }
    .send-btn {
      width: 42px; height: 42px; border-radius: 12px; border: none;
      background: linear-gradient(135deg, var(--emerald), #059669); color: #fff; display: grid; place-items: center; cursor: pointer;
    }

    .backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 25; }
    @media (max-width: 860px) {
      .sidebar { position: fixed; top: 0; left: 0; bottom: 0; transform: translateX(-100%); }
      .sidebar.open { transform: translateX(0); }
      .backdrop.open { display: block; }
      .menu-btn, .close-sidebar-btn { display: grid; }
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .stat-box:nth-child(2) { border-right: none; }
      .stat-box:nth-child(1), .stat-box:nth-child(2) { border-bottom: 1px solid var(--border); }
      .message-row.ai .bubble, .bubble { max-width: 92%; }
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
            <div class="brand-title">CricMind <span class="pro-badge">Python AI</span></div>
            <div class="brand-sub">Global Cricket Intelligence</div>
          </div>
        </div>
        <button class="close-sidebar-btn" id="closeSidebarBtn">✕</button>
      </div>

      <div class="sidebar-section">
        <div class="section-label"><span>Cricket Formats</span><span style="color:var(--emerald)">Active</span></div>
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
        <div class="section-label"><span>Star Players</span><span>Tap for Stats</span></div>
        <div class="player-list" id="playerList"></div>
      </div>

      <div class="sidebar-footer">
        <button class="action-btn" id="compareBtn">📊 Compare All Formats</button>
        <button class="action-btn" id="clearChatBtn">🗑️ Clear Conversation</button>
      </div>
    </aside>

    <main class="main-stage">
      <header class="topbar">
        <div class="topbar-left">
          <button class="menu-btn" id="openSidebarBtn">☰</button>
          <div class="status-pill"><span class="pulse-dot"></span>Python Flask AI Online</div>
        </div>
        <div class="context-chip">Format Focus: <span id="activeFormatLabel">ALL FORMATS</span></div>
      </header>

      <section class="chat-feed" id="chatFeed"></section>

      <footer class="composer-area">
        <div class="composer-inner">
          <div class="suggestion-bar" id="suggestionBar"></div>
          <form class="input-box" id="chatForm">
            <input type="text" class="chat-input" id="userInput" placeholder="Ask about IPL, ODI, Test, T20I, WPL, rules, or any player..." required autocomplete="off" />
            <button type="submit" class="send-btn" aria-label="Send">➤</button>
          </form>
        </div>
      </footer>
    </main>
  </div>

  <script>
    let activeFormat = "ALL";
    let suggestionsMap = {};
    const chatFeed = document.getElementById("chatFeed");
    const suggestionBar = document.getElementById("suggestionBar");
    const playerListEl = document.getElementById("playerList");
    const activeFormatLabel = document.getElementById("activeFormatLabel");
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.getElementById("backdrop");

    async function init() {
      const res = await fetch("/api/init");
      const data = await res.json();
      suggestionsMap = data.suggestions;
      renderPlayerSidebar(data.players);
      renderSuggestions();
      showWelcomeMessage();

      document.getElementById("openSidebarBtn").addEventListener("click", () => {
        sidebar.classList.add("open"); backdrop.classList.add("open");
      });
      const closeMenu = () => { sidebar.classList.remove("open"); backdrop.classList.remove("open"); };
      document.getElementById("closeSidebarBtn").addEventListener("click", closeMenu);
      backdrop.addEventListener("click", closeMenu);

      document.getElementById("formatGrid").addEventListener("click", (e) => {
        const pill = e.target.closest(".format-pill");
        if (!pill) return;
        setActiveFormat(pill.dataset.format);
        if (window.innerWidth <= 860) closeMenu();
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
        const input = document.getElementById("userInput");
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        sendQuery(text);
      });

      chatFeed.addEventListener("click", (e) => {
        const btn = e.target.closest(".inline-q");
        if (btn) sendQuery(btn.dataset.q);
      });
    }

    function renderPlayerSidebar(players) {
      playerListEl.innerHTML = players.map(p => `
        <button class="player-item" data-name="${p.name}">
          <span class="player-item-left">
            <span class="mini-avatar" style="background:${p.gradient}">${p.initials}</span>
            <span>
              <span class="player-item-name">${p.name}</span>
              <span class="player-item-meta">${p.country} • ${p.team}</span>
            </span>
          </span>
          <span>›</span>
        </button>
      `).join("");

      playerListEl.addEventListener("click", (e) => {
        const btn = e.target.closest(".player-item");
        if (!btn) return;
        if (window.innerWidth <= 860) {
          sidebar.classList.remove("open"); backdrop.classList.remove("open");
        }
        sendQuery(`Tell me about ${btn.dataset.name}`);
      });
    }

    function setActiveFormat(fmt) {
      activeFormat = fmt;
      document.querySelectorAll(".format-pill").forEach(b => b.classList.toggle("active", b.dataset.format === fmt));
      activeFormatLabel.textContent = fmt === "ALL" ? "ALL FORMATS" : fmt;
      renderSuggestions();
      if (fmt !== "ALL") sendQuery(`Tell me about ${fmt} format`);
    }

    function renderSuggestions() {
      const list = suggestionsMap[activeFormat] || suggestionsMap.ALL || [];
      suggestionBar.innerHTML = list.map(q => `<button class="suggestion-chip" type="button">${q}</button>`).join("");
      suggestionBar.querySelectorAll(".suggestion-chip").forEach(chip => {
        chip.addEventListener("click", () => sendQuery(chip.textContent));
      });
    }

    function showWelcomeMessage() {
      appendAI(`
        <h2 style="font-size:1.15rem; font-weight:800; margin-bottom:6px;">🏏 Welcome to CricMind AI (Python Edition)</h2>
        <p style="color:var(--text-secondary); font-size:0.9rem;">
          Ask me anything about <strong>IPL, ODI, T20I, Test, WPL</strong>, cricket rules, or any <strong>player's career stats</strong>.
        </p>
        <div class="feature-pills">
          <button class="starter-btn inline-q" data-q="Tell me about Virat Kohli">🔥 Virat Kohli Stats</button>
          <button class="starter-btn inline-q" data-q="Who won IPL 2026?">🏆 IPL 2026 Champions</button>
          <button class="starter-btn inline-q" data-q="Compare all cricket formats">📊 Compare Formats</button>
          <button class="starter-btn inline-q" data-q="Smriti Mandhana stats">⚡ Smriti Mandhana</button>
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
      if (data.type === "players") {
        return `<p>${escapeHtml(data.intro)}</p>` + data.players.map(renderPlayerCard).join("");
      }
      if (data.type === "format") {
        return renderFormatCard(data.format, data.intro);
      }
      if (data.type === "comparison") {
        return `<p>${escapeHtml(data.intro)}</p>` + renderComparisonTable();
      }
      if (data.type === "bullets") {
        return `
          <p><strong>${escapeHtml(data.title)}</strong></p>
          <p style="margin-top:6px; color:var(--text-secondary);">${escapeHtml(data.intro)}</p>
          <ul class="highlights-list" style="margin-top:10px;">
            ${data.bullets.map(b => `<li>${escapeHtml(b)}</li>`).join("")}
          </ul>
        `;
      }
      if (data.type === "table") {
        return `
          <p><strong>${escapeHtml(data.intro)}</strong></p>
          <div class="table-wrap">
            <table class="cric-table">
              <thead><tr>${data.headers.map(h => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead>
              <tbody>${data.rows.map(r => `<tr>${r.map((c, i) => `<td class="${i > 0 ? 'mono' : ''}">${i === 0 ? `<strong>${escapeHtml(c)}</strong>` : escapeHtml(c)}</td>`).join("")}</tr>`).join("")}</tbody>
            </table>
          </div>
        `;
      }
      if (data.type === "fallback") {
        return `
          <p>${escapeHtml(data.text)}</p>
          <div class="feature-pills">
            ${data.chips.map(c => `<button class="starter-btn inline-q" data-q="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join("")}
          </div>
        `;
      }
      return `<p>${escapeHtml(data.text)}</p>`;
    }

    function renderPlayerCard(p) {
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
            <div class="highlights-title">Career Milestones & Highlights</div>
            <ul class="highlights-list">${p.highlights.map(h => `<li>${escapeHtml(h)}</li>`).join("")}</ul>
          </div>
        </div>
      `;
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
            <thead><tr><th>Format</th><th>Overs / Duration</th><th>Ball</th><th>Powerplay</th><th>Recent Champion</th></tr></thead>
            <tbody>
              <tr><td><strong>Test</strong></td><td class="mono">5 Days (90 ov/day)</td><td>Red / Pink</td><td>None</td><td>South Africa (WTC 2025)</td></tr>
              <tr><td><strong>ODI</strong></td><td class="mono">50 Overs/side</td><td>White</td><td>1–10, 11–40, 41–50</td><td>Australia (WC '23) / India (CT '25)</td></tr>
              <tr><td><strong>T20I</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6</td><td>India (T20 WC 2026)</td></tr>
              <tr><td><strong>IPL</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6 + Impact Sub</td><td>RCB (2025 & 2026)</td></tr>
              <tr><td><strong>WPL</strong></td><td class="mono">20 Overs/side</td><td>White</td><td>Overs 1–6</td><td>RCB Women (2026)</td></tr>
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
      row.innerHTML = `<div class="avatar ai">CM</div><div class="bubble">${html}<span class="msg-time">CricMind Python AI • ${now()}</span></div>`;
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
    return jsonify({"players": sidebar_players, "suggestions": SUGGESTIONS_BY_FORMAT})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "")
    active_format = payload.get("format", "ALL")
    ai_reply = generate_ai_response(user_message, active_format)
    return jsonify(ai_reply)


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    print(f"🏏 CricMind AI Server running at {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(debug=False, port=5000)