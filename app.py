import streamlit as st
import yfinance as yf
import math
import plotly.graph_objects as go
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
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

/* ── Root Variables ─────────────────────────── */
:root {
    --bg-void:      #080a08;
    --bg-deep:      #0d0f0d;
    --bg-card:      #111411;
    --bg-surface:   #161a16;
    --bg-hover:     #1c221c;

    --ember-1:      #ff2a2a;
    --ember-2:      #e63c00;
    --ember-3:      #c43a00;
    --ember-glow:   #ff4500;
    --gold:         #d4a843;
    --gold-dim:     #a07820;
    --cream:        #f0e8d8;
    --ash:          #9e9e8e;
    --carbon:       #3a3a34;

    --success:      #4caf50;
    --danger:       #ff2a2a;
    --warning:      #d4a843;

    --radius:       6px;
    --radius-lg:    12px;
}

/* ── Reset & Base ───────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--bg-void) !important;
    color: var(--cream) !important;
}

.main { background-color: var(--bg-void) !important; }
.block-container { padding-top: 2rem !important; }

/* ── Scrollbar ──────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--ember-3); border-radius: 2px; }

/* ── Typography ─────────────────────────────── */
h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: var(--cream) !important;
    letter-spacing: 2px;
}

/* ── Hero Header ────────────────────────────── */
.hero-wrap {
    position: relative;
    padding: 32px 0 24px 0;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--carbon);
}

.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 5px;
    color: var(--ember-1);
    text-transform: uppercase;
    margin-bottom: 6px;
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 64px;
    line-height: 0.9;
    margin: 0;
    background: linear-gradient(135deg, var(--cream) 0%, var(--cream) 40%, var(--gold) 70%, var(--ember-1) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--ash);
    letter-spacing: 2px;
    margin-top: 10px;
    text-transform: uppercase;
}

.hero-rule {
    display: inline-block;
    width: 48px;
    height: 2px;
    background: var(--ember-glow);
    margin-right: 10px;
    vertical-align: middle;
}

/* ── Ticker Strip ───────────────────────────── */
.ticker-strip {
    background: var(--bg-deep);
    border: 1px solid var(--carbon);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin-bottom: 20px;
}

/* ── Metric Cards ───────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--carbon) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    position: relative;
    overflow: hidden;
}

[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--ember-glow);
}

[data-testid="metric-container"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--ash) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--cream) !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
}

/* ── Sidebar ────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--bg-deep) !important;
    border-right: 1px solid var(--carbon) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSlider label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--ash) !important;
}

/* ── Selectbox & Inputs ─────────────────────── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--bg-surface) !important;
    border: 1px solid var(--carbon) !important;
    color: var(--cream) !important;
    border-radius: var(--radius) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: var(--ember-glow) !important;
    box-shadow: 0 0 0 1px var(--ember-3) !important;
}

/* ── Slider ─────────────────────────────────── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--ember-1) !important;
    border-color: var(--ember-1) !important;
}

.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background: var(--ember-1) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Buttons ────────────────────────────────── */
.stButton > button {
    background: var(--ember-glow) !important;
    color: var(--bg-void) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 12px 24px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: var(--gold) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(212, 168, 67, 0.3) !important;
}

/* ── Tabs ───────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--carbon) !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--ash) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    padding: 8px 20px !important;
}

[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    background: var(--ember-glow) !important;
    color: var(--bg-void) !important;
}

/* ── Divider ────────────────────────────────── */
hr { border-color: var(--carbon) !important; margin: 24px 0 !important; }

/* ── Info / Alert ───────────────────────────── */
.stAlert {
    background: var(--bg-card) !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: var(--radius) !important;
    color: var(--cream) !important;
}

/* ── Dataframe ──────────────────────────────── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--carbon) !important;
    border-radius: var(--radius) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-surface) !important;
    color: var(--ash) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

[data-testid="stDataFrame"] td {
    background: var(--bg-card) !important;
    color: var(--cream) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
}

/* ── Custom Cards ───────────────────────────── */
.alloc-card {
    background: var(--bg-card);
    border: 1px solid var(--carbon);
    border-radius: var(--radius-lg);
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.alloc-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--ember-3), var(--gold));
}

.alloc-card:hover { border-color: var(--ember-3); }

.alloc-amount {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    letter-spacing: 2px;
    background: linear-gradient(135deg, var(--cream), var(--gold));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.alloc-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--ash);
    margin-top: 6px;
}

/* ── Section Labels ─────────────────────────── */
.sec-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 4px;
    color: var(--ember-1);
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sec-label::before {
    content: '';
    display: inline-block;
    width: 24px;
    height: 1px;
    background: var(--ember-1);
}

/* ── Number Input Label ─────────────────────── */
.stNumberInput label, .stSelectbox label, .stSlider label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--ash) !important;
}

