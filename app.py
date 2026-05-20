from __future__ import annotations

import html
import math
from textwrap import dedent
from typing import Dict, Iterable, List

import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

APP_NAME = "FinWise India"
RUPEE = "\u20b9"

DEFAULTS = {
    "equity_return": 11.0,
    "debt_return": 7.0,
    "gold_return": 7.0,
    "liquid_return": 5.5,
    "inflation": 6.0,
    "home_loan_rate": 8.5,
    "car_loan_rate": 9.0,
    "consumer_loan_rate": 14.0,
}

MARKET_TICKERS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "GOLD": "GC=F",
    "USD/INR": "INR=X",
}

ASSET_PRESETS = {
    "Car": 1_200_000,
    "Phone": 90_000,
    "Gold": 300_000,
    "Bike": 180_000,
    "Laptop": 120_000,
    "Custom": 500_000,
}


st.set_page_config(
    page_title=APP_NAME,
    page_icon=RUPEE,
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #06111f;
    --panel: #0a1220;
    --panel-2: #0c1728;
    --panel-3: #101f36;
    --line: rgba(96, 165, 250, 0.20);
    --blue: #2f9bff;
    --cyan: #21d4fd;
    --pink: #f43f8b;
    --violet: #a855f7;
    --green: #10b981;
    --amber: #fbbf24;
    --text: #f8fafc;
    --muted: #b8c2d3;
    --subtle: #7d8ba1;
}

html, body, [class*="css"] {
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--text);
    background: var(--bg);
}

.stApp {
    background:
        radial-gradient(circle at 15% 8%, rgba(47, 155, 255, 0.24), transparent 28rem),
        radial-gradient(circle at 85% 12%, rgba(244, 63, 139, 0.12), transparent 26rem),
        linear-gradient(180deg, #07172a 0%, #050910 54%, #07111f 100%);
}

main .block-container {
    max-width: 1320px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: var(--text);
    letter-spacing: 0;
}

section[data-testid="stSidebar"],
div[data-testid="stSidebar"],
div[data-testid="collapsedControl"],
button[kind="header"] {
    display: none;
}

header[data-testid="stHeader"] {
    background: transparent;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}

.top-shell {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 1.2rem;
    align-items: stretch;
    margin-bottom: 1rem;
}

.hero-panel,
.panel,
.metric-card,
.plan-card,
.neon-card {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(145deg, rgba(11, 21, 38, 0.96), rgba(7, 13, 25, 0.98));
    border: 1px solid var(--line);
    border-radius: 18px;
    box-shadow: 0 22px 52px rgba(0, 0, 0, 0.28);
}

.hero-panel {
    min-height: 340px;
    padding: 2rem;
}

.hero-panel::before,
.panel::before,
.neon-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(115deg, rgba(47, 155, 255, 0.18), transparent 38%, rgba(244, 63, 139, 0.10)),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0 1px, transparent 1px 76px);
    pointer-events: none;
}

.kicker {
    position: relative;
    color: var(--cyan);
    font-size: 0.76rem;
    font-weight: 900;
    letter-spacing: 0.16rem;
    text-transform: uppercase;
}

.hero-title {
    position: relative;
    color: var(--text);
    font-size: clamp(2.7rem, 7vw, 6rem);
    font-weight: 900;
    line-height: 0.96;
    margin: 0.5rem 0 0.8rem;
}

.hero-copy {
    position: relative;
    color: var(--muted);
    font-size: clamp(1rem, 1.4vw, 1.18rem);
    line-height: 1.6;
    max-width: 720px;
}

.status-row {
    position: relative;
    display: flex;
    flex-wrap: wrap;
    gap: 0.7rem;
    margin-top: 1.4rem;
}

.status-pill {
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    border: 1px solid rgba(47, 155, 255, 0.34);
    border-radius: 999px;
    padding: 0.45rem 0.8rem;
    color: #dbeafe;
    background: rgba(47, 155, 255, 0.10);
    font-weight: 700;
    font-size: 0.86rem;
}

.credit-card {
    position: relative;
    min-height: 340px;
    border-radius: 18px;
    padding: 1.4rem;
    background:
        radial-gradient(circle at 85% 15%, rgba(33, 212, 253, 0.34), transparent 11rem),
        radial-gradient(circle at 20% 85%, rgba(244, 63, 139, 0.36), transparent 12rem),
        linear-gradient(135deg, #10153a 0%, #0a0c1f 54%, #21124a 100%);
    border: 1px solid rgba(33, 212, 253, 0.34);
    box-shadow: 0 24px 62px rgba(0, 0, 0, 0.34);
}

.card-brand {
    color: var(--text);
    font-weight: 900;
    font-size: 1.25rem;
}

.card-number {
    color: var(--text);
    font-size: clamp(1.25rem, 2.1vw, 2rem);
    font-weight: 800;
    letter-spacing: 0.18rem;
    margin-top: 5.4rem;
}

.card-line {
    display: flex;
    justify-content: space-between;
    color: #dbeafe;
    margin-top: 1.6rem;
    font-weight: 700;
}

.section-title {
    color: var(--text);
    font-weight: 900;
    font-size: 1.22rem;
    margin: 1.15rem 0 0.75rem;
}

.section-subtitle {
    color: var(--subtle);
    margin-top: -0.35rem;
    margin-bottom: 1rem;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.metric-card {
    min-height: 128px;
    padding: 1rem;
}

.metric-label {
    position: relative;
    color: var(--subtle);
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
}

.metric-value {
    position: relative;
    color: var(--text);
    font-size: clamp(1.45rem, 2.8vw, 2.25rem);
    font-weight: 900;
    margin-top: 0.55rem;
}

.metric-note {
    position: relative;
    color: var(--muted);
    font-size: 0.86rem;
    margin-top: 0.35rem;
}

.panel {
    padding: 1rem;
    min-height: 100%;
}

.panel-head {
    position: relative;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: center;
    margin-bottom: 0.7rem;
}

.panel-title {
    color: var(--text);
    font-weight: 900;
    font-size: 1.08rem;
}

.panel-tag {
    color: #dbeafe;
    background: rgba(47, 155, 255, 0.12);
    border: 1px solid rgba(47, 155, 255, 0.28);
    border-radius: 999px;
    padding: 0.35rem 0.65rem;
    font-size: 0.78rem;
    font-weight: 800;
}

.plan-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
}

.plan-card {
    padding: 1rem;
    min-height: 190px;
}

.plan-card strong {
    position: relative;
    display: block;
    color: var(--text);
    font-size: 1.05rem;
    margin-bottom: 0.35rem;
}

.plan-card span {
    position: relative;
    display: block;
    color: var(--muted);
    line-height: 1.45;
}

.plan-amount {
    position: relative;
    color: var(--cyan);
    font-size: 1.45rem;
    font-weight: 900;
    margin: 0.8rem 0 0.25rem;
}

.progress-track {
    position: relative;
    height: 0.65rem;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(148, 163, 184, 0.16);
    margin-top: 0.75rem;
}

.progress-fill {
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--blue), var(--cyan), var(--pink));
}

