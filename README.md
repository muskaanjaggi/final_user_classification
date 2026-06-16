# 🛡️ User Engagement Segmentation

A rule-based classification system that segments users into 8 distinct engagement categories, built from business logic originally encoded in Excel formulas. Includes a Streamlit web app for single-profile analysis and batch classification.

---

## 🚀 Live App

Deploy on [Streamlit Cloud](https://streamlit.io/cloud) by connecting this repo and pointing it to `app.py`.

---

## 📁 Repository Structure

```
├── app.py                  # Streamlit web UI
├── classifier_logic.py     # Core classification engine
├── requirements.txt        # Python dependencies
└── README.md
```

> All three files must be in the **same directory** for the app to work.

---

## 🗂️ User Categories

The engine classifies every user into one of 8 categories:

| Category | Icon | Description |
|---|---|---|
| **Power User** | 🚀 | High-value, highly engaged, long-tenured. Top retention & upsell priority. |
| **Active User** | ✅ | High-value with healthy activity, but not yet enough signals for Power. |
| **Normal User** | 🙂 | New account already showing engagement. Good nurture candidate. |
| **New User** | 🌱 | Recently signed up (≤90 days), no engagement yet. Early nurture priority. |
| **Dormant User** | 💤 | Installed, low value, no engagement. Re-activation candidate. |
| **Repitch User** | 🔁 | Uninstalled but has prior value and engagement. Strong win-back target. |
| **Lapsed User** | 📉 | Uninstalled with prior value but zero engagement. Lower win-back priority. |
| **Inactive User** | 🚫 | Uninstalled, never had any policy/premium value. |

---

## 🧠 Classification Logic

The decision tree uses 10 input features:

| Feature | Type | Values |
|---|---|---|
| `uninstalled` | categorical | `'uninstalled'` / `'na'` |
| `active_policies` | numeric | number of active policies owned |
| `annual_premium` | numeric | total annual premium (₹) |
| `bbps_transactions` | numeric | BBPS transaction amount (₹) |
| `phc_transactions` | numeric | PHC transaction amount (₹) |
| `lead` | categorical | `'lead'` / `'na'` |
| `cpro` | categorical | `'did cpro'` / `'na'` |
| `ioc` | categorical | `'used ioc'` / `'na'` |
| `partner_code` | text | partner code string or blank |
| `signup` | date | account signup date |

### Decision Tree

```
Installed?
├── NO (uninstalled)
│   ├── Has active_policies > 0 OR annual_premium > 0?
│   │   ├── YES + any engagement signal    →  Repitch User
│   │   └── YES + no engagement            →  Lapsed User
│   └── NO                                 →  Inactive User
│
└── YES (installed)
    ├── High value? (active_policies > 3 OR annual_premium > ₹1,00,000)
    │   ├── Account > 90 days AND ≥ 2 of 6 signals*   →  Power User
    │   └── Otherwise                                   →  Active User
    │
    └── Low value (active_policies ≤ 3 AND annual_premium ≤ ₹1,00,000)
        ├── Has any engagement signal?
        │   └── YES                         →  Normal User
        └── NO engagement
            ├── Signup ≤ 90 days            →  New User
            └── Signup > 90 days            →  Dormant User
```

*\* **Power User engagement signals** (need ≥ 2 of these 6):*
1. Partner code assigned
2. Lead generated
3. CoverPro used (CPRO)
4. Insurance on Cards used (IOC)
5. BBPS transactions > 0
6. PHC transactions > 0

---

## 🖥️ Using the App

### Single Profile Tab
Fill in a user's metrics and click **Analyze Profile** to instantly classify them. The result card shows the category, color-coded label, and a plain-English description.

### Batch Upload Tab
Upload a CSV or Excel file containing user data. The app classifies every row and lets you download the results as a CSV. A distribution chart shows the category breakdown across your dataset.

---

## ⚙️ Running Locally

**Prerequisites:** Python 3.8+

```bash
# 1. Clone the repo
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open at https://finaluserclassification-sybdaymh5gvkggejdmohtx.streamlit.app/ 

---

## 📦 Batch File Format

Your CSV or Excel file must include these columns (column names are case-sensitive):

```
uninstalled, active_policies, annual_premium, bbps_transactions,
phc_transactions, lead, cpro, ioc, partner_code, signup
```

Blank / NaN values are treated as `0` or `'na'` automatically. The output file will be identical to the input with a `user_category` column appended.

---

## 📦 Dependencies

```
streamlit>=1.30
pandas>=2.0
openpyxl>=3.1
```

---

## 🗺️ Roadmap

- [ ] Add confidence scores alongside category labels
- [ ] Time-series view to track user category migration over months
- [ ] API endpoint for real-time classification
- [ ] Alerting for users approaching Power User threshold
