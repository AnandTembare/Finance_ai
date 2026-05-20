# FinWise India

FinWise India is a futuristic Streamlit dashboard for Indian personal finance planning. The app first asks for income, expenses, savings, age, dependents, risk comfort, and priority. It then builds an interactive dashboard with cashflow analytics, profile scoring, investment split, asset-buying timelines, and long-term wealth projections.

## Features

- First-screen investor questionnaire.
- Paycent-inspired dark dashboard UI with glass cards, neon accents, and responsive layout.
- Clickable dashboard views: Overview, Investment Plan, Asset Planner, and Analytics.
- Personalized profile category such as Foundation Builder, Balanced Investor, Growth Investor, or Capital Protector.
- Monthly investment allocation based on savings rate, emergency cover, age, dependents, and risk comfort.
- SIP compounding table for 1, 3, 5, 10, 15, and 20-year projections.
- Reinvested-compounding mode versus non-reinvested profit mode.
- Free-form asset planner for home, car, phone, gold, or any custom goal.
- Affordability warnings using practical Indian rules such as car 20/4/10 and EMI pressure checks.
- Income target suggestions when a goal is too expensive for the current salary.
- Statistical dashboard with savings rate, expense ratio, emergency months, medical buffer gap, EMI pressure, wealth projection, and allocation charts.
- Live Indian market strip for NIFTY 50, SENSEX, NIFTY BANK, GOLD, and USD/INR.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy On Streamlit Community Cloud

1. Push this folder to GitHub.
2. Open Streamlit Community Cloud.
3. Select this repository.
4. Set the main file path to `app.py`.
5. Deploy.

## Project Structure

```text
app.py
requirements.txt
.streamlit/config.toml
README.md
```

## Notes

The calculations are projection models for a portfolio project. Users can change their answers and immediately see updated charts, goals, and investment splits.