.asset-strip {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 0.7rem;
    margin: 0.5rem 0 1rem;
}

.asset-tile {
    border: 1px solid rgba(96, 165, 250, 0.26);
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.78);
    color: var(--muted);
    padding: 0.8rem;
    text-align: center;
    font-weight: 800;
}

.asset-tile-active {
    border-color: rgba(33, 212, 253, 0.74);
    color: var(--text);
    background: linear-gradient(135deg, rgba(47, 155, 255, 0.30), rgba(244, 63, 139, 0.16));
}

.insight-list {
    display: grid;
    gap: 0.7rem;
}

.insight-item {
    position: relative;
    border-left: 3px solid var(--blue);
    background: rgba(15, 23, 42, 0.78);
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 0.85rem;
    color: var(--muted);
    line-height: 1.45;
}

.insight-item strong {
    color: var(--text);
}

.danger-item {
    border-left-color: #ef4444;
    background: rgba(127, 29, 29, 0.38);
    color: #fecaca;
}

.watch-item {
    border-left-color: #f59e0b;
    background: rgba(120, 53, 15, 0.34);
    color: #fed7aa;
}

.good-item {
    border-left-color: #10b981;
    background: rgba(6, 78, 59, 0.34);
    color: #bbf7d0;
}

.projection-table {
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 14px;
    margin-top: 0.8rem;
}

.projection-table th,
.projection-table td {
    border-bottom: 1px solid rgba(96, 165, 250, 0.14);
    padding: 0.82rem;
    text-align: left;
}

.projection-table th {
    color: #dbeafe;
    background: rgba(47, 155, 255, 0.16);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
}

.projection-table td {
    color: var(--muted);
    background: rgba(15, 23, 42, 0.68);
}

.projection-table tr:last-child td {
    border-bottom: 0;
}

.rule-chip {
    display: inline-flex;
    align-items: center;
    min-height: 34px;
    border-radius: 999px;
    padding: 0.35rem 0.7rem;
    margin: 0.2rem 0.25rem 0.2rem 0;
    font-weight: 850;
    font-size: 0.82rem;
    border: 1px solid rgba(96, 165, 250, 0.22);
    background: rgba(15, 23, 42, 0.70);
    color: var(--muted);
}

.rule-chip-red {
    color: #fecaca;
    border-color: rgba(239, 68, 68, 0.50);
    background: rgba(127, 29, 29, 0.34);
}

.rule-chip-green {
    color: #bbf7d0;
    border-color: rgba(16, 185, 129, 0.50);
    background: rgba(6, 78, 59, 0.34);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    border-bottom: 1px solid rgba(96, 165, 250, 0.18);
}

.stTabs [data-baseweb="tab"] {
    min-height: 44px;
    color: var(--muted);
    background: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(96, 165, 250, 0.16);
    border-radius: 12px 12px 0 0;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    background: linear-gradient(135deg, rgba(47, 155, 255, 0.30), rgba(168, 85, 247, 0.16));
    border-color: rgba(47, 155, 255, 0.54);
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(11, 21, 38, 0.96), rgba(7, 13, 25, 0.98));
    border: 1px solid rgba(96, 165, 250, 0.20);
    border-radius: 16px;
    padding: 1rem;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text);
    font-weight: 900;
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: 46px;
    border-radius: 12px;
    border: 1px solid rgba(47, 155, 255, 0.48);
    background: linear-gradient(135deg, #2f9bff, #21d4fd);
    color: #03111f;
    font-weight: 900;
}

label, .stRadio label, .stSelectbox label, .stNumberInput label, .stSlider label {
    color: var(--muted) !important;
    font-weight: 750 !important;
}