</style>
""", unsafe_allow_html=True)

# ── Core Business Logic ───────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_market_data() -> Dict[str, Dict[str, float]]:
    tickers = {
        "TADAWUL": "^TASI.SR",
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
    needs, wants, savings = income * 0.50, income * 0.30, income * 0.20
    emergency_target = income * 6
    emergency_monthly = min(savings * 0.3, income * 0.1)
    invest_amount = savings - emergency_monthly

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
    return data


# ── Plotly Layout Base ────────────────────────────────────────────────────────

CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='IBM Plex Mono', color='#9e9e8e', size=11),
    margin=dict(t=20, b=40, l=60, r=20),
)

GRID_STYLE = dict(
    gridcolor='#1c221c',
    zerolinecolor='#3a3a34',
    linecolor='#3a3a34',
)

# Ember/gold palette
EMBER_PALETTE = ['#ff4500', '#d4a843', '#c43a00', '#a07820', '#e63c00', '#7a2900']

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⬡ Enterprise Investment Intelligence</div>
    <div class="hero-title">FINWISE<br>ANALYTICS</div>
    <div class="hero-sub">
        <span class="hero-rule"></span>
        GCC Market Intelligence · Portfolio Strategy · Wealth Engineering
    </div>
</div>
""", unsafe_allow_html=True)

# ── Region Selector ───────────────────────────────────────────────────────────
currency_col, _, _, _, _ = st.columns([1,1,1,1,1])
with currency_col:
    currency_selector = st.selectbox("Region", ["UAE (AED د.إ)", "India (INR ₹)"], label_visibility="collapsed")
    symbol = "AED " if "UAE" in currency_selector else "₹ "
    default_salary = 15000 if "UAE" in currency_selector else 50000

# ── Market Ticker ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Live Markets</div>', unsafe_allow_html=True)

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

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["STRATEGY PLANNER", "COMPOUNDING ENGINE", "GLOBAL TRENDS"])

