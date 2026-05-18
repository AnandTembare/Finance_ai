import streamlit as st
import yfinance as yf
import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinWise Analytics | GCC Edition",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0f1e; color: #e8eaf6; }
.main { background-color: #0a0f1e; }
h1, h2, h3 { font-family: 'Space Mono', monospace; color: #00e5ff; }
.stMetric { background: linear-gradient(135deg, #0d1b2a, #1a2744); border: 1px solid #00e5ff33; border-radius: 12px; padding: 16px; }
.stMetric label { color: #90caf9 !important; font-size: 13px !important; }
.stMetric [data-testid="metric-container"] > div { color: #00e5ff !important; }
.invest-card { background: linear-gradient(135deg, #0d1b2a, #1a2744); border: 1px solid #00e5ff33; border-radius: 14px; padding: 20px; margin: 8px 0; text-align: center; }
.invest-amount { font-family: 'Space Mono', monospace; font-size: 28px; font-weight: 700; color: #00e5ff; }
.invest-label { font-size: 13px; color: #90caf9; margin-top: 4px; }
.stButton > button { background: linear-gradient(135deg, #00e5ff, #0091ea); color: #0a0f1e; font-family: 'Space Mono', monospace; font-weight: 700; border: none; border-radius: 8px; padding: 12px 28px; font-size: 15px; width: 100%; transition: all 0.3s ease; }
.stButton > button:hover { background: linear-gradient(135deg, #ff6b35, #ff3d00); transform: translateY(-2px); box-shadow: 0 8px 25px #ff6b3540; }
.section-title { font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 3px; color: #00e5ff; text-transform: uppercase; margin-bottom: 4px; }
.hero-title { font-family: 'Space Mono', monospace; font-size: 42px; font-weight: 700; background: linear-gradient(135deg, #00e5ff, #00b0ff, #ff6b35); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Core Business Logic ───────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_market_data() -> Dict[str, Dict[str, float]]:
    """Fetches live market indices, including GCC specific trackers."""
    tickers = {
        "TADAWUL (KSA)": "^TASI.SR", 
        "NIFTY 50": "^NSEI", 
        "S&P 500": "^GSPC", 
        "GOLD": "GC=F", 
        "USD/AED": "AED=X",
        "USD/INR": "INR=X"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                data[name] = {"price": curr, "change": ((curr - prev) / prev) * 100}
            else:
                data[name] = {"price": hist['Close'].iloc[-1], "change": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0}
    return data

def calculate_investment_plan(income: float, risk: str) -> Dict[str, Any]:
    """Calculates investment allocation using the 50/30/20 financial rule."""
    needs, wants, savings = income * 0.50, income * 0.30, income * 0.20
    emergency_target = income * 6
    emergency_monthly = min(savings * 0.3, income * 0.1) # Adaptive emergency capping
    invest_amount = savings - emergency_monthly

    allocations = {}
    if risk == "Conservative (Low Risk)":
        allocations = {"Sovereign Bonds/Sukuk": 0.40, "Fixed Deposits": 0.30, "Debt Funds": 0.20, "Gold ETF": 0.10}
    elif risk == "Moderate (Medium Risk)":
        allocations = {"Index Fund SIP": 0.35, "Balanced Funds": 0.25, "Sukuk/Bonds": 0.20, "Real Estate (REITs)": 0.15, "Gold ETF": 0.05}
    else:
        allocations = {"Direct Equity": 0.40, "Small/Mid Cap SIP": 0.25, "Index Fund SIP": 0.20, "Gold ETF": 0.10, "Crypto Assets": 0.05}

    return {
        "needs": needs, "wants": wants, "savings": savings, 
        "emergency_monthly": emergency_monthly, "invest_amount": invest_amount, 
        "allocations": allocations, "target": emergency_target
    }

def calculate_compounding(monthly_contribution: float, years: int, annual_return_pct: float) -> List[Dict[str, float]]:
    """Calculates compound interest projection matrix."""
    monthly_rate = annual_return_pct / 100 / 12
    data, corpus, invested = [], 0, 0
    for month in range(1, years * 12 + 1):
        corpus = (corpus + monthly_contribution) * (1 + monthly_rate)
        invested += monthly_contribution
        if month % 12 == 0:
            data.append({"Year": month // 12, "Invested": round(invested), "Corpus": round(corpus), "Gains": round(corpus - invested)})
    return data

# ── UI Rendering ──────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">FinWise Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Enterprise Investment Strategy · GCC Market Intelligence</div>', unsafe_allow_html=True)

# Localization Toggle
currency_col, _ = st.columns([1, 5])
with currency_col:
    currency_selector = st.selectbox("Select Region", ["UAE (AED د.إ)", "India (INR ₹)"])
    symbol = "AED " if "UAE" in currency_selector else "₹ "
    default_salary = 15000 if "UAE" in currency_selector else 50000

# Live Ticker
st.markdown('<p class="section-title">Global & GCC Markets</p>', unsafe_allow_html=True)
market = get_market_data()
cols = st.columns(len(market))
for i, (name, val) in enumerate(market.items()):
    with cols[i]:
        if "USD" in name: 
            st.metric(name, f"{val['price']:.3f}", f"{val['change']:+.2f}%", delta_color="inverse")
        elif name == "GOLD": 
            st.metric(name, f"${val['price']:,.0f}", f"{val['change']:+.2f}%")
        else: 
            st.metric(name, f"{val['price']:,.0f}", f"{val['change']:+.2f}%")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💰 Strategy Planner", "📈 Compounding Engine", "🌍 Global Trend Tracker"])

# ── TAB 1: Strategy ────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([1, 1.4])
    
    with col1:
        st.markdown('<p class="section-title">Client Profile</p>', unsafe_allow_html=True)
        income = st.number_input(f"Monthly Income ({symbol})", min_value=1000, max_value=1000000, value=default_salary, step=1000)
        risk = st.selectbox("Risk Appetite", ["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"])
        st.button("🚀 Calculate Strategy")

    with col2:
        plan = calculate_investment_plan(income, risk)
        st.markdown('<p class="section-title">Budget Allocation (50/30/20)</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["needs"]:,.0f}</div><div class="invest-label">🏠 Needs (50%)</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["wants"]:,.0f}</div><div class="invest-label">🎯 Wants (30%)</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["savings"]:,.0f}</div><div class="invest-label">💎 Savings (20%)</div></div>', unsafe_allow_html=True)

        fig = go.Figure(go.Pie(
            labels=list(plan['allocations'].keys()), 
            values=[plan['invest_amount'] * v for v in plan['allocations'].values()],
            hole=0.55, marker=dict(colors=['#00e5ff','#0091ea','#00b0ff','#80d8ff','#40c4ff','#29b6f6'])
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=280, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.markdown("### 📊 Monthly Portfolio Breakdown")
    alloc_data = [{"Asset Class": k, f"Monthly Allocation ({symbol})": f"{symbol}{plan['invest_amount']*v:,.0f}", "Weight": f"{int(v*100)}%"} for k, v in plan['allocations'].items()]
    st.dataframe(pd.DataFrame(alloc_data), use_container_width=True, hide_index=True)
    
    months_to_target = math.ceil(plan['target']/plan['emergency_monthly']) if plan['emergency_monthly'] > 0 else 0
    st.info(f"🏦 **Liquidity Goal:** Build {symbol}{plan['target']:,.0f} (6 months runway). Contributing {symbol}{plan['emergency_monthly']:,.0f}/mo reaches this in ~{months_to_target} months.")

# ── TAB 2: Compounding ─────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<p class="section-title">Projection Parameters</p>', unsafe_allow_html=True)
        sip_amount = st.number_input(f"Monthly Investment ({symbol})", min_value=500, value=int(plan['invest_amount']), step=500)
        years = st.slider("Duration (Years)", 1, 40, 15)
        return_rate = st.slider("Expected Annual Return (%)", 4.0, 20.0, 10.0, 0.5)
        
        data = calculate_compounding(sip_amount, years, return_rate)
        final = data[-1]
        st.markdown("---")
        st.metric("💎 Projected Corpus", f"{symbol}{final['Corpus']:,}")
        st.metric("💰 Capital Deployed", f"{symbol}{final['Invested']:,}")

    with col2:
        df = pd.DataFrame(data)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Year'], y=df['Invested'], name='Capital Deployed', marker_color='#1e3a5f'))
        fig.add_trace(go.Bar(x=df['Year'], y=df['Gains'], name='Wealth Generated', marker_color='#00e5ff'))
        fig.add_trace(go.Scatter(x=df['Year'], y=df['Corpus'], name='Total Portfolio Value', line=dict(color='#ff6b35', width=3)))
        fig.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=400, margin=dict(t=20, b=40, l=60, r=20))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

# ── TAB 3: Global Trends ───────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<p class="section-title">Asset Tracker</p>', unsafe_allow_html=True)
        assets = {"Saudi Tadawul": "^TASI.SR", "S&P 500": "^GSPC", "Nifty 50": "^NSEI", "Gold": "GC=F", "Crude Oil": "CL=F", "Bitcoin": "BTC-USD"}
        selected = st.selectbox("Select Asset", list(assets.keys()))
        period = st.selectbox("Historical Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"])
        show = st.button("📊 Render Technical Chart")
    with col2:
        if show:
            hist = yf.Ticker(assets[selected]).history(period=period)
            if not hist.empty:
                ret = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                color = '#00e676' if ret >= 0 else '#ff5252'
                fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], fill='tozeroy', line=dict(color=color, width=2)))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=350, title=f"{selected} ({ret:+.1f}%)")
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