@media (max-width: 980px) {
    main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .top-shell,
    .metric-grid,
    .plan-grid,
    .asset-strip {
        grid-template-columns: 1fr;
    }

    .hero-panel,
    .credit-card {
        min-height: auto;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def html_block(markup: str) -> None:
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


def clamp(value: float, lower: float = 0, upper: float = 100) -> float:
    return max(lower, min(value, upper))


def format_inr(value: float, compact: bool = False) -> str:
    if value is None or not math.isfinite(float(value)):
        return f"{RUPEE}0"

    sign = "-" if value < 0 else ""
    value = abs(float(value))

    if compact:
        if value >= 10_000_000:
            return f"{sign}{RUPEE}{value / 10_000_000:.2f} Cr"
        if value >= 100_000:
            return f"{sign}{RUPEE}{value / 100_000:.2f} L"

    rounded = int(round(value))
    digits = str(rounded)
    if len(digits) <= 3:
        formatted = digits
    else:
        last_three = digits[-3:]
        rest = digits[:-3]
        groups: List[str] = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ",".join(groups + [last_three])

    return f"{sign}{RUPEE}{formatted}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def safe_months(years: float) -> int:
    return max(int(round(years * 12)), 1)


def future_value_lump_sum(amount: float, annual_rate: float, years: float) -> float:
    if amount <= 0:
        return 0.0
    return amount * ((1 + max(annual_rate, 0) / 100) ** years)


def future_value_monthly(monthly_investment: float, annual_rate: float, years: float) -> float:
    months = safe_months(years)
    r = max(annual_rate, 0) / (12 * 100)
    if monthly_investment <= 0:
        return 0.0
    if r == 0:
        return monthly_investment * months
    return monthly_investment * (((1 + r) ** months - 1) / r)


def calculate_emi(principal: float, annual_rate: float, years: float) -> float:
    months = safe_months(years)
    r = max(annual_rate, 0) / (12 * 100)
    if principal <= 0:
        return 0.0
    if r == 0:
        return principal / months
    return principal * r * ((1 + r) ** months) / (((1 + r) ** months) - 1)


def loan_from_emi(max_emi: float, annual_rate: float, years: float) -> float:
    months = safe_months(years)
    r = max(annual_rate, 0) / (12 * 100)
    if max_emi <= 0:
        return 0.0
    if r == 0:
        return max_emi * months
    return max_emi * (((1 + r) ** months) - 1) / (r * ((1 + r) ** months))


def sip_needed(target: float, current_saved: float, annual_rate: float, years: float) -> float:
    future_current = future_value_lump_sum(current_saved, annual_rate, years)
    gap = max(target - future_current, 0)
    months = safe_months(years)
    r = max(annual_rate, 0) / (12 * 100)
    if gap <= 0:
        return 0.0
    if r == 0:
        return gap / months
    factor = ((1 + r) ** months - 1) / r
    return gap / factor


def months_to_goal(target: float, current_saved: float, monthly: float, annual_rate: float) -> int | None:
    if target <= current_saved:
        return 0
    if monthly <= 0:
        return None

    r = max(annual_rate, 0) / (12 * 100)
    for month in range(1, 601):
        if r == 0:
            value = current_saved + monthly * month
        else:
            value = current_saved * ((1 + r) ** month) + monthly * (((1 + r) ** month - 1) / r)
        if value >= target:
            return month
    return None


def projection_rows(
    current_savings: float,
    monthly: float,
    annual_rate: float,
    years: Iterable[int],
    reinvest: bool,
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for year in years:
        yearly = monthly * 12
        invested = current_savings + yearly * year
        if reinvest:
            corpus = future_value_lump_sum(current_savings, annual_rate, year) + future_value_monthly(
                monthly, annual_rate, year
            )
            mode = "Compounded"
        else:
            simple_gain = invested * (annual_rate / 100) * year
            corpus = invested + simple_gain
            mode = "Profit not reinvested"
        profit = max(corpus - invested, 0)
        rows.append(
            {
                "Year": f"{year}Y",
                "Monthly SIP": format_inr(monthly),
                "Yearly SIP": format_inr(yearly),
                "Total Invested": format_inr(invested),
                "Growth / Profit": format_inr(profit),
                "Corpus": format_inr(corpus),
                "Mode": mode,
            }
        )
    return rows


def render_projection_table(rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    markup = ['<table class="projection-table"><thead><tr>']
    markup.extend(f"<th>{html.escape(header)}</th>" for header in headers)
    markup.append("</tr></thead><tbody>")
    for row in rows:
        markup.append("<tr>")
        markup.extend(f"<td>{html.escape(str(row[header]))}</td>" for header in headers)
        markup.append("</tr>")
    markup.append("</tbody></table>")
    html_block("".join(markup))


def instrument_plan_for_risk(risk: str, profile: str) -> List[Dict[str, str]]:
    if risk == "Low" or profile in {"Foundation Builder", "Capital Protector"}:
        return [
            {
                "Bucket": "Safety",
                "Where to study": "Low risk",
                "Example": "Bank FD, liquid fund, short-duration debt fund",
                "Why": "Protects emergency and near-term money.",
            },
            {
                "Bucket": "Market core",
                "Where to study": "Low to medium risk",
                "Example": "Nifty 50 index fund / ETF",
                "Why": "Broad market exposure without choosing individual stocks.",
            },
            {
                "Bucket": "Diversifier",
                "Where to study": "Diversifier",
                "Example": "Gold ETF / Sovereign Gold Bond when suitable",
                "Why": "Adds diversification against shocks.",
            },
        ]
    if risk == "Medium":
        return [
            {
                "Bucket": "Core SIP",
                "Where to study": "Medium risk",
                "Example": "Nifty 50 or Sensex index fund",
                "Why": "Base long-term equity allocation.",
            },
            {
                "Bucket": "Growth SIP",
                "Where to study": "Medium to high risk",
                "Example": "Nifty Next 50 / flexi-cap category",
                "Why": "Adds growth without going fully aggressive.",
            },
            {
                "Bucket": "Stability",
                "Where to study": "Low risk",
                "Example": "Short-duration debt fund / FD",
                "Why": "Balances equity volatility.",
            },
        ]
    return [
        {
            "Bucket": "Core equity",
            "Where to study": "Medium risk",
            "Example": "Nifty 50 index fund / ETF",
            "Why": "Keeps aggressive plan anchored.",
        },
        {
            "Bucket": "Growth equity",
            "Where to study": "High risk",
            "Example": "Mid-cap index / diversified active category",
            "Why": "Higher potential return with higher volatility.",
        },
        {
            "Bucket": "Satellite research",
            "Where to study": "Very high risk",
            "Example": "Quality large-cap stocks after research only",
            "Why": "Use small allocation and avoid concentrated bets.",
        },
    ]


def render_instrument_cards(items: List[Dict[str, str]]) -> None:
    cards = ['<div class="plan-grid">']
    for item in items:
        cards.append(
            '<div class="plan-card">'
            f"<strong>{html.escape(item['Bucket'])}</strong>"
            f"<span>{html.escape(item['Example'])}</span>"
            f'<div class="plan-amount">{html.escape(item["Where to study"])}</div>'
            f"<span>{html.escape(item['Why'])}</span>"
            "</div>"
        )
    cards.append("</div>")
    html_block("".join(cards))


def asset_rule_defaults(asset_type: str) -> Dict[str, float | str]:
    rules = {
        "Home": {
            "rate": DEFAULTS["home_loan_rate"],
            "tenure": 20,
            "down_payment": 20,
            "safe_emi_pct": 35,
            "inflation": 6,
            "rule": "Home: keep total EMIs around 35-40% of monthly income; lenders also check FOIR, credit score, age, and stability.",
        },
        "Car": {
            "rate": DEFAULTS["car_loan_rate"],
            "tenure": 4,
            "down_payment": 20,
            "safe_emi_pct": 10,
            "inflation": 4,
            "rule": "Car: 20/4/10 rule means 20% down payment, 4-year loan, EMI near 10% of monthly income.",
        },
        "Phone": {
            "rate": DEFAULTS["consumer_loan_rate"],
            "tenure": 1,
            "down_payment": 100,
            "safe_emi_pct": 5,
            "inflation": 3,
            "rule": "Phone: prefer cash saving; avoid EMI if it delays emergency fund or SIP.",
        },
        "Gold": {
            "rate": DEFAULTS["gold_return"],
            "tenure": 3,
            "down_payment": 100,
            "safe_emi_pct": 5,
            "inflation": 6,
            "rule": "Gold: treat as a diversifier, not a shortcut to wealth.",
        },
        "Other": {
            "rate": DEFAULTS["debt_return"],
            "tenure": 3,
            "down_payment": 50,
            "safe_emi_pct": 8,
            "inflation": 5,
            "rule": "Custom asset: protect emergency fund first and keep EMI small.",
        },
    }
    return rules[asset_type]


def profile_from_inputs(age: int, savings_rate: float, emergency_months: float, risk: str) -> tuple[str, int]:
    score = 0
    score += 25 if age < 35 else 18 if age < 50 else 10
    score += 25 if savings_rate >= 0.30 else 18 if savings_rate >= 0.18 else 10 if savings_rate >= 0.08 else 3
    score += 25 if emergency_months >= 6 else 16 if emergency_months >= 3 else 6
    score += {"Low": 7, "Medium": 16, "High": 25}[risk]
    score = int(clamp(score))

    if emergency_months < 3 or savings_rate < 0.08:
        return "Foundation Builder", score
    if score >= 78:
        return "Growth Investor", score
    if score >= 58:
        return "Balanced Investor", score
    return "Capital Protector", score


def allocation_for_profile(profile: str, emergency_months: float) -> Dict[str, int]:
    if emergency_months < 6:
        return {
            "Emergency Fund": 35,
            "Debt / FD": 20,
            "Index Equity": 25,
            "Flexi Equity": 10,
            "Gold": 10,
        }
    if profile == "Growth Investor":
        return {
            "Emergency Fund": 5,
            "Debt / FD": 15,
            "Index Equity": 35,
            "Flexi Equity": 30,
            "Gold": 10,
            "Skill / Upskilling": 5,
        }
    if profile == "Balanced Investor":
        return {
            "Emergency Fund": 10,
            "Debt / FD": 25,
            "Index Equity": 35,
            "Flexi Equity": 20,
            "Gold": 10,
        }
    if profile == "Capital Protector":
        return {
            "Emergency Fund": 15,
            "Debt / FD": 40,
            "Index Equity": 25,
            "Gold": 15,
            "Skill / Upskilling": 5,
        }
    return {
        "Emergency Fund": 45,
        "Debt / FD": 25,
        "Index Equity": 20,
        "Gold": 10,
    }


def blended_return(allocation: Dict[str, int]) -> float:
    assumptions = {
        "Emergency Fund": DEFAULTS["liquid_return"],
        "Debt / FD": DEFAULTS["debt_return"],
        "Index Equity": DEFAULTS["equity_return"],
        "Flexi Equity": DEFAULTS["equity_return"] + 1.0,
        "Gold": DEFAULTS["gold_return"],
        "Skill / Upskilling": 0.0,
    }
    return sum(weight * assumptions.get(asset, 0) / 100 for asset, weight in allocation.items())


def make_donut(labels: Iterable[str], values: Iterable[float], title: str) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=list(labels),
            values=list(values),
            hole=0.64,
            marker=dict(
                colors=["#2f9bff", "#21d4fd", "#a855f7", "#f43f8b", "#10b981", "#fbbf24"],
                line=dict(color="#07111f", width=2),
            ),
            textinfo="label+percent",
            textposition="outside",
            hovertemplate="%{label}: %{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color="#f8fafc"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c2d3", family="Inter"),
        height=380,
        margin=dict(t=58, b=32, l=24, r=24),
        showlegend=False,
    )
    return fig


def make_cashflow_chart(income: float, expenses: float, savings: float) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=["Income", "Expenses", "Savings"], y=[income, expenses, savings], marker_color=["#2f9bff", "#f43f8b", "#10b981"])
    fig.update_layout(
        title=dict(text="Monthly cashflow scan", font=dict(size=17, color="#f8fafc"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c2d3", family="Inter"),
        height=340,
        margin=dict(t=58, b=36, l=30, r=18),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.14)", tickprefix=RUPEE),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def make_projection_chart(current_savings: float, monthly: float, rate: float, years: int = 10) -> go.Figure:
    x = list(range(0, years + 1))
    invested = [current_savings + monthly * 12 * year for year in x]
    projected = [
        future_value_lump_sum(current_savings, rate, year) + future_value_monthly(monthly, rate, year)
        for year in x
    ]
    fig = go.Figure()
    fig.add_scatter(x=x, y=invested, mode="lines", name="Invested", line=dict(color="#7d8ba1", width=3, dash="dot"))
    fig.add_scatter(x=x, y=projected, mode="lines+markers", name="Projected", line=dict(color="#21d4fd", width=4))
    fig.update_layout(
        title=dict(text="10-year wealth path", font=dict(size=17, color="#f8fafc"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c2d3", family="Inter"),
        height=380,
        margin=dict(t=58, b=36, l=30, r=18),
        legend=dict(orientation="h", y=1.08, x=0),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.14)", tickprefix=RUPEE),
        xaxis=dict(title="Years", gridcolor="rgba(148, 163, 184, 0.08)"),
    )
    return fig


def make_goal_chart(target: float, current: float, monthly: float, rate: float, years: int) -> go.Figure:
    x = list(range(0, years * 12 + 1))
    values = []
    r = max(rate, 0) / (12 * 100)
    for month in x:
        if r == 0:
            value = current + monthly * month
        else:
            value = current * ((1 + r) ** month) + monthly * (((1 + r) ** month - 1) / r)
        values.append(value)
    fig = go.Figure()
    fig.add_scatter(x=x, y=values, mode="lines", name="Savings path", line=dict(color="#21d4fd", width=4))
    fig.add_scatter(x=x, y=[target for _ in x], mode="lines", name="Target", line=dict(color="#f43f8b", width=3, dash="dash"))
    fig.update_layout(
        title=dict(text="Asset goal timeline", font=dict(size=17, color="#f8fafc"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c2d3", family="Inter"),
        height=360,
        margin=dict(t=58, b=36, l=30, r=18),
        legend=dict(orientation="h", y=1.08, x=0),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.14)", tickprefix=RUPEE),
        xaxis=dict(title="Months", gridcolor="rgba(148, 163, 184, 0.08)"),
    )
    return fig


def make_radar(metrics: Dict[str, float]) -> go.Figure:
    labels = list(metrics.keys())
    values = [clamp(v) for v in metrics.values()]
    labels.append(labels[0])
    values.append(values[0])
    fig = go.Figure(
        go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            fillcolor="rgba(47, 155, 255, 0.20)",
            line=dict(color="#21d4fd", width=3),
            marker=dict(color="#fbbf24", size=7),
            hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor="rgba(148, 163, 184, 0.20)", tickfont=dict(color="#7d8ba1")),
            angularaxis=dict(gridcolor="rgba(148, 163, 184, 0.18)", tickfont=dict(color="#b8c2d3")),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c2d3", family="Inter"),
        height=380,
        margin=dict(t=26, b=26, l=32, r=32),
        showlegend=False,
    )
    return fig


def metric_card(label: str, value: str, note: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div>'
        "</div>"
    )


def plan_card(name: str, amount: float, percent: int, note: str) -> str:
    return (
        '<div class="plan-card">'
        f"<strong>{html.escape(name)}</strong>"
        f'<span>{html.escape(note)}</span>'
        f'<div class="plan-amount">{html.escape(format_inr(amount))}</div>'
        f'<span>{percent}% of monthly plan</span>'
        '<div class="progress-track">'
        f'<div class="progress-fill" style="width: {clamp(percent):.0f}%"></div>'
        "</div></div>"
    )


@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_data() -> Dict[str, Dict[str, float]]:
    data: Dict[str, Dict[str, float]] = {}
    for name, ticker in MARKET_TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
            close = hist["Close"].dropna()
            if len(close) >= 2:
                current = float(close.iloc[-1])
                previous = float(close.iloc[-2])
                change = ((current - previous) / previous) * 100 if previous else 0.0
                data[name] = {"price": current, "change": change}
            else:
                data[name] = {"price": 0.0, "change": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0}
    return data


# -----------------------------------------------------------------------------
# Onboarding
# -----------------------------------------------------------------------------


if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if not st.session_state.onboarded:
    html_block(
        """
        <div class="top-shell">
            <div class="hero-panel">
                <div class="kicker">AI-style finance cockpit</div>
                <div class="hero-title">FinWise India</div>
                <div class="hero-copy">
                    Enter your monthly money data once. The app turns it into a clean dashboard,
                    savings score, investment split, asset-buying timeline, and wealth projection.
                </div>
                <div class="status-row">
                    <div class="status-pill">Income scan</div>
                    <div class="status-pill">Expense map</div>
                    <div class="status-pill">Goal planner</div>
                    <div class="status-pill">Investment split</div>
                </div>
            </div>
            <div class="credit-card">
                <div class="card-brand">FinWise Card</div>
                <div class="card-number">2026  INDIA  PLAN</div>
                <div class="card-line">
                    <span>Dashboard</span>
                    <span>Ready</span>
                </div>
            </div>
        </div>
        """
    )

    with st.form("profile_form"):
        st.markdown("### Build your profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            income = st.number_input(f"Monthly income ({RUPEE})", min_value=0, value=80_000, step=5_000)
            savings = st.number_input(f"How much do you save monthly? ({RUPEE})", min_value=0, value=18_000, step=1_000)
        with c2:
            expenses = st.number_input(f"Monthly expenses ({RUPEE})", min_value=0, value=50_000, step=5_000)
            current_savings = st.number_input(f"Current savings/investments ({RUPEE})", min_value=0, value=150_000, step=10_000)
        with c3:
            age = st.number_input("Age", min_value=18, max_value=90, value=28, step=1)
            existing_emi = st.number_input(f"Existing EMI / loan payments ({RUPEE})", min_value=0, value=0, step=1_000)

        c4, c5, c6 = st.columns(3)
        with c4:
            risk = st.radio("Risk comfort", ["Low", "Medium", "High"], horizontal=True, index=1)
        with c5:
            priority = st.selectbox(
                "Top priority",
                ["Build emergency fund", "Grow wealth", "Buy an asset", "Save tax", "Retire early"],
            )
        with c6:
            dependents = st.number_input("Family members dependent on you", min_value=0, max_value=10, value=0, step=1)

        submitted = st.form_submit_button("Create my dashboard")
        if submitted:
            st.session_state.profile = {
                "income": income,
                "savings": savings,
                "expenses": expenses,
                "current_savings": current_savings,
                "age": age,
                "existing_emi": existing_emi,
                "dependents": dependents,
                "risk": risk,
                "priority": priority,
            }
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# -----------------------------------------------------------------------------
# Derived profile values
# -----------------------------------------------------------------------------


profile_data = st.session_state.profile
income = float(profile_data["income"])
reported_savings = float(profile_data["savings"])
expenses = float(profile_data["expenses"])
current_savings = float(profile_data["current_savings"])
age = int(profile_data["age"])
existing_emi = float(profile_data.get("existing_emi", 0))
dependents = int(profile_data["dependents"])
risk = str(profile_data["risk"])
priority = str(profile_data["priority"])

cashflow_surplus = max(income - expenses, 0)
investable = min(reported_savings, cashflow_surplus) if cashflow_surplus else reported_savings
investable = max(investable, 0)
savings_rate = (investable / income * 100) if income else 0
emergency_months = (current_savings / expenses) if expenses else 12
profile, readiness_score = profile_from_inputs(age, savings_rate / 100, emergency_months, risk)
allocation = allocation_for_profile(profile, emergency_months)
expected_return = blended_return(allocation)
ten_year_projection = future_value_lump_sum(current_savings, expected_return, 10) + future_value_monthly(
    investable, expected_return, 10
)
one_year_savings = investable * 12
total_obligation_ratio = ((existing_emi + expenses) / income * 100) if income else 0
emi_ratio = (existing_emi / income * 100) if income else 0


# -----------------------------------------------------------------------------
# Dashboard header
# -----------------------------------------------------------------------------


html_block(
    f"""
    <div class="top-shell">
        <div class="hero-panel">
            <div class="kicker">Personal finance dashboard</div>
            <div class="hero-title">FinWise India</div>
            <div class="hero-copy">
                Profile: <strong>{html.escape(profile)}</strong>. Priority: <strong>{html.escape(priority)}</strong>.
                Your dashboard updates when you change inputs inside each view.
            </div>
            <div class="status-row">
                <div class="status-pill">Readiness {readiness_score}/100</div>
                <div class="status-pill">Savings rate {savings_rate:.1f}%</div>
                <div class="status-pill">Emergency cover {emergency_months:.1f} months</div>
                <div class="status-pill">10Y projection {html.escape(format_inr(ten_year_projection, compact=True))}</div>
            </div>
        </div>
        <div class="credit-card">
            <div class="card-brand">FinWise Command Card</div>
            <div class="card-number">{readiness_score:03d}  {profile[:6].upper()}  INDIA</div>
            <div class="card-line">
                <span>{html.escape(risk)} Risk</span>
                <span>{html.escape(format_inr(investable))}/mo</span>
            </div>
        </div>
    </div>
    """
)

if st.button("Edit my answers"):
    st.session_state.onboarded = False
    st.rerun()


html_block(
    '<div class="metric-grid">'
    + metric_card("Monthly income", format_inr(income), "Your total cash inflow")
    + metric_card("Monthly expenses", format_inr(expenses), "Lifestyle and obligations")
    + metric_card("Investable amount", format_inr(investable), "Used for plan simulation")
    + metric_card("Existing EMI load", pct(emi_ratio), "Current debt pressure")
    + "</div>"
)


# -----------------------------------------------------------------------------
# Views
# -----------------------------------------------------------------------------


overview_tab, plan_tab, asset_tab, analytics_tab = st.tabs(
    ["Overview", "Investment Plan", "Asset Planner", "Analytics"]
)


with overview_tab:
    left, right = st.columns([1.08, 0.92], gap="large")
    with left:
        html_block('<div class="section-title">Cashflow intelligence</div><div class="section-subtitle">Income, spending, and investable surplus in one scan.</div>')
        st.plotly_chart(make_cashflow_chart(income, expenses, investable), width="stretch", config={"displayModeBar": False})

    with right:
        html_block('<div class="section-title">Profile radar</div><div class="section-subtitle">A quick health check from your answers.</div>')
        radar_metrics = {
            "Savings": clamp(savings_rate * 2.5),
            "Emergency": clamp((emergency_months / 6) * 100),
            "Risk Fit": {"Low": 55, "Medium": 78, "High": 92}[risk],
            "Dependents": clamp(100 - dependents * 12),
            "Age Edge": 95 if age < 35 else 78 if age < 50 else 58,
            "Surplus": clamp((cashflow_surplus / max(income, 1)) * 240),
        }
        st.plotly_chart(make_radar(radar_metrics), width="stretch", config={"displayModeBar": False})

    html_block('<div class="section-title">Live market strip</div>')
    market = fetch_market_data()
    market_cols = st.columns(len(market))
    for col, (name, values) in zip(market_cols, market.items()):
        with col:
            price = values["price"]
            label = "Unavailable" if price <= 0 else f"{price:,.2f}" if "USD" in name else f"{price:,.0f}"
            st.metric(name, label, f"{values['change']:+.2f}%")


with plan_tab:
    html_block('<div class="section-title">Your monthly investment split</div><div class="section-subtitle">Built from income, expenses, savings capacity, emergency cover, age, and risk comfort.</div>')
    notes = {
        "Emergency Fund": "Liquid savings before taking more risk.",
        "Debt / FD": "Stability bucket for near-term money.",
        "Index Equity": "Core long-term wealth engine.",
        "Flexi Equity": "Growth layer for longer horizons.",
        "Gold": "Diversifier for currency and inflation shocks.",
        "Skill / Upskilling": "Human-capital investment.",
    }
    cards = ['<div class="plan-grid">']
    for asset, weight in allocation.items():
        cards.append(plan_card(asset, investable * weight / 100, weight, notes.get(asset, "Monthly allocation bucket.")))
    cards.append("</div>")
    html_block("".join(cards))

    p1, p2 = st.columns([1, 1], gap="large")
    with p1:
        st.plotly_chart(make_donut(allocation.keys(), allocation.values(), "Suggested allocation"), width="stretch", config={"displayModeBar": False})
    with p2:
        st.plotly_chart(make_projection_chart(current_savings, investable, expected_return, 10), width="stretch", config={"displayModeBar": False})

    html_block('<div class="section-title">SIP compounding planner</div><div class="section-subtitle">See monthly SIP, yearly contribution, profit, and corpus across adjustable years.</div>')
    sip_c1, sip_c2, sip_c3 = st.columns([1, 1, 1])
    with sip_c1:
        sip_monthly = st.number_input(
            f"Monthly SIP to project ({RUPEE})",
            min_value=0,
            value=int(investable),
            step=1_000,
            key="sip_monthly_projection",
        )
    with sip_c2:
        sip_rate = st.slider(
            "Expected yearly growth",
            min_value=4.0,
            max_value=16.0,
            value=float(round(expected_return, 1)),
            step=0.5,
            key="sip_rate_projection",
        )
    with sip_c3:
        compounding_mode = st.radio(
            "Profit handling",
            ["Reinvest and compound", "Do not reinvest profit"],
            horizontal=False,
            key="compounding_mode",
        )

    selected_years = st.multiselect(
        "Projection columns",
        options=[1, 3, 5, 10, 15, 20],
        default=[1, 3, 5, 10],
        key="projection_years",
    )
    projection = projection_rows(
        current_savings=current_savings,
        monthly=sip_monthly,
        annual_rate=sip_rate,
        years=selected_years,
        reinvest=compounding_mode == "Reinvest and compound",
    )
    render_projection_table(projection)

    if projection:
        final_row = projection[-1]
        html_block(
            f"""
            <div class="insight-list">
                <div class="insight-item good-item"><strong>Compounding plan:</strong> If you continue {html.escape(format_inr(sip_monthly))} per month and choose "{html.escape(compounding_mode)}", the {html.escape(final_row["Year"])} projected corpus is {html.escape(final_row["Corpus"])}.</div>
                <div class="insight-item"><strong>Yearly discipline:</strong> Your yearly SIP engine is {html.escape(format_inr(sip_monthly * 12))}. Increasing it by 10% every year can materially improve the final corpus.</div>
            </div>
            """
        )

    html_block('<div class="section-title">Where this money can go</div><div class="section-subtitle">Risk-based research buckets. The app avoids one-stock tips and uses diversified choices for stability.</div>')
    render_instrument_cards(instrument_plan_for_risk(risk, profile))

    insight_html = ['<div class="section-title">Plan logic</div><div class="insight-list">']
    if emergency_months < 3:
        insight_html.append('<div class="insight-item"><strong>First move:</strong> Build emergency savings to at least 3 months before increasing risky investments.</div>')
    elif emergency_months < 6:
        insight_html.append('<div class="insight-item"><strong>Next move:</strong> Push emergency savings toward 6 months, then route more surplus into long-term assets.</div>')
    else:
        insight_html.append('<div class="insight-item"><strong>Base is strong:</strong> Emergency cover is healthy, so the plan can focus more on long-term compounding.</div>')
    if savings_rate < 15:
        insight_html.append('<div class="insight-item"><strong>Upgrade lever:</strong> Try increasing savings rate toward 20% by cutting one recurring expense or raising income.</div>')
    else:
        insight_html.append('<div class="insight-item"><strong>Good engine:</strong> Your savings rate can support structured investing if kept consistent.</div>')
    insight_html.append(f'<div class="insight-item"><strong>Profile:</strong> {html.escape(profile)} with an estimated blended return model of {expected_return:.1f}% per year.</div>')
    insight_html.append("</div>")
    html_block("".join(insight_html))


with asset_tab:
    html_block('<div class="section-title">Asset affordability engine</div><div class="section-subtitle">Type the asset you want. The app checks salary fit, EMI danger, saving timeline, and income required.</div>')

    ac1, ac2, ac3 = st.columns([1.1, 0.9, 1])
    with ac1:
        asset_name = st.text_input("What do you want to buy?", value="1 Cr house")
    with ac2:
        asset_type = st.selectbox("Rule category", ["Home", "Car", "Phone", "Gold", "Other"])
    with ac3:
        target_cost = st.number_input(f"Current market price ({RUPEE})", min_value=1_000, value=10_000_000, step=50_000)

    defaults = asset_rule_defaults(asset_type)
    ac4, ac5, ac6 = st.columns(3)
    with ac4:
        desired_years = st.slider("When do you want it?", 1, 15, 5)
    with ac5:
        asset_saved = st.number_input(f"Already saved for this asset ({RUPEE})", min_value=0, value=0, step=10_000)
    with ac6:
        price_growth = st.slider(
            "Expected yearly price growth",
            min_value=0.0,
            max_value=12.0,
            value=float(defaults["inflation"]),
            step=0.5,
        )

    projected_asset_cost = future_value_lump_sum(target_cost, price_growth, desired_years)
    goal_rate = DEFAULTS["debt_return"] if desired_years <= 5 else DEFAULTS["equity_return"]
    required_monthly = sip_needed(projected_asset_cost, asset_saved, goal_rate, desired_years)

    loan_c1, loan_c2, loan_c3 = st.columns(3)
    with loan_c1:
        down_payment_pct = st.slider(
            "Down payment planned",
            min_value=0,
            max_value=100,
            value=int(defaults["down_payment"]),
            step=5,
        )
    with loan_c2:
        loan_rate = st.slider(
            "Loan / planning rate",
            min_value=0.0,
            max_value=18.0,
            value=float(defaults["rate"]),
            step=0.25,
        )
    with loan_c3:
        loan_tenure = st.slider(
            "Loan tenure",
            min_value=1,
            max_value=30,
            value=int(defaults["tenure"]),
        )

    down_payment_amount = projected_asset_cost * down_payment_pct / 100
    loan_amount = max(projected_asset_cost - down_payment_amount, 0)
    projected_emi = calculate_emi(loan_amount, loan_rate, loan_tenure)
    safe_emi_pct = float(defaults["safe_emi_pct"])
    safe_new_emi = max(income * safe_emi_pct / 100 - existing_emi, 0)
    required_income = (projected_emi + existing_emi) / (safe_emi_pct / 100) if safe_emi_pct else 0
    income_gap = max(required_income - income, 0)
    max_safe_loan = loan_from_emi(safe_new_emi, loan_rate, loan_tenure)
    affordable_asset_cost = max_safe_loan + down_payment_amount
    total_emi_after_asset = existing_emi + projected_emi
    total_emi_after_ratio = (total_emi_after_asset / income * 100) if income else 999
    current_monthly_goal_capacity = max(investable * 0.55, 0)
    possible_months = months_to_goal(projected_asset_cost, asset_saved, current_monthly_goal_capacity, goal_rate)

    if projected_emi > safe_new_emi or income_gap > 0:
        verdict = "Not affordable right now"
        verdict_class = "danger-item"
    elif total_emi_after_ratio > 30:
        verdict = "High EMI pressure"
        verdict_class = "watch-item"
    else:
        verdict = "Looks manageable"
        verdict_class = "good-item"

    html_block(
        '<div class="metric-grid">'
        + metric_card("Future asset cost", format_inr(projected_asset_cost, compact=True), f"{price_growth:.1f}% yearly price growth")
        + metric_card("Required monthly saving", format_inr(required_monthly), f"To buy in {desired_years} year(s)")
        + metric_card("Estimated EMI", format_inr(projected_emi), f"{loan_tenure}Y loan at {loan_rate:.2f}%")
        + metric_card("Income needed", format_inr(required_income), f"Rule: EMI near {safe_emi_pct:.0f}% of income")
        + "</div>"
    )

    goal_left, goal_right = st.columns([1.18, 0.82], gap="large")
    with goal_left:
        st.plotly_chart(
            make_goal_chart(projected_asset_cost, asset_saved, current_monthly_goal_capacity, goal_rate, desired_years),
            width="stretch",
            config={"displayModeBar": False},
        )
    with goal_right:
        if possible_months is None:
            possible_text = "Your current goal saving is zero, so the asset will not be reached without increasing savings."
        else:
            possible_text = f"At {format_inr(current_monthly_goal_capacity)} per month, estimated time is {possible_months // 12} year(s) and {possible_months % 12} month(s)."

        if income_gap > 0:
            income_text = (
                f"Your monthly income may need to rise by about {format_inr(income_gap)} "
                f"to around {format_inr(required_income)} before this {asset_type.lower()} is safe."
            )
        else:
            income_text = "Your current income can support this EMI under the selected rule if other expenses stay controlled."

        html_block(
            f"""
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">{html.escape(asset_name)} verdict</div>
                    <div class="panel-tag">{html.escape(asset_type)}</div>
                </div>
                <div class="insight-list">
                    <div class="insight-item {verdict_class}"><strong>{html.escape(verdict)}:</strong> EMI after this asset becomes {html.escape(format_inr(total_emi_after_asset))}/month, or {total_emi_after_ratio:.1f}% of income.</div>
                    <div class="insight-item"><strong>Rule used:</strong> {html.escape(str(defaults["rule"]))}</div>
                    <div class="insight-item"><strong>Timeline:</strong> {html.escape(possible_text)}</div>
                    <div class="insight-item {'danger-item' if income_gap > 0 else 'good-item'}"><strong>Income target:</strong> {html.escape(income_text)}</div>
                </div>
            </div>
            """
        )

    red_flags = []
    if projected_emi > safe_new_emi:
        red_flags.append(
            f"The new EMI {format_inr(projected_emi)} is above your safe EMI room of {format_inr(safe_new_emi)}."
        )
    if total_emi_after_ratio > 40:
        red_flags.append("Total EMI would cross 40% of income. This can create future debt stress.")
    if required_monthly > investable:
        red_flags.append(
            f"Required monthly saving {format_inr(required_monthly)} is higher than your current investable amount {format_inr(investable)}."
        )
    if emergency_months < 6 and asset_type in {"Home", "Car"}:
        red_flags.append("Emergency cover is below 6 months. Big-ticket loans should wait until cash buffer improves.")

    if red_flags:
        flags_html = ['<div class="section-title">Red danger signals</div><div class="insight-list">']
        for flag in red_flags:
            flags_html.append(f'<div class="insight-item danger-item"><strong>Do not rush:</strong> {html.escape(flag)}</div>')
        flags_html.append("</div>")
        html_block("".join(flags_html))

    growth_salary = max(required_income, income * 1.25)
    html_block(
        f"""
        <div class="section-title">How to reach the asset safely</div>
        <div class="insight-list">
            <div class="insight-item"><strong>Step 1:</strong> Build or protect a medical + emergency fund of at least {html.escape(format_inr(expenses * 6))} before taking a large EMI.</div>
            <div class="insight-item"><strong>Step 2:</strong> If this goal is unrealistic now, target income of {html.escape(format_inr(growth_salary))}/month through upskilling, job switch, freelance income, or business income before buying.</div>
            <div class="insight-item"><strong>Step 3:</strong> Keep goal money in safer buckets for under 3 years; use equity-style compounding only for longer flexible timelines.</div>
            <div class="insight-item"><strong>Step 4:</strong> If the asset is a want, delay it until SIP and insurance are stable. If it is a need, reduce target price or increase down payment.</div>
        </div>
        """
    )


with analytics_tab:
    html_block('<div class="section-title">Statistical dashboard</div><div class="section-subtitle">A more analytical view for your project demo.</div>')

    a1, a2, a3, a4 = st.columns(4)
    expense_ratio = (expenses / income * 100) if income else 0
    networth_multiple = current_savings / max(expenses, 1)
    wealth_multiple = ten_year_projection / max(income * 12, 1)
    a1.metric("Expense ratio", pct(expense_ratio))
    a2.metric("Savings rate", pct(savings_rate))
    a3.metric("Emergency months", f"{emergency_months:.1f}")
    a4.metric("10Y wealth / annual income", f"{wealth_multiple:.1f}x")

    stat_left, stat_right = st.columns([1, 1], gap="large")
    with stat_left:
        st.plotly_chart(make_projection_chart(current_savings, investable, expected_return, 15), width="stretch", config={"displayModeBar": False})
    with stat_right:
        expense_map = {
            "Needs": min(expenses * 0.60, expenses),
            "Lifestyle": expenses * 0.25,
            "Buffer leakage": max(expenses * 0.15, 0),
        }
        st.plotly_chart(make_donut(expense_map.keys(), expense_map.values(), "Expense pressure map"), width="stretch", config={"displayModeBar": False})

    html_block(
        f"""
        <div class="panel">
            <div class="panel-head">
                <div class="panel-title">Dashboard summary</div>
                <div class="panel-tag">{readiness_score}/100</div>
            </div>
            <div class="insight-list">
                <div class="insight-item"><strong>Annual saving engine:</strong> {html.escape(format_inr(one_year_savings))} at the current monthly plan.</div>
                <div class="insight-item"><strong>Emergency strength:</strong> {emergency_months:.1f} months of expenses covered.</div>
                <div class="insight-item"><strong>Projected 10-year value:</strong> {html.escape(format_inr(ten_year_projection, compact=True))} using the current allocation model.</div>
                <div class="insight-item"><strong>Best improvement lever:</strong> {"reduce recurring expenses" if expense_ratio > 65 else "increase monthly investing consistency"}.</div>
            </div>
        </div>
        """
    )

    html_block('<div class="section-title">Bad areas to improve</div><div class="section-subtitle">Anything risky is marked in red so the user knows what to fix first.</div>')
    medical_buffer_target = max(expenses * 6, 200_000 if dependents else 100_000)
    medical_gap = max(medical_buffer_target - current_savings, 0)
    diagnostics = []
    diagnostics.append(
        (
            "danger-item" if savings_rate < 15 else "good-item",
            "Savings rate",
            f"{savings_rate:.1f}% savings rate. Aim for 20%+ first, then 30%+ for faster asset goals.",
        )
    )
    diagnostics.append(
        (
            "danger-item" if emergency_months < 3 else "watch-item" if emergency_months < 6 else "good-item",
            "Emergency fund",
            f"You have {emergency_months:.1f} months of cover. Target at least 6 months before large loans.",
        )
    )
    diagnostics.append(
        (
            "danger-item" if emi_ratio > 30 else "watch-item" if emi_ratio > 15 else "good-item",
            "Existing EMI load",
            f"Existing EMI is {emi_ratio:.1f}% of salary. Keep total EMI controlled before adding car/home EMI.",
        )
    )
    diagnostics.append(
        (
            "danger-item" if expense_ratio > 75 else "watch-item" if expense_ratio > 60 else "good-item",
            "Expense pressure",
            f"Expenses consume {expense_ratio:.1f}% of income. Lower this to create future stability.",
        )
    )
    diagnostics.append(
        (
            "danger-item" if medical_gap > 0 else "good-item",
            "Medical emergency fund",
            f"Target medical/emergency buffer is {format_inr(medical_buffer_target)}. Gap is {format_inr(medical_gap)}.",
        )
    )
    diagnostics.append(
        (
            "danger-item" if "projected_emi" in locals() and total_emi_after_ratio > 40 else "watch-item" if "projected_emi" in locals() and total_emi_after_ratio > 30 else "good-item",
            "Future EMI protection",
            f"After selected asset, EMI pressure is {total_emi_after_ratio:.1f}% of income. Avoid crossing 30-40%.",
        )
    )

    diag_html = ['<div class="insight-list">']
    for css_class, title, text in diagnostics:
        diag_html.append(f'<div class="insight-item {css_class}"><strong>{html.escape(title)}:</strong> {html.escape(text)}</div>')
    diag_html.append("</div>")
    html_block("".join(diag_html))

    html_block(
        f"""
        <div class="section-title">Stability plan</div>
        <div class="insight-list">
            <div class="insight-item"><strong>Protect first:</strong> Keep {html.escape(format_inr(medical_buffer_target))} as medical/emergency money before upgrading lifestyle assets.</div>
            <div class="insight-item"><strong>Debt rule:</strong> If total EMI crosses 30%, slow down. If it crosses 40%, treat it as danger and reduce the asset price or increase income.</div>
            <div class="insight-item"><strong>Growth path:</strong> Increase income through job switch preparation, certification, freelancing, portfolio projects, or business side income before buying a high-value home/car.</div>
            <div class="insight-item"><strong>Compounding path:</strong> Keep SIPs running even when buying assets; stopping SIP for EMI is how future wealth gets delayed.</div>
        </div>
        """
    )
