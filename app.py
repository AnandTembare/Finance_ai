import streamlit as st
import anthropic
import yfinance as yf
import requests
import json
import math
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinWise AI — Investment Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0f1e;
    color: #e8eaf6;
}

.main { background-color: #0a0f1e; }

h1, h2, h3 {
    font-family: 'Space Mono', monospace;
    color: #00e5ff;
}

.stMetric {
    background: linear-gradient(135deg, #0d1b2a, #1a2744);
    border: 1px solid #00e5ff33;
    border-radius: 12px;
    padding: 16px;
}

.stMetric label { color: #90caf9 !important; font-size: 13px !important; }
.stMetric [data-testid="metric-container"] > div { color: #00e5ff !important; }

.news-card {
    background: linear-gradient(135deg, #0d1b2a, #111e35);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #00e5ff;
    border-radius: 10px;
    padding: 16px;
    margin: 10px 0;
    transition: all 0.3s ease;
}

.news-card:hover { border-left-color: #ff6b35; transform: translateX(4px); }

.news-impact-positive {
    background: #00e5ff11;
    border-left: 4px solid #00e676;
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 13px;
    color: #00e676;
}

.news-impact-negative {
    background: #ff6b3511;
    border-left: 4px solid #ff5252;
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 13px;
    color: #ff5252;
}

.news-impact-neutral {
    background: #ffeb3b11;
    border-left: 4px solid #ffeb3b;
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 13px;
    color: #ffeb3b;
}

.invest-card {
    background: linear-gradient(135deg, #0d1b2a, #1a2744);
    border: 1px solid #00e5ff33;
    border-radius: 14px;
    padding: 20px;
    margin: 8px 0;
    text-align: center;
}

.invest-amount {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #00e5ff;
}

.invest-label {
    font-size: 13px;
    color: #90caf9;
    margin-top: 4px;
}

.stButton > button {
    background: linear-gradient(135deg, #00e5ff, #0091ea);
    color: #0a0f1e;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 12px 28px;
    font-size: 15px;
    width: 100%;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff6b35, #ff3d00);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px #ff6b3540;
}

.stSlider > div > div > div { background: #00e5ff !important; }

div[data-testid="stSelectbox"] > div {
    background: #0d1b2a !important;
    border: 1px solid #1e3a5f !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
}

.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: #00e5ff;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #00e5ff, #00b0ff, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #90caf9;
    font-size: 16px;
    margin-bottom: 32px;
}

.ai-response {
    background: linear-gradient(135deg, #071a2e, #0d1f3c);
    border: 1px solid #00e5ff44;
    border-radius: 14px;
    padding: 24px;
    font-size: 15px;
    line-height: 1.8;
    color: #cfd8dc;
    white-space: pre-wrap;
}

.ticker-badge {
    display: inline-block;
    background: #00e5ff22;
    border: 1px solid #00e5ff55;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #00e5ff;
    margin: 2px;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0d1b2a;
    border-radius: 10px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    color: #90caf9;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00e5ff22, #0091ea22) !important;
    color: #00e5ff !important;
    border-radius: 8px;
}

hr { border-color: #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

def get_market_data():
    """Fetch live market indices"""
    tickers = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "GOLD": "GC=F",
        "USD/INR": "INR=X"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((curr - prev) / prev) * 100
                data[name] = {"price": curr, "change": chg}
            elif len(hist) == 1:
                curr = hist['Close'].iloc[-1]
                data[name] = {"price": curr, "change": 0.0}
        except:
            data[name] = {"price": 0, "change": 0}
    return data

def calculate_investment_plan(salary, age, risk, goals):
    """Calculate investment allocation using 50/30/20 rule"""
    needs = salary * 0.50
    wants = salary * 0.30
    savings = salary * 0.20

    emergency_fund_target = salary * 6
    emergency_monthly = min(savings * 0.3, 5000)

    invest_amount = savings - emergency_monthly

    allocations = {}
    if risk == "Conservative (Low Risk)":
        allocations = {
            "FD / Liquid Fund": 0.40,
            "PPF / NPS": 0.30,
            "Debt Mutual Funds (SIP)": 0.20,
            "Gold ETF": 0.10,
        }
    elif risk == "Moderate (Medium Risk)":
        allocations = {
            "Index Fund SIP (Nifty 50)": 0.35,
            "Balanced Mutual Funds": 0.25,
            "PPF / NPS": 0.20,
            "FD / Liquid Fund": 0.15,
            "Gold ETF": 0.05,
        }
    else:
        allocations = {
            "Direct Equity / Stocks": 0.40,
            "Small & Mid Cap SIP": 0.25,
            "Index Fund SIP": 0.20,
            "Crypto (Max 5%)": 0.05,
            "Gold ETF": 0.10,
        }

    return {
        "salary": salary,
        "needs": needs,
        "wants": wants,
        "savings": savings,
        "emergency_monthly": emergency_monthly,
        "invest_amount": invest_amount,
        "allocations": allocations,
        "emergency_fund_target": emergency_fund_target,
    }

def calculate_compounding(monthly_sip, years, annual_return_pct):
    """Calculate SIP compounding growth month by month"""
    monthly_rate = annual_return_pct / 100 / 12
    data = []
    corpus = 0
    invested = 0
    for month in range(1, years * 12 + 1):
        corpus = (corpus + monthly_sip) * (1 + monthly_rate)
        invested += monthly_sip
        if month % 12 == 0:
            data.append({
                "Year": month // 12,
                "Invested": round(invested),
                "Corpus": round(corpus),
                "Gains": round(corpus - invested)
            })
    return data

def get_world_news_with_impact(client):
    """Use Claude to generate current world financial news + market impact"""
    prompt = """You are a senior financial analyst. Generate 6 current major global financial/economic news items that are affecting markets RIGHT NOW in May 2026. 

For each news item provide:
1. A realistic headline
2. 2-sentence description
3. Market impact (POSITIVE/NEGATIVE/NEUTRAL)
4. Impact explanation on Indian markets specifically (1 sentence)
5. Affected sectors in India

Format as JSON array:
[
  {
    "headline": "...",
    "description": "...",
    "impact": "POSITIVE",
    "india_impact": "...",
    "sectors": ["Banking", "IT"]
  }
]

Make news realistic for May 2026 global context. Return ONLY the JSON array, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except:
        return []

def get_ai_investment_advice(client, plan, age, risk, goals, salary):
    """Get personalised AI investment advice from Claude"""
    prompt = f"""You are a SEBI-registered financial advisor helping a young Indian professional.

CLIENT PROFILE:
- Age: {age} years
- Monthly Salary: ₹{salary:,}
- Risk Appetite: {risk}
- Financial Goals: {', '.join(goals)}

CALCULATED PLAN:
- Monthly Needs (50%): ₹{plan['needs']:,.0f}
- Monthly Wants (30%): ₹{plan['wants']:,.0f}
- Monthly Savings (20%): ₹{plan['savings']:,.0f}
- Emergency Fund (monthly): ₹{plan['emergency_monthly']:,.0f}
- Available to Invest: ₹{plan['invest_amount']:,.0f}

Investment Allocations:
{chr(10).join([f"- {k}: ₹{plan['invest_amount']*v:,.0f}/month ({int(v*100)}%)" for k,v in plan['allocations'].items()])}

Write a personalised, warm, motivating investment advisory letter. Include:
1. A short greeting and summary of their financial health
2. Why this allocation suits their age and risk profile
3. Step-by-step action plan for this month (what to open, where to invest)
4. One key warning or thing to avoid
5. Motivating closing with 5-year projection at 12% returns
6. One line about how this discipline separates wealth builders from the rest

Be specific, practical, India-focused. Use ₹ symbols. Keep it under 400 words."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# ── Initialize Claude Client ──────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return anthropic.Anthropic()

# ── Main App ──────────────────────────────────────────────────────────────────

# Hero Section
st.markdown('<div class="hero-title">FinWise AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">AI-Powered Investment Strategy · Global Market Intelligence · Compounding Engine</div>', unsafe_allow_html=True)

# ── Live Market Ticker ────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Live Markets</p>', unsafe_allow_html=True)
with st.spinner("Fetching live market data..."):
    market = get_market_data()

cols = st.columns(len(market))
for i, (name, val) in enumerate(market.items()):
    with cols[i]:
        chg = val['change']
        price = val['price']
        delta_str = f"{chg:+.2f}%"
        if name == "USD/INR":
            st.metric(name, f"₹{price:.2f}", delta_str, delta_color="inverse")
        elif name in ["GOLD"]:
            st.metric(name, f"${price:,.0f}", delta_str)
        elif name in ["NIFTY 50", "SENSEX"]:
            st.metric(name, f"{price:,.0f}", delta_str)
        else:
            st.metric(name, f"{price:,.0f}", delta_str)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Investment Planner",
    "📰 World News & Market Impact",
    "📈 Compounding Calculator",
    "🌍 Global Trend Tracker"
])

# ═══════════════════════════════════════════════════════════
# TAB 1 — INVESTMENT PLANNER
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 💰 Personal Investment Strategy")
    st.markdown("*Enter your details below to get a personalised AI-generated investment plan*")

    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown('<p class="section-title">Your Profile</p>', unsafe_allow_html=True)
        salary = st.number_input("Monthly Salary (₹)", min_value=10000, max_value=500000,
                                  value=30000, step=1000, help="Your take-home monthly salary")
        age = st.slider("Your Age", min_value=18, max_value=60, value=23)
        risk = st.selectbox("Risk Appetite", [
            "Conservative (Low Risk)",
            "Moderate (Medium Risk)",
            "Aggressive (High Risk)"
        ])
        goals = st.multiselect("Financial Goals", [
            "Emergency Fund", "Buy a House", "Retirement",
            "Child Education", "Travel", "Car", "Business", "Wealth Creation"
        ], default=["Emergency Fund", "Wealth Creation"])

        generate = st.button("🚀 Generate My Investment Plan")

    with col2:
        if generate or 'plan' in st.session_state:
            plan = calculate_investment_plan(salary, age, risk, goals)
            st.session_state['plan'] = plan
            st.session_state['salary'] = salary
            st.session_state['age'] = age
            st.session_state['risk'] = risk
            st.session_state['goals'] = goals

            # Budget Breakdown
            st.markdown('<p class="section-title">Budget Breakdown (50/30/20 Rule)</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="invest-card">
                    <div class="invest-amount">₹{plan['needs']:,.0f}</div>
                    <div class="invest-label">🏠 Needs (50%)</div>
                    <div style="font-size:11px;color:#546e7a;margin-top:6px">Rent · Food · Bills</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="invest-card">
                    <div class="invest-amount">₹{plan['wants']:,.0f}</div>
                    <div class="invest-label">🎯 Wants (30%)</div>
                    <div style="font-size:11px;color:#546e7a;margin-top:6px">Entertainment · Shopping</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="invest-card">
                    <div class="invest-amount">₹{plan['savings']:,.0f}</div>
                    <div class="invest-label">💎 Savings (20%)</div>
                    <div style="font-size:11px;color:#546e7a;margin-top:6px">Invest · Emergency</div>
                </div>""", unsafe_allow_html=True)

            # Allocation Chart
            st.markdown('<p class="section-title" style="margin-top:20px">Investment Allocation</p>', unsafe_allow_html=True)
            labels = list(plan['allocations'].keys())
            values = [plan['invest_amount'] * v for v in plan['allocations'].values()]
            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                hole=0.55,
                marker=dict(colors=['#00e5ff','#0091ea','#00b0ff','#80d8ff','#40c4ff','#29b6f6']),
                textfont=dict(color='white', size=12),
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}/month<br>%{percent}<extra></extra>"
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),
                legend=dict(font=dict(color='#90caf9', size=11)),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                annotations=[dict(text=f"₹{plan['invest_amount']:,.0f}<br><span style='font-size:10px'>/ month</span>",
                                   x=0.5, y=0.5, font_size=16, showarrow=False,
                                   font=dict(color='#00e5ff'))]
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Allocation Breakdown Table
    if 'plan' in st.session_state:
        plan = st.session_state['plan']
        st.markdown("### 📊 Monthly Investment Breakdown")
        alloc_data = []
        for instrument, pct in plan['allocations'].items():
            amount = plan['invest_amount'] * pct
            annual = amount * 12
            alloc_data.append({
                "Investment": instrument,
                "Monthly (₹)": f"₹{amount:,.0f}",
                "Annual (₹)": f"₹{annual:,.0f}",
                "Allocation": f"{int(pct*100)}%"
            })
        df = pd.DataFrame(alloc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div style="background:#00e67622;border:1px solid #00e676;border-radius:10px;padding:16px;margin:12px 0">
        <b style="color:#00e676">🏦 Emergency Fund Goal:</b> 
        <span style="color:#e8eaf6"> Build ₹{plan['emergency_fund_target']:,.0f} (6 months salary) — 
        Contributing ₹{plan['emergency_monthly']:,.0f}/month → 
        Done in ~{math.ceil(plan['emergency_fund_target']/plan['emergency_monthly'])} months</span>
        </div>""", unsafe_allow_html=True)

        # AI Advice
        st.markdown("### 🤖 AI Financial Advisor — Your Personalised Plan")
        if st.button("✨ Get AI Investment Advice"):
            with st.spinner("Claude AI is analysing your profile..."):
                client = get_client()
                advice = get_ai_investment_advice(
                    client, plan,
                    st.session_state['age'],
                    st.session_state['risk'],
                    st.session_state['goals'],
                    st.session_state['salary']
                )
                st.markdown(f'<div class="ai-response">{advice}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TAB 2 — WORLD NEWS & MARKET IMPACT
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📰 Global News & Market Impact")
    st.markdown("*AI-analysed world events and their impact on Indian & global markets*")

    if st.button("🔄 Fetch Latest News & Analysis"):
        with st.spinner("Claude AI is analysing global markets and news..."):
            client = get_client()
            news_items = get_world_news_with_impact(client)
            st.session_state['news'] = news_items

    if 'news' in st.session_state:
        news_items = st.session_state['news']
        for item in news_items:
            impact = item.get('impact', 'NEUTRAL')
            impact_class = {
                'POSITIVE': 'news-impact-positive',
                'NEGATIVE': 'news-impact-negative',
                'NEUTRAL': 'news-impact-neutral'
            }.get(impact, 'news-impact-neutral')
            impact_emoji = {'POSITIVE': '🟢', 'NEGATIVE': '🔴', 'NEUTRAL': '🟡'}.get(impact, '🟡')
            sectors = ' '.join([f'<span class="ticker-badge">{s}</span>' for s in item.get('sectors', [])])

            st.markdown(f"""
            <div class="news-card">
                <div style="font-weight:600;font-size:16px;color:#e8eaf6;margin-bottom:8px">
                    {impact_emoji} {item['headline']}
                </div>
                <div style="color:#90caf9;font-size:14px;line-height:1.6">{item['description']}</div>
                <div class="{impact_class}">
                    🇮🇳 India Impact: {item['india_impact']}
                </div>
                <div style="margin-top:10px">{sectors}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Click 'Fetch Latest News & Analysis' to get AI-powered global market intelligence")

        st.markdown("### 📚 Key Global Indicators to Watch")
        indicators = [
            ("🇺🇸 US Federal Reserve Rate", "Current rate decisions directly impact FII flows into India. Rate cuts = more money into emerging markets like India."),
            ("🇮🇳 RBI Repo Rate", "India's central bank rate. Lower rate = cheaper loans = market rally. Higher rate = FD rates rise."),
            ("📊 US CPI Inflation", "If US inflation rises, Fed may hike rates → FII outflows from India → Nifty falls."),
            ("🛢️ Crude Oil Price", "India imports 85% of oil. Oil rise = higher inflation → RBI may hike rates → market pressure."),
            ("💵 Dollar Index (DXY)", "Strong dollar = weak rupee = FII outflows = market fall. Watch DXY weekly."),
            ("🌏 China Economic Data", "China slowdown = global commodity demand falls = good for India's import bill."),
        ]
        for title, desc in indicators:
            st.markdown(f"""
            <div class="news-card">
                <div style="font-weight:600;font-size:15px;color:#e8eaf6">{title}</div>
                <div style="color:#90caf9;font-size:13px;margin-top:6px">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TAB 3 — COMPOUNDING CALCULATOR
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📈 Compounding Growth Calculator")
    st.markdown("*See the power of consistent SIP investing over time*")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<p class="section-title">SIP Parameters</p>', unsafe_allow_html=True)
        sip_amount = st.number_input("Monthly SIP (₹)", min_value=500, max_value=100000,
                                      value=5000, step=500)
        years = st.slider("Investment Duration (Years)", min_value=1, max_value=40, value=15)
        return_rate = st.slider("Expected Annual Return (%)", min_value=6.0, max_value=20.0,
                                 value=12.0, step=0.5)

        # Summary metrics
        data = calculate_compounding(sip_amount, years, return_rate)
        if data:
            final = data[-1]
            st.markdown("---")
            st.metric("💎 Final Corpus", f"₹{final['Corpus']:,}")
            st.metric("💰 Total Invested", f"₹{final['Invested']:,}")
            st.metric("🚀 Total Gains", f"₹{final['Gains']:,}")
            wealth_mult = final['Corpus'] / final['Invested']
            st.metric("✨ Wealth Multiplier", f"{wealth_mult:.1f}x")

    with col2:
        data = calculate_compounding(sip_amount, years, return_rate)
        df = pd.DataFrame(data)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Year'], y=df['Invested'],
            name='Amount Invested',
            marker_color='#1e3a5f',
            hovertemplate="Year %{x}<br>Invested: ₹%{y:,}<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=df['Year'], y=df['Gains'],
            name='Gains / Returns',
            marker_color='#00e5ff',
            hovertemplate="Year %{x}<br>Gains: ₹%{y:,}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df['Year'], y=df['Corpus'],
            name='Total Corpus',
            line=dict(color='#ff6b35', width=3),
            mode='lines+markers',
            hovertemplate="Year %{x}<br>Corpus: ₹%{y:,}<extra></extra>"
        ))
        fig.update_layout(
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8eaf6'),
            xaxis=dict(title='Year', gridcolor='#1e3a5f', color='#90caf9'),
            yaxis=dict(title='Amount (₹)', gridcolor='#1e3a5f', color='#90caf9',
                       tickformat=',.0f'),
            legend=dict(font=dict(color='#90caf9')),
            height=420,
            margin=dict(t=20, b=40, l=60, r=20)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Milestone table
        st.markdown("### 🏆 Corpus Milestones")
        milestones = [1, 3, 5, 10, 15, 20, 25, 30]
        milestone_data = [d for d in data if d['Year'] in milestones]
        df_m = pd.DataFrame(milestone_data)
        df_m['Invested'] = df_m['Invested'].apply(lambda x: f"₹{x:,}")
        df_m['Corpus'] = df_m['Corpus'].apply(lambda x: f"₹{x:,}")
        df_m['Gains'] = df_m['Gains'].apply(lambda x: f"₹{x:,}")
        df_m.columns = ['Year', 'Invested', 'Corpus', 'Gains']
        st.dataframe(df_m, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════
# TAB 4 — GLOBAL TREND TRACKER
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 🌍 Global Trend Tracker")
    st.markdown("*Track top global stocks and indices live*")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<p class="section-title">Select Asset</p>', unsafe_allow_html=True)
        asset_options = {
            "Nifty 50 (India)": "^NSEI",
            "Sensex (India)": "^BSESN",
            "S&P 500 (USA)": "^GSPC",
            "NASDAQ (USA)": "^IXIC",
            "Dow Jones (USA)": "^DJI",
            "Apple (AAPL)": "AAPL",
            "Microsoft (MSFT)": "MSFT",
            "Reliance Industries": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS",
            "Infosys": "INFY.NS",
            "Gold": "GC=F",
            "Crude Oil": "CL=F",
        }
        selected = st.selectbox("Choose Asset", list(asset_options.keys()))
        period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
        show_chart = st.button("📊 Load Chart")

    with col2:
        if show_chart:
            ticker_sym = asset_options[selected]
            with st.spinner(f"Loading {selected}..."):
                try:
                    t = yf.Ticker(ticker_sym)
                    hist = t.history(period=period)
                    if not hist.empty:
                        start_price = hist['Close'].iloc[0]
                        end_price = hist['Close'].iloc[-1]
                        total_return = ((end_price - start_price) / start_price) * 100
                        color = '#00e676' if total_return >= 0 else '#ff5252'

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=hist.index, y=hist['Close'],
                            fill='tozeroy',
                            fillcolor=f'{"#00e67611" if total_return >= 0 else "#ff525211"}',
                            line=dict(color=color, width=2),
                            name=selected,
                            hovertemplate="%{x|%d %b %Y}<br>Price: %{y:,.2f}<extra></extra>"
                        ))
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e8eaf6'),
                            xaxis=dict(gridcolor='#1e3a5f', color='#90caf9'),
                            yaxis=dict(gridcolor='#1e3a5f', color='#90caf9', tickformat=',.2f'),
                            height=350,
                            margin=dict(t=20, b=40, l=60, r=20),
                            title=dict(
                                text=f"{selected} — {total_return:+.1f}% ({period})",
                                font=dict(color=color, size=16)
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Current Price", f"{end_price:,.2f}")
                        c2.metric("Period Return", f"{total_return:+.2f}%")
                        c3.metric("52W High", f"{hist['High'].max():,.2f}")
                except Exception as e:
                    st.error(f"Could not load data for {selected}. Try another asset.")

    # Global Trends Education
    st.markdown("---")
    st.markdown("### 📚 How Global Trends Affect Indian Markets")
    trends = [
        ("🇺🇸 US Fed Rate Decision", "NEGATIVE", "Rate hike → FII sell India stocks → Nifty falls 1–3%"),
        ("🛢️ Oil Price Spike", "NEGATIVE", "India imports 85% oil → inflation rises → RBI may hike → market pressure"),
        ("💵 Dollar Strengthens", "NEGATIVE", "FII outflows → Rupee weakens → import inflation → market falls"),
        ("🇨🇳 China Slowdown", "MIXED", "Less competition for India + global demand falls = mixed impact"),
        ("🌧️ Good Monsoon Forecast", "POSITIVE", "Rural demand rises → FMCG, agri stocks rally → Sensex up"),
        ("🏦 RBI Rate Cut", "POSITIVE", "Cheaper loans → more spending → banking, real estate rally"),
        ("📉 US Recession Fear", "NEGATIVE", "Global risk-off → FII sell emerging markets → India falls"),
        ("🤖 AI/Tech Boom", "POSITIVE", "India IT sector rallies → TCS, Infosys, Wipro outperform"),
    ]
    col1, col2 = st.columns(2)
    for i, (event, impact, effect) in enumerate(trends):
        col = col1 if i % 2 == 0 else col2
        impact_color = '#00e676' if impact == 'POSITIVE' else '#ff5252' if impact == 'NEGATIVE' else '#ffeb3b'
        with col:
            st.markdown(f"""
            <div class="news-card">
                <div style="font-weight:600;color:#e8eaf6">{event}</div>
                <div style="color:{impact_color};font-size:12px;margin:4px 0">● {impact}</div>
                <div style="color:#90caf9;font-size:13px">{effect}</div>
            </div>""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#546e7a;font-size:12px;font-family:'Space Mono',monospace">
    FinWise AI · Built with Python + Streamlit + Claude API · For educational purposes only<br>
    Not SEBI-registered financial advice · Always consult a certified advisor
</div>
""", unsafe_allow_html=True)
