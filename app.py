from __future__ import annotations

import html
import math
import os
from dataclasses import dataclass
from typing import Dict, Iterable
from urllib.parse import urlparse

import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------

APP_NAME = "FinWise India"
RUPEE = "₹"
LTCG_EXEMPTION = 125_000
DEFAULT_LTCG_RATE = 12.5
DEFAULT_CAR_LOAN_RATE = 8.75
DEFAULT_EQUITY_RETURN = 11.0
DEFAULT_FD_RATE = 6.75
DEFAULT_DEBT_RETURN = 7.0

MARKET_TICKERS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "S&P 500": "^GSPC",
    "GOLD": "GC=F",
    "USD/INR": "INR=X",
}

SOURCE_LINKS = {
    "SEBI investor caution":
    "https://investor.sebi.gov.in/cautiontoinvestor.html",
    "SEBI registered adviser caution":
    "https://www.sebi.gov.in/media/press-releases/jun-2016/sebi-cautions-public-to-deal-with-only-sebi-registered-investment-advisers-and-research-analysts_32627.html",
    "Income-tax Section 112A":
    "https://www.incometaxindia.gov.in/w/section-112a-59",
    "Budget 2024 capital gains update":
    "https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2035596",
}

st.set_page_config(
    page_title=APP_NAME,
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

st.markdown(
    """
<style>
:root {
    --bg: #050505;
    --panel: #0F172A;
    --panel-soft: #111827;
    --border: #253045;
    --text: #F8FAFC;
    --muted: #CBD5E1;
    --subtle: #94A3B8;
    --gold: #D4AF37;
    --gold-strong: #F8D56B;
    --blue: #38BDF8;
    --green: #22C55E;
    --red: #F87171;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.08), transparent 28rem),
        linear-gradient(180deg, #050505 0%, #080B11 48%, #050505 100%);
}

main .block-container {
    padding-top: 2.4rem;
    padding-bottom: 3.2rem;
    max-width: 1220px;
}

h1, h2, h3 {
    color: var(--text);
    letter-spacing: 0;
}

.hero {
    border-bottom: 1px solid rgba(212, 175, 55, 0.24);
    padding-bottom: 1.1rem;
    margin-bottom: 1.15rem;
}

.hero-kicker {
    color: var(--gold-strong);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.13rem;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.hero-title {
    color: var(--text);
    font-size: clamp(2.2rem, 4.6vw, 4.8rem);
    font-weight: 800;
    line-height: 1.02;
    margin: 0;
}

.hero-subtitle {
    color: var(--muted);
    font-size: clamp(1rem, 1.6vw, 1.25rem);
    line-height: 1.55;
    max-width: 760px;
    margin-top: 0.85rem;
}

.disclaimer-strip {
    background: rgba(212, 175, 55, 0.10);
    border: 1px solid rgba(212, 175, 55, 0.34);
    border-radius: 8px;
    color: #F8E6A0;
    padding: 0.9rem 1rem;
    line-height: 1.45;
    margin: 0.6rem 0 1.25rem;
}

.section-title {
    color: var(--gold-strong);
    font-size: 0.78rem;
    letter-spacing: 0.12rem;
    text-transform: uppercase;
    font-weight: 800;
    margin: 1.4rem 0 0.75rem;
}

.insight-box {
    background: rgba(15, 23, 42, 0.86);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    color: var(--muted);
    line-height: 1.55;
}

.small-note {
    color: var(--subtle);
    font-size: 0.86rem;
    line-height: 1.5;
}

.source-links a {
    color: var(--blue);
    text-decoration: none;
}

.source-links a:hover,
.source-links a:focus-visible {
    text-decoration: underline;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(17, 24, 39, 0.96), rgba(3, 7, 18, 0.98));
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
}

div[data-testid="metric-container"] > label {
    color: var(--subtle) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06rem;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 800;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    color: var(--muted);
    font-weight: 700;
    padding: 0.95rem 0.8rem;
}

.stTabs [aria-selected="true"] {
    color: var(--gold-strong) !important;
    background: rgba(212, 175, 55, 0.08);
    border-bottom-color: var(--gold-strong) !important;
}

.broker-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.broker-card {
    min-height: 244px;
    background: linear-gradient(145deg, rgba(17, 24, 39, 0.96), rgba(3, 7, 18, 0.98));
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.broker-name {
    color: var(--text);
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: 0.05rem;
    text-transform: uppercase;
}

.broker-desc {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.5;
    margin: 0.7rem 0 1rem;
}

.broker-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    width: 100%;
    background: #D4AF37;
    border-radius: 8px;
    color: #050505 !important;
    font-weight: 800;
    text-decoration: none !important;
}

.broker-btn:hover,
.broker-btn:focus-visible {
    background: #F8D56B;
    outline: 3px solid rgba(248, 213, 107, 0.28);
    outline-offset: 2px;
}

.footer {
    border-top: 1px solid var(--border);
    color: var(--subtle);
    font-size: 0.86rem;
    line-height: 1.55;
    margin-top: 2rem;
    padding-top: 1rem;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 44px;
    border-radius: 8px;
}

a:focus-visible,
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="tab"]:focus-visible {
    outline: 3px solid rgba(56, 189, 248, 0.45) !important;
    outline-offset: 2px !important;
}

@media (max-width: 840px) {
    main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .broker-grid {
        grid-template-columns: 1fr;
    }

    .hero {
        padding-bottom: 0.85rem;
    }

    .hero-subtitle {
        max-width: 100%;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data models and helpers
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Broker:
    name: str
    env_key: str
    default_url: str
    description: str


BROKERS = (
    Broker(
        name="Zerodha",
        env_key="ZERODHA_URL",
        default_url="https://zerodha.com/open-account",
        description="Execution-first broker for direct equity and Coin mutual fund access.",
    ),
    Broker(
        name="Groww",
        env_key="GROWW_URL",
        default_url="https://groww.in/",
        description="Beginner-friendly investing app with a simple SIP onboarding flow.",
    ),
    Broker(
        name="Upstox",
        env_key="UPSTOX_URL",
        default_url="https://upstox.com/open-demat-account/",
        description="Trading and investing platform with charting tools and app-led account opening.",
    ),
)


def get_secret_or_env(key: str, default: str) -> str:
    """Read Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(key)
    except Exception:
        value = None
    return str(value or os.getenv(key, default)).strip()


def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def safe_external_url(url: str, fallback: str) -> str:
    return url if is_safe_url(url) else fallback


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
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ",".join(groups + [last_three])

    return f"{sign}{RUPEE}{formatted}"


def format_market_price(name: str, value: float) -> str:
    if value <= 0 or not math.isfinite(float(value)):
        return "Unavailable"
    if "USD" in name:
        return f"{value:.2f}"
    if "GOLD" in name:
        return f"{value:,.0f}"
    return f"{value:,.0f}"


def pct(value: float) -> str:
    if not math.isfinite(float(value)):
        return "0.00%"
    return f"{value:.2f}%"


def safe_months(years: float) -> int:
    return max(int(round(years * 12)), 1)


def calculate_emi(principal: float, rate_annual: float, years: float) -> float:
    n = safe_months(years)
    r = max(rate_annual, 0) / (12 * 100)
    if principal <= 0:
        return 0.0
    if r == 0:
        return principal / n
    return principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)


def future_value_monthly(monthly_investment: float, rate_annual: float, years: float) -> float:
    n = safe_months(years)
    r = max(rate_annual, 0) / (12 * 100)
    if monthly_investment <= 0:
        return 0.0
    if r == 0:
        return monthly_investment * n
    return monthly_investment * (((1 + r) ** n - 1) / r)


def calculate_sip_needed(target: float, rate_annual: float, years: float) -> float:
    n = safe_months(years)
    r = max(rate_annual, 0) / (12 * 100)
    if target <= 0:
        return 0.0
    if r == 0:
        return target / n
    factor = ((1 + r) ** n - 1) / r
    return target / factor


def calculate_ltcg_tax(
    final_value: float,
    invested_amount: float,
    annual_exemption_remaining: float,
    tax_rate: float,
) -> tuple[float, float]:
    gain = max(final_value - invested_amount, 0)
    taxable_gain = max(gain - max(annual_exemption_remaining, 0), 0)
    tax = taxable_gain * max(tax_rate, 0) / 100
    return taxable_gain, tax


def get_risk_profile(age: int, horizon: int, crash_behavior: str, stability_need: str) -> str:
    score = 0

    if age < 30:
        score += 3
    elif age < 45:
        score += 2
    else:
        score += 1

    if horizon >= 10:
        score += 3
    elif horizon >= 5:
        score += 2
    else:
        score += 1

    if "Invest more" in crash_behavior:
        score += 3
    elif "Stay invested" in crash_behavior:
        score += 2

    if "Very high" in stability_need:
        score -= 2
    elif "Moderate" in stability_need:
        score -= 1

    if score >= 8:
        return "Aggressive"
    if score >= 5:
        return "Balanced"
    return "Conservative"


def get_allocations(profile: str) -> Dict[str, int]:
    allocations = {
        "Conservative": {
            "Emergency / Liquid Fund": 20,
            "Fixed Deposits": 25,
            "Debt Funds": 25,
            "Large-cap Equity": 20,
            "Gold ETF / SGB": 10,
        },
        "Balanced": {
            "Emergency / Liquid Fund": 10,
            "Debt Funds": 20,
            "Large-cap Equity": 35,
            "Flexi / Mid-cap Equity": 25,
            "Gold ETF / SGB": 10,
        },
        "Aggressive": {
            "Emergency / Liquid Fund": 5,
            "Debt Funds": 10,
            "Large-cap Equity": 30,
            "Flexi / Mid-cap Equity": 35,
            "Small-cap Equity": 15,
            "Gold ETF / SGB": 5,
        },
    }
    return allocations[profile]


def weighted_return(allocations: Dict[str, int], assumptions: Dict[str, float]) -> float:
    total = 0.0
    for asset, weight in allocations.items():
        total += weight * assumptions.get(asset, DEFAULT_EQUITY_RETURN) / 100
    return total


def make_pie_chart(labels: Iterable[str], values: Iterable[float], title: str) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=list(labels),
            values=list(values),
            hole=0.62,
            marker=dict(
                colors=["#D4AF37", "#38BDF8", "#2563EB", "#22C55E", "#F59E0B", "#A78BFA"],
                line=dict(color="#050505", width=2),
            ),
            textinfo="label+percent",
            textposition="outside",
            hovertemplate="%{label}<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=16, color="#F8FAFC")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter"),
        height=390,
        margin=dict(t=58, b=34, l=24, r=24),
        showlegend=False,
    )
    return fig


