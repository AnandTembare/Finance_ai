import streamlit as st
import yfinance as yf
import math
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinWise Analytics | Wealth Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS for Premium Dark UI ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

/* Base Styles */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    background-color: #0B0E14; 
    color: #E2E8F0; 
}
.stApp { background-color: #0B0E14; }

/* Typography */
h1, h2, h3 { font-family: 'Space Mono', monospace; color: #00E5FF; }
.hero-title { 
    font-family: 'Space Mono', monospace; 
    font-size: 46px; 
    font-weight: 700; 
    background: linear-gradient(135deg, #00E5FF, #007BFF, #8A2BE2); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    line-height: 1.2; 
    margin-bottom: 4px; 
}
.hero-subtitle { font-size: 16px; color: #94A3B8; margin-bottom: 30px; letter-spacing: 1px; }
.section-title { 
    font-family: 'Space Mono', monospace; 
    font-size: 12px; 
    letter-spacing: 2px; 
    color: #00E5FF; 
    text-transform: uppercase; 
    margin-bottom: 12px; 
    border-bottom: 1px solid #1E293B;
    padding-bottom: 8px;
}

/* Metrics & Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #0F172A);
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
div[data-testid="metric-container"] > label { color: #94A3B8 !important; font-size: 14px !important; font-weight: 500;}
div[data-testid="metric-container"] > div { color: #F8FAFC !important; font-family: 'Space Mono', monospace; }

.invest-card { 
    background: linear-gradient(145deg, #111827, #0F172A); 
    border: 1px solid #1E293B; 
    border-radius: 12px; 
    padding: 24px 16px; 
    text-align: center; 
    transition: transform 0.2s ease;
}
.invest-card:hover { transform: translateY(-3px); border-color: #00E5FF; }
.invest-amount { font-family: 'Space Mono', monospace; font-size: 26px; font-weight: 700; color: #F8FAFC; }
.invest-label { font-size: 14px; color: #94A3B8; margin-top: 8px; font-weight: 500; }

/* Buttons */
.stButton > button { 
    background: linear-gradient(135deg, #00E5FF, #007BFF); 
    color: #0B0E14; 
    font-family: 'Space Mono', monospace; 
    font-weight: 700; 
    border: none; 
    border-radius: 8px; 
    padding: 12px 24px; 
    width: 100%; 
    transition: all 0.3s ease; 
}
.stButton > button:hover { 
    background: linear-gradient(135deg, #007BFF, #8A2BE2); 
    color: white;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3); 
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 2px solid #1E293B; }
.stTabs [data-baseweb="tab"] { color: #94A3B8; font-family: 'Space Mono', monospace; font-size: 14px; }
.stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom-color: #00E5FF !important; }
</style>
""", unsafe_allow_html=True)

# ── Core Business Logic ───────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_market_data() -> Dict[str, Dict[str, float]]:
    """Fetches live market indices with robust error handling."""
    tickers = {
        "NIFTY 50": "^NSEI", 
        "S&P 500": "^GSPC", 
        "GOLD (Ounce)": "GC=F", 
        "CRUDE OIL": "CL=F",
        "BTC/USD": "BTC-USD",
        "USD/INR": "INR=X"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d") # Fetch 5 days to ensure we get valid close prices over weekends
            if len(hist) >= 2:
                curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                data[name] = {"price": curr, "change": ((curr - prev) / prev) * 100}
            elif len(hist) == 1:
                data[name] = {"price": hist['Close'].iloc[-1], "change": 0.0}
            else:
                data[name] = {"price": 0.0, "change": 0.0}
        except Exception:
            data[name] = {"price": 0.0, "change": 0.0}
    return data

def calculate_investment_plan(income: float, risk: str) -> Dict[str, Any]:
    """Calculates investment allocation using the 50/30/20 financial rule."""
    needs, wants, savings = income * 0.50, income * 0.30, income * 0.20
    emergency_target = income * 6
    emergency_monthly = min(savings * 0.3, income * 0.1)
    invest_amount = savings - emergency_monthly

    if risk == "Conservative (Low Risk)":
        allocations = {"Sovereign Bonds/FDs": 0.50, "Large Cap Index": 0.30, "Gold": 0.20}
    elif risk == "Moderate (Medium Risk)":
        allocations = {"Large Cap Index": 0.40, "Mid Cap SIP": 0.25, "Debt Funds": 0.20, "Gold": 0.15}
    else:
        allocations = {"Small/Mid Cap Equity": 0.45, "Large Cap Index": 0.30, "International Tech": 0.15, "Crypto/High Risk": 0.10}

    return {
        "needs": needs, "wants": wants, "savings": savings, 
        "emergency_monthly": emergency_monthly, "invest_amount": invest_amount, 
        "allocations": allocations, "target": emergency_target
    }

def calculate_compounding(monthly_contribution: float, years: int, annual_return_pct: float) -> pd.DataFrame:
    """Calculates compound interest projection matrix."""
    monthly_rate = annual_return_pct / 100 / 12
    data, corpus, invested = [], 0, 0
    for month in range(1, years * 12 + 1):
        corpus = (corpus + monthly_contribution) * (1 + monthly_rate)
        invested += monthly_contribution
        if month % 12 == 0:
            data.append({
                "Year": month // 12, 
                "Invested": round(invested), 
                "Corpus": round(corpus), 
                "Gains": round(corpus - invested)
            })
    return pd.DataFrame(data)

# ── UI Rendering ──────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">FinWise Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Institutional Grade Wealth Management & Market Intelligence</div>', unsafe_allow_html=True)

# Live Ticker Dashboard
st.markdown('<p class="section-title">Live Global Markets</p>', unsafe_allow_html=True)
with st.spinner("Syncing with global exchanges..."):
    market = get_market_data()

cols = st.columns(len(market))
for i, (name, val) in enumerate(market.items()):
    with cols[i]:
        # Formatting logic based on asset type
        if "USD" in name or "INR" in name and "BTC" not in name: 
            st.metric(name, f"{val['price']:.2f}", f"{val['change']:+.2f}%", delta_color="inverse")
        else: 
            st.metric(name, f"{val['price']:,.2f}", f"{val['change']:+.2f}%")
st.markdown("<br>", unsafe_allow_html=True)

# Main Application Tabs
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Strategy", "📈 Compounding Engine", "🕯️ Technical Tracker"])

symbol = "₹"

# ── TAB 1: Strategy ────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([1, 1.8], gap="large")
    
    with col1:
        st.markdown('<p class="section-title">Client Profile</p>', unsafe_allow_html=True)
        income = st.number_input(f"Monthly Income ({symbol})", min_value=10000, max_value=10000000, value=100000, step=5000)
        risk = st.selectbox("Risk Appetite", ["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"], index=1)
        
        plan = calculate_investment_plan(income, risk)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Liquidity Goal</p>', unsafe_allow_html=True)
        months_to_target = math.ceil(plan['target'] / plan['emergency_monthly']) if plan['emergency_monthly'] > 0 else 0
        st.info(f"**Emergency Fund Target:** {symbol}{plan['target']:,.0f} (6 months expenses)\n\nRouting {symbol}{plan['emergency_monthly']:,.0f}/month to liquid savings to reach this in **{months_to_target} months**.")

    with col2:
        st.markdown('<p class="section-title">Optimal Budget Allocation (50/30/20 Rule)</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["needs"]:,.0f}</div><div class="invest-label">🏠 Needs (50%)</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["wants"]:,.0f}</div><div class="invest-label">🎯 Wants (30%)</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="invest-card"><div class="invest-amount">{symbol}{plan["savings"]:,.0f}</div><div class="invest-label">💎 Savings (20%)</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<p class="section-title">Deployment Strategy: {symbol}{plan["invest_amount"]:,.0f} / Month</p>', unsafe_allow_html=True)
        
        # Donut Chart for Allocation
        fig = go.Figure(go.Pie(
            labels=list(plan['allocations'].keys()), 
            values=[plan['invest_amount'] * v for v in plan['allocations'].values()],
            hole=0.65, 
            marker=dict(colors=['#00E5FF', '#3B82F6', '#8A2BE2', '#F59E0B', '#10B981']),
            textinfo='label+percent',
            textposition='outside'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Inter'), 
            height=320, 
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ── TAB 2: Compounding ─────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns([1, 2.5], gap="large")
    
    with col1:
        st.markdown('<p class="section-title">Growth Parameters</p>', unsafe_allow_html=True)
        sip_amount = st.number_input(f"Monthly Investment ({symbol})", min_value=500, value=int(plan['invest_amount']), step=1000)
        years = st.slider("Time Horizon (Years)", 1, 40, 15)
        return_rate = st.slider("Expected Annual Return (%)", 4.0, 25.0, 12.0, 0.5)
        
        df = calculate_compounding(sip_amount, years, return_rate)
        final = df.iloc[-1]
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Future Value</p>', unsafe_allow_html=True)
        st.metric("Total Portfolio Value", f"{symbol}{final['Corpus']:,.0f}")
        st.metric("Total Capital Deployed", f"{symbol}{final['Invested']:,.0f}")
        st.metric("Wealth Generated (Interest)", f"{symbol}{final['Gains']:,.0f}", f"{(final['Gains']/final['Invested'])*100:,.0f}% ROI")

    with col2:
        st.markdown('<p class="section-title">Wealth Accumulation Trajectory</p>', unsafe_allow_html=True)
        # Advanced Area Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Year'], y=df['Invested'], 
            name='Capital Deployed', 
            mode='lines',
            line=dict(color='#3B82F6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=df['Year'], y=df['Corpus'], 
            name='Total Portfolio Value', 
            mode='lines',
            line=dict(color='#00E5FF', width=3),
            fill='tonexty',
            fillcolor='rgba(0, 229, 255, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Inter'), 
            height=450, 
            margin=dict(t=20, b=40, l=10, r=10),
            xaxis=dict(showgrid=False, title="Years"),
            yaxis=dict(showgrid=True, gridcolor='#1E293B', title=f"Value ({symbol})"),
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(15,23,42,0.8)')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ── TAB 3: Global Trends ───────────────────────────────────────────────────────
with tab3:
    st.markdown('<p class="section-title">Professional Technical Analysis</p>', unsafe_allow_html=True)
    
    col_config, col_chart = st.columns([1, 4])
    
    with col_config:
        assets = {
            "S&P 500 (US)": "^GSPC", 
            "Nifty 50 (India)": "^NSEI", 
            "BSE Sensex": "^BSESN",
            "Gold Future": "GC=F", 
            "Bitcoin": "BTC-USD",
            "Apple Inc.": "AAPL"
        }
        selected = st.selectbox("Select Asset", list(assets.keys()))
        period = st.select_slider("Historical Timeframe", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="6mo")
        render_btn = st.button("Generate Chart")

    with col_chart:
        ticker_symbol = assets[selected]
        with st.spinner(f"Fetching institutional data for {selected}..."):
            hist = yf.Ticker(ticker_symbol).history(period=period)
            
            if not hist.empty:
                ret = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                
                # Professional Candlestick Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    increasing_line_color='#10B981',  # Green for up
                    decreasing_line_color='#EF4444'   # Red for down
                )])
                
                fig.update_layout(
                    template='plotly_dark',
                    title=f"{selected} Trend | Period Return: {ret:+.2f}%",
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94A3B8', family='Inter'), 
                    height=500,
                    margin=dict(t=50, b=20, l=10, r=10),
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(showgrid=False, type='category'),
                    yaxis=dict(showgrid=True, gridcolor='#1E293B')
                )
                
                # Customize x-axis labels to look clean
                fig.update_xaxes(
                    tickformat="%b %d\n%Y",
                    nticks=10
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.error("Market data currently unavailable for this asset. It may be delisted or experiencing API rate limits.")
