
import streamlit as st
import pandas as pd
import pickle
import json
import os
from google import genai

st.set_page_config(
    page_title="AI Revenue Detective",
    page_icon="🔎",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load analysis data
with open(os.path.join(BASE_DIR, "revenue_data.pkl"), "rb") as f:
    data = pickle.load(f)

monthly_revenue = data["monthly_revenue"]
items_products = data["items_products"]

# Gemini API
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# Header
st.title("🔎 AI Revenue Detective")
st.caption(
    "Automated Revenue Root-Cause & Business Intelligence System"
)

st.divider()

# KPIs
latest = monthly_revenue.iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Latest Revenue", f"₹{latest['revenue']:,.0f}")

with col2:
    st.metric("Monthly Change", f"{latest['revenue_change_pct']:.2f}%")

with col3:
    st.metric("Months Analyzed", len(monthly_revenue))

st.divider()

# Revenue trend
st.subheader("📈 Revenue Trend")

chart_data = monthly_revenue.copy()
chart_data["month"] = pd.to_datetime(chart_data["month"])
chart_data = chart_data.set_index("month")

st.line_chart(chart_data["revenue"], height=350)

st.divider()

# Investigation
st.subheader("🔎 Investigate Revenue")

selected_month = st.selectbox(
    "Select a month to investigate",
    monthly_revenue["month"].tolist()
)

if st.button(
    "🔎 Investigate This",
    type="primary",
    use_container_width=True
):

    idx = monthly_revenue[
        monthly_revenue["month"] == selected_month
    ].index[0]

    if idx == 0:

        st.warning(
            "This is the first month in the dataset, "
            "so there is no previous month for comparison."
        )

    else:

        previous_month = monthly_revenue.iloc[idx - 1]["month"]

        current_revenue = float(
            monthly_revenue.iloc[idx]["revenue"]
        )

        previous_revenue = float(
            monthly_revenue.iloc[idx - 1]["revenue"]
        )

        change_pct = (
            (current_revenue - previous_revenue)
            / previous_revenue
        ) * 100

        current_data = items_products[
            items_products["month"] == selected_month
        ]

        previous_data = items_products[
            items_products["month"] == previous_month
        ]

        current_cat = current_data.groupby(
            "category_name"
        )["revenue"].sum()

        previous_cat = previous_data.groupby(
            "category_name"
        )["revenue"].sum()

        comparison = pd.concat(
            [
                previous_cat.rename("Previous Revenue"),
                current_cat.rename("Current Revenue")
            ],
            axis=1
        ).fillna(0)

        comparison["Change"] = (
            comparison["Current Revenue"]
            - comparison["Previous Revenue"]
        )

        top_categories = (
            comparison
            .sort_values("Change")
            .head(5)
            .reset_index()
        )

        st.subheader("📊 Investigation Results")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Investigation Month", selected_month)

        with c2:
            st.metric("Previous Month", previous_month)

        with c3:
            st.metric("Revenue Change", f"{change_pct:.2f}%")

        st.subheader("📉 Top Revenue Decline Drivers")

        st.dataframe(
            top_categories,
            use_container_width=True,
            hide_index=True
        )

        evidence = {
            "month": selected_month,
            "previous_month": previous_month,
            "revenue_change_pct": round(change_pct, 2),
            "top_category_drivers":
                top_categories.to_dict(orient="records")
        }

        prompt = f"""
You are an experienced business analyst.

Analyze ONLY the validated evidence below.

{json.dumps(evidence, indent=2)}

Create a concise business investigation.

Include:

1. WHAT HAPPENED
2. TOP DRIVERS
3. WHAT THE EVIDENCE SHOWS
4. POSSIBLE BUSINESS EXPLANATIONS
5. RECOMMENDED INVESTIGATIONS
6. CONFIDENCE

Rules:
- Use only the supplied evidence.
- Do not invent numbers.
- Do not claim causation.
- Clearly separate facts from possible explanations.
- Keep it suitable for a business manager.
"""

        with st.spinner("🤖 AI Revenue Detective is analyzing..."):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                st.divider()
                st.subheader("🤖 AI Revenue Detective Analysis")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Gemini error: {e}")

st.divider()

st.caption(
    "Python • Pandas • Streamlit • Gemini API • Olist E-Commerce Dataset"
)
