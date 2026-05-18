import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from typing import Dict, List, Any

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinWise Pro | Quant Analytics Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Production-Grade UI Styling (Dark Cyber Theme) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #060a13; color: #e2e8f0; }
.main { background-color: #060a13; }
h1, h2, h3 { font-family: 'Space Mono', monospace; color: #00f0ff; text-shadow: 0 0 10px rgba(0,240,255,0.1); }
.stMetric { background: linear-gradient(135deg, #0b1528, #12223f); border: 1px solid #00f0ff22; border-radius: 12px; padding: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.stMetric label { color: #94a3b8 !important; font-size: 13px !important; font-weight: 500; letter-spacing: 1px; }
.stMetric [data-testid="metric-container"] > div { color: #00f0ff !important; font-family: 'Space Mono', monospace; font-size: 24px !important; }
.invest-card { background: linear-gradient(135deg, #0b1528, #162a4e); border: 1px solid #00f0ff33; border-radius: 14px; padding: 22px; margin: 8px 0; text-align: center; }
.invest-amount { font-family: 'Space Mono', monospace; font-size: 26px; font-weight: 700; color: #00f0ff; }
.invest-label { font-size: 13px; color: #94a3b8; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }
.stButton > button { background: linear-gradient(135deg, #00f0ff, #0072ff); color: #060a13; font-family: 'Space Mono', monospace; font-weight: 700; border: none; border-radius: 8px; padding: 14px 28px; font-size: 15px; width: 100%; transition: all 0.3s ease; letter-spacing: 1px; }
.stButton > button:hover { background: linear-gradient(135deg, #ff5722, #ff9800); color: #fff; transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,87,34,0.4); }
.section-title { font-family: 'Space Mono', monospace; font-size: 12px; letter-spacing: 3px; color: #00f0ff; text-transform: uppercase; margin-bottom: 6px; }
.hero-title { font-family: 'Space Mono', monospace; font-size: 46px; font-weight: 700; background: linear-gradient(135deg, #00f0ff, #7000ff, #ff007c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin-bottom: 4px; }
.tax-badge { display: inline-block; background: #00e6761a; border: 1px solid #00e676; border-radius: 4px; padding: 2px 6px; font-size: 10px; color: #00e676; margin-left: 6px; font-weight: bold; }
.metric-box { background: #09111f; border-left: 4px solid #ff007c; padding: 12px; border-radius: 6px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Core Quantitative Math Engines ───────────────────────────────────────────

@st.cache_data(ttl=300)
def get_market_data() -> Dict[str, Dict[str, float]]:
    """Fetches real-time tickers and calculates precise interday changes."""
    tickers = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANK NIFTY": "^NSEBANK", "GOLD (MCX)": "GC=F", "USD/INR": "INR=X"}
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

def calculate_quant_metrics(df: pd.DataFrame, risk_free_rate: float = 0.07) -> Dict[str, float]:
    """Computes advanced algorithmic financial risk parameters natively."""
    if df.empty or len(df) < 10:
        return {"Sharpe Ratio": 0.0, "Annualized Volatility": 0.0, "Max Drawdown": 0.0}
    
    # Calculate log returns for mathematical statistical robustness
    df['Returns'] = df['Close'].pct_change()
    
    # Annualized Volatility calculation
    daily_vol = df['Returns'].std()
    annual_vol = daily_vol * np.sqrt(252)
    
    # Annualized Sharpe Ratio calculation (assuming Risk-Free yield of 7% RBI Repo rate)
    annual_return = df['Returns'].mean() * 252
    excess_return = annual_return - risk_free_rate
    sharpe_ratio = excess_return / annual_vol if annual_vol != 0 else 0.0
    
    # Maximum Drawdown peak-to-trough drop calculation
    cum_returns = (1 + df['Returns'].dropna()).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    max_dd = drawdown.min() * 100
    
    return {
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Annualized Volatility": round(annual_vol * 100, 2),
        "Max Drawdown": round(max_dd, 2)
    }

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes basic core math calculations for SMA, EMA, and RSI natively."""
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # Native RSI-14 Engine calculation
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    # Avoid mathematical zero division context errors
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50) # Fallback baseline normalization
    return df

def calculate_stepup_compounding(monthly_sip: float, step_up_pct: float, years: int, annual_return_pct: float) -> List[Dict[str, float]]:
    """Calculates premium Step-Up compounding logic month-by-month."""
    monthly_rate = annual_return_pct / 100 / 12
    data, corpus, total_invested = [], 0.0, 0.0
    current_sip = monthly_sip

    for year in range(1, years + 1):
        year_invested = 0.0
        for month in range(1, 13):
            corpus = (corpus + current_sip) * (1 + monthly_rate)
            total_invested += current_sip
            year_invested += current_sip
        
        data.append({
            "Year": year,
            "Monthly SIP": round(current_sip),
            "Invested": round(total_invested),
            "Corpus": round(corpus),
            "Gains": round(corpus - total_invested)
        })
        # Step-up increment applies seamlessly at the end of every fiscal cycle
        current_sip = current_sip * (1 + (step_up_pct / 100))
        
    return data

# ── Master Dashboard Layout Rendering ────────────────────────────────────────

st.markdown('<div class="hero-title">FinWise Pro Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Quantitative Risk Architecture & Quantitative Financial Strategy</div>', unsafe_allow_html=True)

# Real-Time Market Feed
st.markdown('<p class="section-title">Live Indian Indices & Macro Variables</p>', unsafe_allow_html=True)
market = get_market_data()
cols = st.columns(len(market))
for i, (name, val) in enumerate(market.items()):
    with cols[i]:
        if name == "USD/INR": 
            st.metric(name, f"₹{val['price']:.2f}", f"{val['change']:+.2f}%", delta_color="inverse")
        elif name == "GOLD (MCX)": 
            st.metric(name, f"${val['price']:,.0f}/oz", f"{val['change']:+.2f}%")
        else: 
            st.metric(name, f"{val['price']:,.0f}", f"{val['change']:+.2f}%")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Asset Class Allocator", "📈 Step-Up SIP Engine", "⚡ Market Quantitative Analytics"])

# ── TAB 1: Asset Allocation ──────────────────────────────────────────────────
with tab1:
    st.markdown("## 💰 Strategic Asset Management")
    col1, col2 = st.columns([1, 1.4])
    
    with col1:
        st.markdown('<p class="section-title">Client Profile Matrix</p>', unsafe_allow_html=True)
        income = st.number_input("Monthly In-Hand Net Income (Ref: ₹)", min_value=15000, max_value=2000000, value=75000, step=5000)
        risk = st.selectbox("Algorithmic Risk Filter Profile", ["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"])
        
        needs, wants, savings = income * 0.50, income * 0.30, income * 0.20
        emergency_target = income * 6
        emergency_monthly = min(savings * 0.3, 5000)
        invest_amount = savings - emergency_monthly

        if risk == "Conservative (Low Risk)":
            allocations = {"Bank FDs / Liquid Mutual Funds": 0.40, "PPF / EPF (80C Tax-Exempt)": 0.30, "Arbitrage Funds": 0.20, "Sovereign Gold Bonds (SGB)": 0.10}
        elif risk == "Moderate (Medium Risk)":
            allocations = {"Nifty 50 Index Fund (Large Cap)": 0.35, "Flexi-Cap Diversified Funds": 0.25, "PPF / ELSS (Tax-Saving Category)": 0.20, "Highly Rated Corporate Bonds": 0.15, "Gold ETF": 0.05}
        else:
            allocations = {"Nifty Midcap 150 Index Funds": 0.40, "Direct Nifty Bluechip Equities": 0.25, "Nifty Next 50 ETF": 0.20, "ELSS Mutual Funds": 0.10, "Alternative Assets / Options Hedging": 0.05}

    with col2:
        st.markdown('<p class="section-title">Capital Distribution Architecture</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="invest-card"><div class="invest-amount">₹{needs:,.0f}</div><div class="invest-label">🏠 Operating Costs (50%)</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="invest-card"><div class="invest-amount">₹{wants:,.0f}</div><div class="invest-label">🎯 Discretionary (30%)</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="invest-card"><div class="invest-amount">₹{savings:,.0f}</div><div class="invest-label">💎 Retained Capital (20%)</div></div>', unsafe_allow_html=True)

        fig = go.Figure(go.Pie(
            labels=list(allocations.keys()), 
            values=[invest_amount * v for v in allocations.values()],
            hole=0.55, marker=dict(colors=['#00f0ff','#0072ff','#7000ff','#ff007c','#ff5722'])
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2e8f0'), height=260, margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.markdown("### 📊 Absolute Deployment Manifest")
    table_html = "<table style='width:100%; text-align:left; border-collapse: collapse;'><tr><th style='padding:12px; border-bottom: 2px solid #00f0ff22; color: #00f0ff;'>Asset Strategy Vehicle</th><th style='padding:12px; border-bottom: 2px solid #00f0ff22; color: #00f0ff;'>Monthly Contribution Allocation</th><th style='padding:12px; border-bottom: 2px solid #00f0ff22; color: #00f0ff;'>Strategic Weight</th></tr>"
    for k, v in allocations.items():
        badge = '<span class="tax-badge">Tax Shield Sec 80C</span>' if any(x in k for x in ['Tax', 'PPF', 'ELSS']) else ''
        table_html += f"<tr><td style='padding:12px; border-bottom: 1px solid #00f0ff11;'>{k} {badge}</td><td style='padding:12px; border-bottom: 1px solid #00f0ff11;'>₹{invest_amount*v:,.0f}</td><td style='padding:12px; border-bottom: 1px solid #00f0ff11;'>{int(v*100)}%</td></tr>"
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

# ── TAB 2: Step-Up SIP Engine ────────────────────────────────────────────────
with tab2:
    st.markdown("## 📈 Dynamic Growth & Step-Up Compounding Engine")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<p class="section-title">Parametric Matrix Inputs</p>', unsafe_allow_html=True)
        initial_sip = st.number_input("Base Starting Monthly SIP (₹)", min_value=500, value=10000, step=500)
        annual_step_up = st.slider("Annual Contribution Step-Up Increment Percentage (%)", 0, 25, 10)
        horizon_years = st.slider("Absolute Investment Horizon (Years Scale)", 1, 35, 15)
        rate_of_return = st.slider("Conservative Expected Compounding Annual Return (%)", 5.0, 22.0, 13.0, 0.5)
        
        compounding_matrix = calculate_stepup_compounding(initial_sip, annual_step_up, horizon_years, rate_of_return)
        terminal_record = compounding_matrix[-1]
        
        st.markdown("---")
        st.metric("💎 Terminal Asset Corpus Value", f"₹{terminal_record['Corpus']:,}")
        st.metric("💰 Total Cumulative Net Capital Invested", f"₹{terminal_record['Invested']:,}")
        st.metric("🚀 Absolute Net Capital Gains Accrued", f"₹{terminal_record['Gains']:,}")

    with col2:
        df_comp = pd.DataFrame(compounding_matrix)
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=df_comp['Year'], y=df_comp['Invested'], name='Total Capital Input Stream', marker_color='#0b1528', marker_line_color='#00f0ff', marker_line_width=1))
        fig_comp.add_trace(go.Bar(x=df_comp['Gains'], x=df_comp['Year'], name='Cumulative Compound Interest Value Generator', marker_color='#ff007c'))
        fig_comp.add_trace(go.Scatter(x=df_comp['Year'], y=df_comp['Corpus'], name='Total Absolute Portfolio Curve Valuation', line=dict(color='#00f0ff', width=3)))
        fig_comp.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2e8f0'), height=420, margin=dict(t=20, b=40, l=60, r=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_comp.update_xaxes(gridcolor='#1e293b')
        fig_comp.update_yaxes(gridcolor='#1e293b')
        st.plotly_chart(fig_comp, width="stretch", config={'displayModeBar': False})

# ── TAB 3: Advanced Market Analytics ─────────────────────────────────────────
with tab3:
    st.markdown("## ⚡ Deep Equity Technical Analytics & Statistical Risk Model")
    col1, col2 = st.columns([1, 2.2])
    
    with col1:
        st.markdown('<p class="section-title">Asset Specification Selector</p>', unsafe_allow_html=True)
        equities_pool = {
            "Reliance Industries Ltd.": "RELIANCE.NS",
            "HDFC Bank Ltd.": "HDFCBANK.NS",
            "Tata Consultancy Services (TCS)": "TCS.NS",
            "Infosys Ltd.": "INFY.NS",
            "State Bank of India (SBI)": "SBIN.NS",
            "NIFTY 50 Index Asset": "^NSEI"
        }
        selected_equity = st.selectbox("Choose Target Equity for Analysis", list(equities_pool.keys()))
        analysis_window = st.selectbox("Historical Time-Series Lookback Horizon", ["1y", "2y", "5y"])
        
        # Pull core raw historical data matrix
        ticker_endpoint = equities_pool[selected_equity]
        raw_df = yf.Ticker(ticker_endpoint).history(period=analysis_window)
        
        if not raw_df.empty:
            # Execute backend computational engines natively
            processed_df = calculate_technical_indicators(raw_df.copy())
            risk_metrics = calculate_quant_metrics(raw_df.copy())
            
            st.markdown("### 📊 Portfolio Risk Architecture Metrics")
            st.markdown(f'<div class="metric-box"><b>Sharpe Ratio:</b> {risk_metrics["Sharpe Ratio"]}<br><small>Risk-Adjusted Outperformance Efficiency Index</small></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box"><b>Annualized Volatility Risk:</b> {risk_metrics["Annualized Volatility"]}%<br><small>Standard Deviation Deviance Index Factor</small></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box"><b>Max Peak-to-Trough Drawdown:</b> {risk_metrics["Max Drawdown"]}%<br><small>Worst Case Peak-to-Valley Historical Loss</small></div>', unsafe_allow_html=True)
            
            # Real-time mathematical parsing of terminal momentum values
            last_rsi = processed_df['RSI'].iloc[-1]
            rsi_condition = "🔴 OVERBOUGHT RISK ZONE" if last_rsi > 70 else "🟢 OVERSOLD ACCUMULATION ZONE" if last_rsi < 30 else "🟡 NEUTRAL MOMENTUM AXIS"
            st.markdown(f'<div class="metric-box" style="border-left-color: #00f0ff"><b>RSI Momentum (14):</b> {last_rsi:.2f}<br><small>{rsi_condition}</small></div>', unsafe_allow_html=True)

    with col2:
        if not raw_df.empty:
            # Generate advanced professional multi-axis analytical graphs using pure Plotly mechanics
            fig_quant = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_width=[0.3, 0.7])
            
            # Primary structural candlestick line trend representation overlaying moving averages
            fig_quant.add_trace(go.Scatter(x=processed_df.index, y=processed_df['Close'], name='Closing Execution Price', line=dict(color='#00f0ff', width=2)), row=1, col=1)
            fig_quant.add_trace(go.Scatter(x=processed_df.index, y=processed_df['SMA_20'], name='SMA (20 Cycle Momentum)', line=dict(color='#ff007c', width=1.5, dash='dot')), row=1, col=1)
            fig_quant.add_trace(go.Scatter(x=processed_df.index, y=processed_df['EMA_50'], name='EMA (50 Cycle Trend Line)', line=dict(color='#7000ff', width=1.5, dash='dash')), row=1, col=1)
            
            # Momentum oscillator tracking channel subplot architecture
            fig_quant.add_trace(go.Scatter(x=processed_df.index, y=processed_df['RSI'], name='RSI Oscillator Scale', line=dict(color='#e2e8f0', width=1.5)), row=2, col=1)
            
            # Injecting professional standard horizontal support parameters within oscillator threshold ranges
            fig_quant.add_hline(y=70, line_dash="dash", line_color="#ff5722", line_width=1, row=2, col=1)
            fig_quant.add_hline(y=30, line_dash="dash", line_color="#00e676", line_width=1, row=2, col=1)
            
            fig_quant.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2e8f0'), height=550, margin=dict(t=10, b=10, l=10, r=10), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
            fig_quant.update_xaxes(gridcolor='#1e293b', row=1, col=1)
            fig_quant.update_xaxes(gridcolor='#1e293b', row=2, col=1)
            fig_quant.update_yaxes(gridcolor='#1e293b', title_text="Price Axis Scale", row=1, col=1)
            fig_quant.update_yaxes(gridcolor='#1e293b', title_text="RSI Value Channel", row=2, col=1, range=[10, 90])
            
            st.plotly_chart(fig_quant, width="stretch", config={'displayModeBar': False})
        else:
            st.error("Time-Series stream broken. Please re-verify endpoint query verification parameters.")

# Footer Section
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#475569;font-size:12px;font-family:'Space Mono',monospace;letter-spacing:1px;">
    FinWise Pro Engine Engine v2.4 • System Architecture Core: Python 3.11 + Streamlit Frame Protocol • Core Analytics Executed Natively via Mathematical Vector Mapping
</div>
""", unsafe_allow_html=True)
