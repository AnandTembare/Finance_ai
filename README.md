# FinWise India

FinWise India is a polished Streamlit app for India-focused personal finance education. It demonstrates portfolio planning, EMI-vs-SIP comparisons, simplified Indian capital-gains tax estimates, Section 80C / ELSS planning, live market snapshots, and configurable broker links.

> This is an educational portfolio project. It is not personalized investment advice, research advice, tax advice, or a SEBI-registered advisory service.

## Highlights

- India-localized rupee formatting using lakh/crore style grouping.
- Configurable car-loan, equity-return, debt-return, FD-return, and tax assumptions.
- Simplified Section 112A equity LTCG estimate using a 12.5% default rate and ₹1.25 lakh annual exemption.
- Section 80C / ELSS helper with old-tax-regime context and lock-in reminder.
- SEBI-style risk disclosures and affiliate-link disclosure.
- Live NIFTY 50, SENSEX, NIFTY BANK, S&P 500, GOLD, and USD/INR snapshot via Yahoo Finance.
- Responsive dark UI with keyboard-focus states, clear labels, chart captions, and high contrast.
- Broker links configurable from Streamlit secrets or environment variables.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configure referral links

Create `.streamlit/secrets.toml` locally, or add the same keys in Streamlit Community Cloud secrets:

```toml
ZERODHA_URL = "https://your-zerodha-link"
GROWW_URL = "https://your-groww-link"
UPSTOX_URL = "https://your-upstox-link"
```

If these are missing, the app falls back to each platform's public account-opening page.

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub.
2. Open Streamlit Community Cloud and choose the repository.
3. Set the main file path to `app.py`.
4. Add referral links under app secrets if needed.
5. Deploy.

## India-specific assumptions

The app intentionally keeps assumptions editable because actual outcomes depend on lender, credit profile, taxation status, fund category, holding period, and investor goals.

- Car-loan default is set to 8.75% as a realistic planning midpoint around recent Indian bank auto-loan starting rates.
- Equity SIP return default is 11.0%, with reminders that past returns do not guarantee future returns.
- Eligible listed equity / equity-oriented fund LTCG is modeled at 12.5% above the remaining ₹1.25 lakh annual exemption for transfers on or after 23 July 2024.
- ELSS is shown as a Section 80C planning input with a 3-year lock-in reminder and old-tax-regime context.

## Sources

- [SEBI caution on registered investment advisers and research analysts](https://www.sebi.gov.in/media/press-releases/jun-2016/sebi-cautions-public-to-deal-with-only-sebi-registered-investment-advisers-and-research-analysts_32627.html)
- [SEBI investor caution materials](https://investor.sebi.gov.in/cautiontoinvestor.html)
- [Income-tax Act Section 112A](https://www.incometaxindia.gov.in/w/section-112a-59)
- [PIB: Budget 2024 capital gains update](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2035596)

## Important disclaimer

Mutual fund and securities market investments are subject to market risks. Read all scheme and related documents carefully before investing. The tax calculations are simplified and should be checked with a qualified tax professional before making investment or filing decisions.