# ── TAB 1: Strategy ───────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown('<div class="sec-label">Client Profile</div>', unsafe_allow_html=True)
        income = st.number_input(
            f"Monthly Income ({symbol})",
            min_value=1000, max_value=1_000_000, value=default_salary, step=1000
        )
        risk = st.selectbox(
            "Risk Appetite",
            ["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"]
        )
        st.button("CALCULATE STRATEGY")

    plan = calculate_investment_plan(income, risk)

    with col2:
        st.markdown('<div class="sec-label">Budget Allocation — 50 / 30 / 20 Rule</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
            <div class="alloc-card">
                <div class="alloc-amount">{symbol}{plan['needs']:,.0f}</div>
                <div class="alloc-label">Needs — 50%</div>
            </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
            <div class="alloc-card">
                <div class="alloc-amount">{symbol}{plan['wants']:,.0f}</div>
                <div class="alloc-label">Wants — 30%</div>
            </div>""", unsafe_allow_html=True)
        c3.markdown(f"""
            <div class="alloc-card">
                <div class="alloc-amount">{symbol}{plan['savings']:,.0f}</div>
                <div class="alloc-label">Savings — 20%</div>
            </div>""", unsafe_allow_html=True)

        # Donut Chart
        fig_pie = go.Figure(go.Pie(
            labels=list(plan['allocations'].keys()),
            values=[plan['invest_amount'] * v for v in plan['allocations'].values()],
            hole=0.60,
            marker=dict(
                colors=EMBER_PALETTE[:len(plan['allocations'])],
                line=dict(color='#080a08', width=2)
            ),
            textfont=dict(family='IBM Plex Mono', size=11, color='#f0e8d8'),
        ))
        fig_pie.update_layout(
            **CHART_BASE,
            height=260,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(
                font=dict(family='IBM Plex Mono', size=10, color='#9e9e8e'),
                bgcolor='rgba(0,0,0,0)',
                orientation='v'
            ),
            annotations=[dict(
                text=f"<b>{symbol}{plan['invest_amount']:,.0f}</b><br>Monthly",
                x=0.5, y=0.5, font_size=13, showarrow=False,
                font=dict(family='IBM Plex Mono', color='#f0e8d8')
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    # Allocation Table
    st.markdown('<div class="sec-label">Monthly Portfolio Breakdown</div>', unsafe_allow_html=True)
    alloc_data = [
        {
            "Asset Class": k,
            f"Monthly Allocation ({symbol})": f"{symbol}{plan['invest_amount'] * v:,.0f}",
            "Weight": f"{int(v * 100)}%",
        }
        for k, v in plan['allocations'].items()
    ]
    st.dataframe(pd.DataFrame(alloc_data), use_container_width=True, hide_index=True)

    months_to_target = math.ceil(plan['target'] / plan['emergency_monthly']) if plan['emergency_monthly'] > 0 else 0
    st.info(
        f"**Liquidity Target:** Build {symbol}{plan['target']:,.0f} (6-month runway). "
        f"Contributing {symbol}{plan['emergency_monthly']:,.0f}/mo reaches this in ~{months_to_target} months."
    )

# ── TAB 2: Compounding ────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="sec-label">Projection Parameters</div>', unsafe_allow_html=True)
        sip_amount = st.number_input(
            f"Monthly Investment ({symbol})",
            min_value=500, value=int(plan['invest_amount']), step=500
        )
        years = st.slider("Duration (Years)", 1, 40, 15)
        return_rate = st.slider("Expected Annual Return (%)", 4.0, 20.0, 10.0, 0.5)

        comp_data = calculate_compounding(sip_amount, years, return_rate)
        final = comp_data[-1]
        st.markdown("---")
        st.metric("Projected Corpus", f"{symbol}{final['Corpus']:,}")
        st.metric("Capital Deployed", f"{symbol}{final['Invested']:,}")
        gains_pct = ((final['Corpus'] - final['Invested']) / final['Invested'] * 100) if final['Invested'] else 0
        st.metric("Total Gains", f"{symbol}{final['Gains']:,}", f"+{gains_pct:.1f}%")

    with col2:
        df = pd.DataFrame(comp_data)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=df['Year'], y=df['Invested'],
            name='Capital Deployed',
            marker_color='#2a1a0e',
            marker_line=dict(width=0),
        ))
        fig_comp.add_trace(go.Bar(
            x=df['Year'], y=df['Gains'],
            name='Wealth Generated',
            marker=dict(
                color=df['Year'],
                colorscale=[[0, '#7a2900'], [0.5, '#d4a843'], [1, '#ff4500']],
                line=dict(width=0)
            ),
        ))
        fig_comp.add_trace(go.Scatter(
            x=df['Year'], y=df['Corpus'],
            name='Total Portfolio Value',
            line=dict(color='#f0e8d8', width=2, dash='dot'),
            mode='lines',
        ))
        fig_comp.update_layout(
            **CHART_BASE,
            barmode='stack',
            height=420,
            xaxis=dict(title='Year', **GRID_STYLE),
            yaxis=dict(title=f'Value ({symbol})', **GRID_STYLE),
            legend=dict(
                font=dict(family='IBM Plex Mono', size=10, color='#9e9e8e'),
                bgcolor='rgba(0,0,0,0)',
                orientation='h',
                yanchor='bottom', y=1.02, xanchor='left', x=0
            )
        )
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

# ── TAB 3: Global Trends ──────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns([1, 2.2])

    with col1:
        st.markdown('<div class="sec-label">Asset Tracker</div>', unsafe_allow_html=True)
        assets = {
            "Saudi Tadawul": "^TASI.SR",
            "S&P 500": "^GSPC",
            "Nifty 50": "^NSEI",
            "Gold": "GC=F",
            "Crude Oil": "CL=F",
            "Bitcoin": "BTC-USD"
        }
        selected = st.selectbox("Select Asset", list(assets.keys()))
        period = st.selectbox("Historical Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"])
        show = st.button("RENDER CHART")

    with col2:
        if show:
            hist = yf.Ticker(assets[selected]).history(period=period)
            if not hist.empty:
                ret = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                line_color = '#ff4500' if ret >= 0 else '#d4a843'
                fill_color = 'rgba(255,69,0,0.08)' if ret >= 0 else 'rgba(212,168,67,0.08)'

                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    fill='tozeroy',
                    fillcolor=fill_color,
                    line=dict(color=line_color, width=2),
                    mode='lines',
                    name=selected
                ))
                # Moving average overlay
                ma = hist['Close'].rolling(window=20).mean()
                fig_trend.add_trace(go.Scatter(
                    x=hist.index,
                    y=ma,
                    line=dict(color='#d4a843', width=1, dash='dot'),
                    mode='lines',
                    name='MA(20)',
                    opacity=0.8
                ))
                fig_trend.update_layout(
                    **CHART_BASE,
                    height=380,
                    title=dict(
                        text=f"<b>{selected}</b>  <span style='color:{'#ff4500' if ret>=0 else '#d4a843'}'>{ret:+.2f}%</span>",
                        font=dict(family='Bebas Neue', size=22, color='#f0e8d8'),
                        x=0
                    ),
                    xaxis=dict(**GRID_STYLE, showgrid=True),
                    yaxis=dict(**GRID_STYLE, showgrid=True),
                    legend=dict(
                        font=dict(family='IBM Plex Mono', size=10, color='#9e9e8e'),
                        bgcolor='rgba(0,0,0,0)',
                    )
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("""
            <div style="
                height:380px;
                background:var(--bg-card);
                border:1px dashed #3a3a34;
                border-radius:6px;
                display:flex;
                align-items:center;
                justify-content:center;
                flex-direction:column;
                gap:8px;
            ">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:3px;color:#3a3a34;text-transform:uppercase;">
                    SELECT AN ASSET AND RENDER
                </div>
            </div>
            """, unsafe_allow_html=True)
