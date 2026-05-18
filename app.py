import streamlit as st
import yfinance as yf
import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinWise — Investment Analytics",
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

.news-card { background: linear-gradient(135deg, #0d1b2a, #111e35); border: 1px solid #1e3a5f; border-left: 4px solid #00e5ff; border-radius: 10px; padding: 16px; margin: 10px 0; transition: all 0.3s ease; }
.news-card:hover { border-left-color: #ff6b35; transform: translateX(4px); }

.invest-card { background: linear-gradient(135deg, #0d1b2a, #1a2744); border: 1px solid #00e5ff33; border-radius: 14px; padding: 20px; margin: 8px 0; text-align: center; }
.invest-amount { font-family: 'Space Mono', monospace; font-size: 28px; font-weight: 700; color: #00e5ff; }
.invest-label { font-size: 13px; color: #90caf9; margin-top: 4px; }

.stButton > button { background: linear-gradient(135deg, #00e5ff, #0091ea); color: #0a0f1e; font-family: 'Space Mono', monospace; font-weight: 700; border: none; border-radius: 8px; padding: 12px 28px; font-size: 15px; width: 100%; transition: all 0.3s ease; }
.stButton > button:hover { background: linear-gradient(135deg, #ff6b35, #ff3d00); transform: translateY(-2px); box-shadow: 0 8px 25px #ff6b3540; }
.section-title { font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 3px; color: #00e5ff; text-transform: uppercase; margin-bottom: 4px; }
.hero-title { font-family: 'Space Mono', monospace; font-size: 42px; font-weight: 700; background: linear-gradient(135deg, #00e5ff, #00b0ff, #ff6b35); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin-bottom: 8px; }
.hero-subtitle { color: #90caf9; font-size: 16px; margin-bottom: 32px; }
.stTabs [data-baseweb="tab-list"] { background: #0d1b2a; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #90caf9; font-family: 'DM Sans', sans-serif; font-weight: 500; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #00e5ff22, #0091ea22) !important; color: #00e5ff !important; border-radius: 8px; }
hr { border-color: #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_market_data():
    """Fetch live market indices"""
    tickers = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "GOLD": "GC=F", "USD/INR": "INR=X"}
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
        except:
            data[name] = {"price": 0, "change": 0}
    return data

@st.cache_data(ttl=3600)
def get_live_news():
    """Fetch real global market news via yfinance"""
    try:
        # SPY ETF acts as a good proxy for global financial news
        news = yf.Ticker("SPY").news
        return news[:6]
    except:
        return []

def calculate_investment_plan(salary, risk):
    """Calculate investment allocation using 50/30/20 rule"""
    needs, wants, savings = salary * 0.50, salary * 0.30, salary * 0.20
    emergency_fund_target = salary * 6
    emergency_monthly = min(savings * 0.3, 5000)
    invest_amount = savings - emergency_monthly

    if risk == "Conservative (Low Risk)":
        allocations = {"FD / Liquid Fund": 0.40, "PPF / NPS": 0.30, "Debt Mutual Funds": 0.20, "Gold ETF": 0.10}
    elif risk == "Moderate (Medium Risk)":
        allocations = {"Index Fund SIP": 0.35, "Balanced Funds": 0.25, "PPF / NPS": 0.20, "FDs": 0.15, "Gold ETF": 0.05}
    else:
        allocations = {"Direct Equity": 0.40, "Small/Mid Cap SIP": 0.25, "Index Fund SIP": 0.20, "Gold ETF": 0.10, "Crypto/High Risk": 0.05}

    return {"needs": needs, "wants": wants, "savings": savings, "emergency_monthly": emergency_monthly, 
            "invest_amount": invest_amount, "allocations": allocations, "target": emergency_fund_target}

def calculate_compounding(monthly_sip, years, annual_return_pct):
    """Calculate SIP compounding growth month by month"""
    monthly_rate = annual_return_pct / 100 / 12
    data, corpus, invested = [], 0, 0
    for month in range(1, years * 12 + 1):
        corpus = (corpus + monthly_sip) * (1 + monthly_rate)
        invested += monthly_sip
        if month % 12 == 0:
            data.append({"Year": month // 12, "Invested": round(invested), "Corpus": round(corpus), "Gains": round(corpus - invested)})
    return data

# ── Main App ──────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">FinWise Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Investment Strategy · Live Market Intelligence · Compounding Engine</div>', unsafe_allow_html=True)

# Live Ticker
st.markdown('<p class="section-title">Live Markets</p>', unsafe_allow_html=True)
market = get_market_data()
cols = st.columns(len(market))
for i, (name, val) in enumerate(market.items()):
    with cols[i]:
        if name == "USD/INR": st.metric(name, f"₹{val['price']:.2f}", f"{val['change']:+.2f}%", delta_color="inverse")
        elif name == "GOLD": st.metric(name, f"${val['price']:,.0f}", f"{val['change']:+.2f}%")
        else: st.metric(name, f"{val['price']:,.0f}", f"{val['change']:+.2f}%")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["💰 Investment Planner", "📰 Live Market News", "📈 Compounding Calculator", "🌍 Global Trend Tracker"])

# ── TAB 1 ──────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("## 💰 Personal Investment Strategy")
    col1, col2 = st.columns([1, 1.4])
    
    with col1:
        st.markdown('<p class="section-title">Your Profile</p>', unsafe_allow_html=True)
        salary = st.number_input("Monthly Salary (₹)", min_value=10000, max_value=500000, value=30000, step=1000)
        risk = st.selectbox("Risk Appetite", ["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"])
        generate = st.button("🚀 Calculate Strategy")

    with col2:
        plan = calculate_investment_plan(salary, risk)
        st.markdown('<p class="section-title">Budget Breakdown (50/30/20 Rule)</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="invest-card"><div class="invest-amount">₹{plan["needs"]:,.0f}</div><div class="invest-label">🏠 Needs (50%)</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="invest-card"><div class="invest-amount">₹{plan["wants"]:,.0f}</div><div class="invest-label">🎯 Wants (30%)</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="invest-card"><div class="invest-amount">₹{plan["savings"]:,.0f}</div><div class="invest-label">💎 Savings (20%)</div></div>', unsafe_allow_html=True)

        fig = go.Figure(go.Pie(
            labels=list(plan['allocations'].keys()), 
            values=[plan['invest_amount'] * v for v in plan['allocations'].values()],
            hole=0.55, marker=dict(colors=['#00e5ff','#0091ea','#00b0ff','#80d8ff','#40c4ff','#29b6f6'])
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=280, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.markdown("### 📊 Monthly Investment Breakdown")
    alloc_data = [{"Investment": k, "Monthly (₹)": f"₹{plan['invest_amount']*v:,.0f}", "Allocation": f"{int(v*100)}%"} for k, v in plan['allocations'].items()]
    st.dataframe(pd.DataFrame(alloc_data), use_container_width=True, hide_index=True)
    st.info(f"🏦 **Emergency Fund Goal:** Save ₹{plan['target']:,.0f} (6 months salary). Contributing ₹{plan['emergency_monthly']:,.0f}/mo will get you there in ~{math.ceil(plan['target']/plan['emergency_monthly'])} months.")

# ── TAB 2 ──────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("## 📰 Live Market News")
    st.markdown("*Real-time financial headlines directly from global markets.*")
    
    with st.spinner("Fetching live news..."):
        news_items = get_live_news()
        
    if news_items:
        for item in news_items:
            title = item.get('title', 'Market Update')
            publisher = item.get('publisher', 'Financial News')
            link = item.get('link', '#')
            st.markdown(f"""
            <div class="news-card">
                <div style="font-weight:600;font-size:16px;color:#e8eaf6;margin-bottom:8px">📰 {title}</div>
                <div style="color:#90caf9;font-size:13px;line-height:1.6">Source: {publisher}</div>
                <a href="{link}" target="_blank" style="color:#00e5ff;font-size:13px;text-decoration:none;margin-top:8px;display:block">Read Full Article →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No live news available right now. Please check back later.")

# ── TAB 3 ──────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("## 📈 Compounding Growth Calculator")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<p class="section-title">SIP Parameters</p>', unsafe_allow_html=True)
        sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, value=5000, step=500)
        years = st.slider("Duration (Years)", 1, 40, 15)
        return_rate = st.slider("Annual Return (%)", 6.0, 20.0, 12.0, 0.5)
        
        data = calculate_compounding(sip_amount, years, return_rate)
        final = data[-1]
        st.markdown("---")
        st.metric("💎 Final Corpus", f"₹{final['Corpus']:,}")
        st.metric("💰 Total Invested", f"₹{final['Invested']:,}")

    with col2:
        df = pd.DataFrame(data)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Year'], y=df['Invested'], name='Invested', marker_color='#1e3a5f'))
        fig.add_trace(go.Bar(x=df['Year'], y=df['Gains'], name='Gains', marker_color='#00e5ff'))
        fig.add_trace(go.Scatter(x=df['Year'], y=df['Corpus'], name='Total Corpus', line=dict(color='#ff6b35', width=3)))
        fig.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=400, margin=dict(t=20, b=40, l=60, r=20))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

# ── TAB 4 ──────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("## 🌍 Global Trend Tracker")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<p class="section-title">Select Asset</p>', unsafe_allow_html=True)
        assets = {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "S&P 500": "^GSPC", "Reliance": "RELIANCE.NS", "TCS": "TCS.NS", "Gold": "GC=F", "Bitcoin": "BTC-USD"}
        selected = st.selectbox("Asset", list(assets.keys()))
        period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"])
        show = st.button("📊 Load Chart")
    with col2:
        if show:
            hist = yf.Ticker(assets[selected]).history(period=period)
            if not hist.empty:
                ret = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                color = '#00e676' if ret >= 0 else '#ff5252'
                fig = go.Figure(go.Scatter(x=hist.index, y=hist['Close'], fill='tozeroy', line=dict(color=color, width=2)))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6'), height=350, title=f"{selected} ({ret:+.1f}%)")
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