def make_stacked_bar(title: str, bars: Dict[str, float], colors: Dict[str, str]) -> go.Figure:
    fig = go.Figure()
    for label, value in bars.items():
        fig.add_bar(name=label, x=[title], y=[value], marker_color=colors.get(label, "#94A3B8"))

    fig.update_layout(
        barmode="stack",
        title=dict(text=title, x=0.02, font=dict(size=16, color="#F8FAFC")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter"),
        height=320,
        margin=dict(t=58, b=40, l=28, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.16)", tickprefix=RUPEE),
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_data() -> Dict[str, Dict[str, float]]:
    data: Dict[str, Dict[str, float]] = {}
    for name, ticker in MARKET_TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
            close = hist["Close"].dropna()
            if len(close) >= 2:
                curr = float(close.iloc[-1])
                prev = float(close.iloc[-2])
                change = ((curr - prev) / prev) * 100 if prev else 0.0
                data[name] = {"price": curr, "change": change}
            else:
                data[name] = {"price": 0.0, "change": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0}
    return data


def render_source_links() -> None:
    links = " &nbsp; ".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>'
        for label, url in SOURCE_LINKS.items()
    )
    st.markdown(f'<p class="small-note source-links">{links}</p>', unsafe_allow_html=True)


def render_broker_cards(brokers: Iterable[Broker], urls: Dict[str, str]) -> None:
    cards = ['<div class="broker-grid">']
    for broker in brokers:
        url = html.escape(urls[broker.env_key], quote=True)
        label = html.escape(f"Open {broker.name} account", quote=True)
        cards.append(
            f"""
            <div class="broker-card">
                <div>
                    <div class="broker-name">{html.escape(broker.name)}</div>
                    <div class="broker-desc">{html.escape(broker.description)}</div>
                </div>
                <a class="broker-btn" href="{url}" target="_blank" rel="noopener noreferrer sponsored" aria-label="{label}">
                    Open account
                </a>
            </div>
            """
        )
    cards.append("</div>")
    st.markdown("\n".join(cards), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar controls
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("Assumptions")
    st.caption("Use realistic values for your own scenario. These are planning assumptions, not assured returns.")

    car_loan_rate = st.number_input(
        "Car loan interest rate",
        min_value=0.0,
        max_value=20.0,
        value=DEFAULT_CAR_LOAN_RATE,
        step=0.05,
        format="%.2f",
        help="Recent Indian bank auto-loan rates vary by lender, credit profile, vehicle, and tenure.",
    )
    equity_return = st.number_input(
        "Expected equity SIP return",
        min_value=0.0,
        max_value=25.0,
        value=DEFAULT_EQUITY_RETURN,
        step=0.25,
        format="%.2f",
        help="Use a conservative long-term assumption. Past returns do not assure future returns.",
    )
    debt_return = st.number_input(
        "Debt fund / fixed-income return",
        min_value=0.0,
        max_value=15.0,
        value=DEFAULT_DEBT_RETURN,
        step=0.25,
        format="%.2f",
    )
    fd_rate = st.number_input(
        "Fixed deposit return",
        min_value=0.0,
        max_value=12.0,
        value=DEFAULT_FD_RATE,
        step=0.25,
        format="%.2f",
    )

    st.divider()
    st.header("Tax inputs")
    ltcg_rate = st.number_input(
        "Equity LTCG tax rate",
        min_value=0.0,
        max_value=30.0,
        value=DEFAULT_LTCG_RATE,
        step=0.25,
        format="%.2f",
        help="Simplified Section 112A rate for eligible listed equity / equity-oriented funds on or after 23 July 2024.",
    )
    exemption_used = st.number_input(
        "LTCG exemption already used this FY",
        min_value=0,
        max_value=LTCG_EXEMPTION,
        value=0,
        step=5_000,
        help="The ₹1.25L exemption is annual and shared across eligible gains.",
    )
    exemption_remaining = max(LTCG_EXEMPTION - exemption_used, 0)

    st.divider()
    st.header("Referral links")
    st.caption("For deployment, set these as Streamlit secrets or environment variables.")
    configured_urls: Dict[str, str] = {}
    for broker in BROKERS:
        value = st.text_input(
            f"{broker.name} URL",
            value=get_secret_or_env(broker.env_key, broker.default_url),
            key=broker.env_key,
        )
        configured_urls[broker.env_key] = safe_external_url(value, broker.default_url)


# -----------------------------------------------------------------------------
# Header and market snapshot
# -----------------------------------------------------------------------------

st.markdown(
    """
<header class="hero">
    <div class="hero-kicker">India-focused personal finance planner</div>
    <h1 class="hero-title">FinWise India</h1>
    <div class="hero-subtitle">
        A Streamlit project for educational portfolio planning, EMI-vs-SIP comparisons,
        Indian tax-aware projections, and transparent execution links.
    </div>
</header>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="disclaimer-strip" role="note">
    <strong>Important:</strong> This tool provides general financial education only. It is not personalized
    investment advice, research advice, tax advice, or a SEBI-registered advisory service.
    Securities market investments are subject to market risks. Read all related documents carefully before investing.
</div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading market snapshot..."):
    market = fetch_market_data()

market_cols = st.columns(3)
for index, (name, val) in enumerate(market.items()):
    with market_cols[index % 3]:
        st.metric(name, format_market_price(name, val["price"]), f"{val['change']:+.2f}%")

st.caption("Market data is fetched from Yahoo Finance and may be delayed or unavailable during exchange holidays.")


# -----------------------------------------------------------------------------
# Main navigation
# -----------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Portfolio planner",
        "EMI vs SIP",
        "Tax & 80C",
        "Action hub",
    ]
)


# -----------------------------------------------------------------------------
# Tab 1: Portfolio planner
# -----------------------------------------------------------------------------

with tab1:
    left, right = st.columns([1, 1.55], gap="large")

    with left:
        st.markdown('<p class="section-title">Investor profile</p>', unsafe_allow_html=True)
        age = st.number_input("Age", min_value=18, max_value=90, value=30, step=1)
        monthly_income = st.number_input(
            f"Monthly household income ({RUPEE})",
            min_value=0,
            value=100_000,
            step=5_000,
        )
        existing_emergency_months = st.slider(
            "Emergency fund already saved",
            min_value=0,
            max_value=24,
            value=3,
            help="Number of months of expenses available in liquid savings.",
        )
        investment_horizon = st.slider("Primary investment horizon", 1, 30, 10)
        crash_behavior = st.radio(
            "If equity markets fell 20% in a month, you would most likely:",
            [
                "Exit risky investments",
                "Stay invested and review calmly",
                "Invest more if the goal is long term",
            ],
        )
        stability_need = st.radio(
            "Need for stable capital in the next 3 years",
            ["Low", "Moderate", "Very high"],
            horizontal=True,
        )

        investable_amount = monthly_income * 0.20
        emergency_gap = max(6 - existing_emergency_months, 0)
        st.info(
            f"Rule-of-thumb investable surplus: {format_inr(investable_amount)} per month. "
            f"Emergency buffer gap: {emergency_gap} month(s) toward a 6-month base."
        )

    with right:
        profile = get_risk_profile(age, investment_horizon, crash_behavior, stability_need)
        allocations = get_allocations(profile)
        asset_return_assumptions = {
            "Emergency / Liquid Fund": 5.5,
            "Fixed Deposits": fd_rate,
            "Debt Funds": debt_return,
            "Large-cap Equity": equity_return,
            "Flexi / Mid-cap Equity": min(equity_return + 1.0, 25.0),
            "Small-cap Equity": min(equity_return + 2.0, 25.0),
            "Gold ETF / SGB": 7.0,
        }
        blended_return = weighted_return(allocations, asset_return_assumptions)

        st.markdown(
            f'<p class="section-title">Educational allocation: {profile}</p>',
            unsafe_allow_html=True,
        )
        allocation_chart = make_pie_chart(
            allocations.keys(),
            allocations.values(),
            "Sample asset allocation by risk profile",
        )
        st.plotly_chart(
            allocation_chart,
            width="stretch",
            config={"displayModeBar": False},
        )
        st.caption(
            "Chart description: allocation split across emergency funds, deposits, debt, equity, and gold. "
            "This is an educational model, not a recommendation."
        )

        met1, met2, met3 = st.columns(3)
        met1.metric("Risk profile", profile)
        met2.metric("Blended return assumption", pct(blended_return))
        met3.metric("Monthly surplus model", format_inr(investable_amount, compact=True))

        st.markdown(
            """
<div class="insight-box">
    Start with emergency money and insurance before scaling market exposure. For equity allocations,
    match the horizon to the fund category and avoid relying on assured-return language.
</div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Tab 2: EMI vs SIP
# -----------------------------------------------------------------------------

with tab2:
    st.markdown('<p class="section-title">Purchase planning</p>', unsafe_allow_html=True)
    st.write(
        "Compare the cash-flow cost of borrowing for a depreciating purchase with the discipline of investing first."
    )

    gc1, gc2, gc3 = st.columns(3, gap="medium")
    with gc1:
        goal_amount = st.number_input(
            f"Purchase cost ({RUPEE})",
            min_value=10_000,
            value=2_000_000,
            step=25_000,
        )
    with gc2:
        timeframe = st.slider("Planning period in years", 1, 10, 5)
    with gc3:
        asset_depreciation = st.slider(
            "Expected asset value drop by end",
            min_value=0,
            max_value=95,
            value=60,
            help="Many cars depreciate meaningfully over five years; adjust for your model and usage.",
        )

    emi = calculate_emi(goal_amount, car_loan_rate, timeframe)
    total_loan_paid = emi * safe_months(timeframe)
    interest_paid = max(total_loan_paid - goal_amount, 0)
    resale_value = goal_amount * (1 - (asset_depreciation / 100))

    sip = calculate_sip_needed(goal_amount, equity_return, timeframe)
    total_invested = sip * safe_months(timeframe)
    pre_tax_gain = max(goal_amount - total_invested, 0)
    taxable_gain, ltcg_tax = calculate_ltcg_tax(
        final_value=goal_amount,
        invested_amount=total_invested,
        annual_exemption_remaining=exemption_remaining,
        tax_rate=ltcg_rate,
    )
    after_tax_goal_corpus = goal_amount - ltcg_tax
    tax_adjusted_gap = max(goal_amount - after_tax_goal_corpus, 0)

    cc1, cc2 = st.columns(2, gap="large")

    with cc1:
        st.subheader("Borrow now")
        st.metric(f"Monthly EMI at {car_loan_rate:.2f}%", format_inr(emi))
        loan_chart = make_stacked_bar(
            "Loan cash outflow",
            {"Principal": goal_amount, "Interest": interest_paid},
            {"Principal": "#475569", "Interest": "#F87171"},
        )
        st.plotly_chart(loan_chart, width="stretch", config={"displayModeBar": False})
        st.caption("Chart description: total loan repayment split into principal and interest.")
        st.error(
            f"Total paid to lender: {format_inr(total_loan_paid)}. "
            f"Estimated resale value after depreciation: {format_inr(resale_value)}."
        )
        st.caption("Car-loan interest is generally not tax-deductible for personal-use vehicles.")

    with cc2:
        st.subheader("Invest first")
        st.metric(f"Monthly SIP at {equity_return:.2f}%", format_inr(sip))
        sip_chart = make_stacked_bar(
            "Target corpus",
            {"Your investment": total_invested, "Market gain": pre_tax_gain},
            {"Your investment": "#475569", "Market gain": "#22C55E"},
        )
        st.plotly_chart(sip_chart, width="stretch", config={"displayModeBar": False})
        st.caption("Chart description: target corpus split into invested amount and estimated market gain.")
        st.success(
            f"Estimated investment required: {format_inr(total_invested)}. "
            f"Simplified LTCG tax on withdrawal: {format_inr(ltcg_tax)}."
        )
        if tax_adjusted_gap > 0:
            st.warning(
                f"To net the full purchase amount after tax, plan an extra buffer of about "
                f"{format_inr(tax_adjusted_gap)}."
            )


# -----------------------------------------------------------------------------
# Tab 3: Tax and 80C
# -----------------------------------------------------------------------------

with tab3:
    st.markdown('<p class="section-title">India tax-aware planning</p>', unsafe_allow_html=True)

    tx1, tx2 = st.columns([1, 1.3], gap="large")
    with tx1:
        sip_monthly = st.number_input(
            f"Monthly SIP for tax estimate ({RUPEE})",
            min_value=0,
            value=25_000,
            step=1_000,
        )
        tax_years = st.slider("Holding period for estimate", 1, 30, 10, key="tax_years")
        estimated_corpus = future_value_monthly(sip_monthly, equity_return, tax_years)
        estimated_invested = sip_monthly * safe_months(tax_years)
        taxable_gain_est, estimated_ltcg_tax = calculate_ltcg_tax(
            estimated_corpus,
            estimated_invested,
            exemption_remaining,
            ltcg_rate,
        )
        after_tax_corpus = estimated_corpus - estimated_ltcg_tax

        t1, t2 = st.columns(2)
        t1.metric("Estimated corpus", format_inr(estimated_corpus, compact=True))
        t2.metric("After simplified LTCG", format_inr(after_tax_corpus, compact=True))
        st.caption(
            "Simplified model assumes eligible equity-oriented funds, one final redemption, and the current "
            "Section 112A exemption/rate inputs shown in the sidebar."
        )

    with tx2:
        st.subheader("Section 80C / ELSS helper")
        old_regime = st.toggle(
            "I am evaluating the old tax regime",
            value=True,
            help="Most 80C deductions are not available under the new tax regime.",
        )
        existing_80c = st.number_input(
            f"Existing 80C usage this year ({RUPEE})",
            min_value=0,
            max_value=150_000,
            value=50_000,
            step=5_000,
        )
        planned_elss = st.number_input(
            f"Planned ELSS investment ({RUPEE})",
            min_value=0,
            value=100_000,
            step=5_000,
            help="ELSS has a 3-year lock-in. Confirm suitability before investing.",
        )
        marginal_rate = st.selectbox(
            "Approximate marginal tax rate",
            options=[0, 5, 10, 15, 20, 30],
            index=5,
        )
        available_80c = max(150_000 - existing_80c, 0)
        eligible_elss = min(planned_elss, available_80c)
        estimated_tax_saving = eligible_elss * marginal_rate / 100 if old_regime else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("80C room", format_inr(available_80c))
        c2.metric("ELSS counted", format_inr(eligible_elss))
        c3.metric("Estimated tax saving", format_inr(estimated_tax_saving))
        st.info(
            "ELSS can be considered for Section 80C only when it suits the investor's goal, risk profile, "
            "tax regime, and lock-in comfort."
        )

    st.markdown('<p class="section-title">Regulatory notes</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="insight-box">
    SEBI cautions investors to deal with registered investment advisers for investment advice and to be wary
    of unrealistic return promises. This app avoids stock tips, assured returns, and personalized recommendations.
    The tax model is simplified and should be checked with a qualified tax professional before filing or transacting.
</div>
        """,
        unsafe_allow_html=True,
    )
    render_source_links()


# -----------------------------------------------------------------------------
# Tab 4: Action hub
# -----------------------------------------------------------------------------

with tab4:
    st.markdown('<p class="section-title">Execution links</p>', unsafe_allow_html=True)
    st.write(
        "These links are configurable so the project can be deployed without editing the app code."
    )
    render_broker_cards(BROKERS, configured_urls)

    st.info(
        "Disclosure: Some links may be referral or affiliate links. The app owner may earn a commission if a user "
        "opens an account through them. Compare costs, features, and regulatory status before choosing a platform."
    )

    st.markdown('<p class="section-title">Configuration names</p>', unsafe_allow_html=True)
    st.code(
        "ZERODHA_URL = \"https://your-link\"\n"
        "GROWW_URL = \"https://your-link\"\n"
        "UPSTOX_URL = \"https://your-link\"",
        language="toml",
    )


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.markdown(
    """
<footer class="footer">
    <strong>Risk disclosure:</strong> Mutual fund and securities market investments are subject to market risks.
    Read all scheme and related documents carefully before investing. Registration granted by SEBI, membership of
    BASL, or NISM certification, wherever applicable to an intermediary, does not guarantee performance or assure
    returns. This project is for learning and portfolio demonstration only.
</footer>
    """,
    unsafe_allow_html=True,
)
