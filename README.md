# FinWise AI — Investment Strategy & Market Intelligence App
## Built by Anand Tembare | Python + Streamlit + Claude API

---

## STEP 1 — Install Python
1. Go to python.org → Download Python 3.11+
2. During install → CHECK "Add Python to PATH"
3. Open Command Prompt → type: python --version
   Should show: Python 3.11.x ✅

---

## STEP 2 — Install VS Code
1. Go to code.visualstudio.com → Download
2. Install with all default settings
3. Open VS Code
4. Install Extensions (left sidebar → Extensions icon):
   - Python (by Microsoft)
   - Pylance
   - Python Indent

---

## STEP 3 — Open Project in VS Code
1. Open VS Code
2. File → Open Folder → Select the "finance_app" folder
3. You will see all files in left sidebar

---

## STEP 4 — Open Terminal in VS Code
Press: Ctrl + ` (backtick key — top left of keyboard)
A terminal opens at bottom of VS Code

---

## STEP 5 — Install Dependencies
In the VS Code terminal, type these one by one:

```
pip install streamlit
pip install anthropic
pip install yfinance
pip install plotly
pip install pandas
pip install requests
```

OR install all at once:
```
pip install -r requirements.txt
```

---

## STEP 6 — Get Your Anthropic API Key
1. Go to console.anthropic.com
2. Sign up / Login
3. Click "API Keys" → "Create Key"
4. Copy the key (starts with sk-ant-...)

---

## STEP 7 — Add Your API Key
In VS Code, open the file: .streamlit/secrets.toml
Replace "your-anthropic-api-key-here" with your actual key:

```
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxxx"
```

ALSO — Set it as environment variable in terminal:
Windows:  set ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
Mac/Linux: export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

---

## STEP 8 — Run the App
In VS Code terminal:
```
streamlit run app.py
```

Browser opens automatically at: http://localhost:8501 ✅

---

## STEP 9 — Deploy on Streamlit Cloud (FREE)
1. Upload your code to GitHub (create free account at github.com)
   - Create new repository called "finwise-ai"
   - Upload all files EXCEPT secrets.toml
2. Go to share.streamlit.io → Sign in with GitHub
3. Click "New App" → Select your repository → Select app.py
4. Under "Advanced Settings" → Secrets → Add:
   ANTHROPIC_API_KEY = "your-key-here"
5. Click Deploy → Get public URL!
6. Add URL to your resume immediately ✅

---

## APP FEATURES
- Live market data: Nifty, Sensex, S&P 500, NASDAQ, Gold, USD/INR
- Investment Planner: 50/30/20 budget rule + allocation chart
- AI Financial Advisor: Claude API generates personalised advice
- World News: AI-analysed global events + India market impact
- Compounding Calculator: SIP growth with milestone table
- Global Trend Tracker: Live charts for 13 assets

---

## RESUME BULLET POINTS (copy these)
• Built FinWise AI — an end-to-end investment analytics web app using Python,
  Streamlit and Claude API that generates personalised investment plans based on
  salary and risk profile using the 50/30/20 rule, tracks live global market data
  (Nifty, S&P 500, Gold, USD/INR), delivers AI-powered financial news impact
  analysis, and visualises SIP compounding growth — deployed live on Streamlit Cloud.

---

## INTERVIEW TALKING POINTS
Q: Tell me about your projects
A: "I built FinWise AI — a personal investment advisor. The user enters their
   salary and risk appetite. The app calculates their budget split using the
   50/30/20 rule, recommends investment allocations across SIPs, FDs and equity,
   and Claude API generates a personalised financial plan. It also tracks live
   market data — Nifty, S&P 500, Gold — and analyses how global news like Fed
   rate decisions and oil price changes affect Indian markets. I deployed it live
   on Streamlit Cloud. This project directly applies the kind of financial data
   analysis Morningstar does at scale."

---

## TROUBLESHOOTING
Error: "streamlit not found"    → Run: pip install streamlit
Error: "anthropic not found"    → Run: pip install anthropic
Error: "API key invalid"        → Check your key in secrets.toml
Port already in use             → Run: streamlit run app.py --server.port 8502
yfinance data not loading       → Check internet connection
