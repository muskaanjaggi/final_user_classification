"""
app.py
======
CoverSure - AI-Powered Risk & User Engagement Segmentation Dashboard

A Streamlit front-end for classifier_logic.py.

Run locally:
    streamlit run app.py

Deploy:
    Push this repo (app.py, classifier_logic.py, requirements.txt) to GitHub
    and connect it on streamlit.io/cloud — no extra config needed.
"""

from datetime import date

import pandas as pd
import streamlit as st

from classifier_logic import CATEGORY_INFO, classify_dataframe, classify_user

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CoverSure | User Segmentation",
    page_icon="🛡️",
    layout="wide",
)

# ─── Custom Dark Theme CSS ─────────────────────────────────────────────────────

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b0f17;
            color: #e6edf3;
        }

        /* Header */
        .cs-title {
            font-size: 46px;
            font-weight: 800;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 0px;
        }
        .cs-subtitle {
            color: #8b949e;
            font-size: 17px;
            margin-top: 6px;
            margin-bottom: 18px;
        }

        /* Section headers */
        .cs-section {
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .cs-helper {
            color: #8b949e;
            font-size: 15px;
            margin-bottom: 18px;
        }

        hr {
            border-color: #21262d;
            margin: 18px 0px;
        }

        /* Inputs */
        div[data-baseweb="select"] > div {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            color: #e6edf3 !important;
        }
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            color: #e6edf3 !important;
        }
        label, .stMarkdown p {
            color: #c9d1d9 !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #1f6feb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 0.6em 1.6em;
            font-weight: 600;
            font-size: 15px;
        }
        .stButton > button:hover {
            background-color: #388bfd;
            color: #ffffff;
        }

        /* Result card */
        .cs-result-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            margin-top: 16px;
        }
        .cs-result-label {
            color: #8b949e;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .cs-result-value {
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .cs-result-desc {
            color: #c9d1d9;
            font-size: 15px;
            line-height: 1.5;
        }

        /* Dataframe */
        .stDataFrame {
            border: 1px solid #30363d;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="cs-title">🛡️ CoverSure</div>'
    '<div class="cs-subtitle">AI-Powered Risk &amp; User Engagement '
    'Segmentation Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown("<hr/>", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────

tab_single, tab_batch = st.tabs(["🔍 Single Profile", "📁 Batch Upload"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Profile
# ════════════════════════════════════════════════════════════════════════════

with tab_single:
    col_left, col_right = st.columns([1.3, 1], gap="large")

    with col_left:
        st.markdown('<div class="cs-section">📋 User Profile Metrics</div>', unsafe_allow_html=True)
        st.markdown('<div class="cs-helper">Enter the user\'s metrics below.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            app_status = st.selectbox("App Status", ["Installed", "Uninstalled"])
            active_policies = st.number_input(
                "Active Policies Owned", min_value=0, value=1, step=1
            )
            annual_premium = st.number_input(
                "Total Annual Premium Amount (\u20b9)", min_value=0, value=2000, step=500
            )
            signup_date_input = st.date_input("Account Signup Date", value=date(2025, 1, 1))
            bbps_transactions = st.number_input(
                "BBPS Transactions Amount (\u20b9)", min_value=0, value=0, step=100
            )

        with c2:
            lead_status = st.selectbox("Lead Generation Status", ["na", "lead"])
            cpro_status = st.selectbox("CoverPro Usage (CPRO)", ["na", "did cpro"])
            ioc_status = st.selectbox("Insurance on Cards Usage (IOC)", ["na", "used ioc"])
            partner_code = st.text_input("Partner Code Assignment", value="", placeholder="Enter code if assigned")
            phc_transactions = st.number_input(
                "PHC Transactions Amount (\u20b9)", min_value=0, value=0, step=100
            )

    with col_right:
        st.markdown('<div class="cs-section">🔮 AI Classification Output</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="cs-helper">Click the button below to run these metrics '
            'through the classification engine.</div>',
            unsafe_allow_html=True,
        )

        if st.button("Analyze Profile", type="primary"):
            category = classify_user(
                uninstalled=(app_status == "Uninstalled"),
                active_policies=active_policies,
                annual_premium=annual_premium,
                bbps_transactions=bbps_transactions,
                phc_transactions=phc_transactions,
                lead=(lead_status == "lead"),
                cpro=(cpro_status == "did cpro"),
                ioc=(ioc_status == "used ioc"),
                has_partner=bool(partner_code.strip()),
                signup_date=signup_date_input,
            )
            st.session_state["category"] = category

        if "category" in st.session_state:
            cat = st.session_state["category"]
            info = CATEGORY_INFO[cat]
            st.markdown(
                f"""
                <div class="cs-result-card">
                    <div class="cs-result-label">Assigned Category</div>
                    <div class="cs-result-value" style="color:{info['color']};">
                        {info['icon']} {cat}
                    </div>
                    <div class="cs-result-desc">{info['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="cs-result-card">
                    <div class="cs-result-desc">No profile analyzed yet — fill in the
                    metrics on the left and click <b>Analyze Profile</b>.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Batch Upload
# ════════════════════════════════════════════════════════════════════════════

with tab_batch:
    st.markdown('<div class="cs-section">📁 Batch Classification</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cs-helper">Upload a CSV or Excel file containing the columns: '
        '<code>uninstalled, active_policies, annual_premium, bbps_transactions, '
        'phc_transactions, lead, cpro, ioc, partner_code, signup</code></div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file, low_memory=False)
            else:
                df = pd.read_excel(uploaded_file)

            result = classify_dataframe(df)

            st.markdown('<div class="cs-section" style="font-size:18px; margin-top:20px;">Results</div>', unsafe_allow_html=True)
            st.dataframe(result, use_container_width=True)

            csv_bytes = result.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download classified results (CSV)",
                data=csv_bytes,
                file_name="classified_users.csv",
                mime="text/csv",
            )

            st.markdown('<div class="cs-section" style="font-size:18px; margin-top:24px;">Category Distribution</div>', unsafe_allow_html=True)
            counts = result["user_category"].value_counts()
            st.bar_chart(counts)

        except Exception as e:
            st.error(f"Could not process file: {e}")
    else:
        st.info("Awaiting file upload.")
