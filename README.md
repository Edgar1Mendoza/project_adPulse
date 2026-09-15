# adPulse

Marketing data pipeline (bronze → silver → gold) that unifies campaign performance from Google Ads, Meta Ads, Email Campaigns, and CRM.

## Setup

1. `python3 -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and edit `DOWNLOADS_SOURCE_DIR` with the local path to your source files

## Data caveats

- **`spend_eur` does not mean the same thing across sources.** For `google` and `meta` it's real media spend (what was paid to show the ad). For `email` it's agency management cost (design, copy), not the cost of sending the email itself. **Never compare `revenue_eur / spend_eur` across sources without filtering by `source` first** — mixing them produces a false ROI conclusion.
- **`date` grain is not the same across sources.** For `google` and `meta` it's daily. For `email` it's weekly (`week_start`) — one row represents the whole week, not a specific day. Not valid for day-of-week analysis.
- **`crm_ventas` is not included in `unified_campaigns`.** It's a transactional table (one row per sale), with a different grain and purpose than campaign performance tables.