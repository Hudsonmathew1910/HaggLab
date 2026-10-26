# Sample datasets (fictional)

One default knowledge source per project. These are loaded into Pinecone (one namespace per project) and,
for tables, into pandas for calculations. Visitors never upload files; the Try it pages use these.

**Everything here is made up**: companies (Northwind Supplies, Brightcart, Green Field Sports Arena,
CareFirst Family Clinic), products, customers and numbers. No personal data. Customer references are codes like `C1234`.

Recreate the CSV/Excel files exactly with: `python datasets/generate.py` (fixed random seed).
The `.md` documents are written by hand.

| Project | Files | What it is | Size |
|---|---|---|---|
| DocuMind | `documind/staff_handbook.md` | Staff handbook of a fictional company, 17 sections | ~2,000 words |
| InsightDesk | `insightdesk/retail_sales.csv` | Sales lines, Apr 2025 – Sep 2026, 4 stores + online | ~17,600 rows |
| ShopAssist | `shopassist/products.csv` | Product catalog with descriptions, features, stock | 132 products |
| BookIt | `bookit/venue_rules.md`, `bookit/bookings.csv` | Venue rules and prices; bookings for the last 120 days and next 14 | ~4,900 rows |
| SupportFlow | `supportflow/support_policy.md`, `supportflow/tickets.csv` | Support policy; labelled customer messages with agent replies | 800 tickets |
| ForecastBoard | `forecastboard/weekly_sales.csv` | Weekly units by category, Jan 2024 – Sep 2026, promo and holiday flags | 864 rows |
| VoiceDesk | `voicedesk/clinic_faq.md`, `voicedesk/services.csv` | Clinic FAQ (practical questions only, no medical advice); services and fees | 22 services |
| PageMind | `pagemind/*.md` | Three sample web pages (news article, blog post, press release) | 3 pages |
| DeskPilot | `deskpilot/office_sops.md` | Office procedures with file-naming rules and safety rules | 7 SOPs |
| ReportBot | `reportbot/cafe_sales.xlsx` | Sheets: Transactions (daily, 3 outlets, Oct 2025 – Sep 2026), Targets, Expenses | ~15,300 rows |

## Columns

**insightdesk/retail_sales.csv**: `date, order_id, store, region, channel, category, product, sku, quantity, unit_price, discount_pct, revenue, unit_cost, cost, profit, payment_method`. `unit_cost` is what the shop paid per item; `profit = revenue - cost`. A few thin-margin products (1TB Portable SSD, Kids Volume-Safe Headphones, Adjustable Dumbbell Pair) lose money on discounted sales, and Thermal Gloves are cleared at 40% off in March to May, below cost.
Built-in patterns: November–December peak, quiet February, busier weekends, about 12% yearly growth, four 15%-off promotion weeks, winter apparel and January fitness spikes.

**shopassist/products.csv**: `product_id, name, category, subcategory, brand, price_usd, colours, description, features, stock_qty, availability, rating, review_count`.

**bookit/bookings.csv**: `booking_id, date, start_time, end_time, resource, customer_ref, channel, status, price_usd, equipment_rental`. Status: Completed, Cancelled, No-show (past) or Confirmed (future). Prices match `venue_rules.md`.

**supportflow/tickets.csv**: `ticket_id, created_at, channel, message, topic, urgency, agent_reply, first_reply_minutes, status`. Topics and urgency follow `support_policy.md`.

**forecastboard/weekly_sales.csv**: `week_start, category, units_sold, avg_price, promotion, holiday_week, revenue`.

**voicedesk/services.csv**: `service, category, duration_minutes, fee, preparation, how_to_book`.

**reportbot/cafe_sales.xlsx**: Transactions `date, outlet, item, category, quantity, unit_price, revenue, payment_method, order_type`; Targets `month, outlet, revenue_target`; Expenses `month, outlet, expense_type, amount`.
