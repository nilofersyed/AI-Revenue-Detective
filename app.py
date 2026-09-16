import os
import pickle
import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Revenue Detective",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "revenue_data.pkl")

with open(DATA_PATH, "rb") as f:
    data = pickle.load(f)

monthly_revenue = data["monthly_revenue"]
items_products = data["items_products"]


# ============================================================
# PREPARE MONTHLY REVENUE DATA
# ============================================================

monthly_revenue = monthly_revenue.copy()

# Make sure month is datetime
if "month" in monthly_revenue.columns:
    monthly_revenue["month"] = pd.to_datetime(
        monthly_revenue["month"]
    )

monthly_revenue = monthly_revenue.sort_values("month").reset_index(drop=True)


# ============================================================
# FIX: USE LATEST COMPLETE MONTH FOR KPI
# ============================================================

# The final month in the Olist dataset is incomplete.
# Therefore, we exclude the last month from the executive KPIs.

if len(monthly_revenue) >= 2:

    complete_monthly_revenue = monthly_revenue.iloc[:-1].copy()

else:

    complete_monthly_revenue = monthly_revenue.copy()


# Latest complete month
latest_row = complete_monthly_revenue.iloc[-1]

latest_revenue = latest_row["revenue"]

latest_monthly_change = latest_row.get(
    "revenue_change_pct",
    None
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:

    st.error(
        "Gemini API key not configured. "
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )

    st.stop()


client = genai.Client(api_key=api_key)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🔎 AI Revenue Detective")

st.caption(
    "Automated Revenue Root-Cause Analysis & Business Intelligence System"
)

st.markdown(
    """
    > **Revenue changed. Why?**
    
    Analyze revenue trends, identify the major contributors to change,
    and generate an evidence-based business explanation using Generative AI.
    """
)


# ============================================================
# EXECUTIVE KPI SECTION
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Latest Complete Revenue",
        f"₹{latest_revenue:,.0f}"
    )


with col2:

    if pd.notna(latest_monthly_change):

        st.metric(
            "Monthly Change",
            f"{latest_monthly_change:.2f}%"
        )

    else:

        st.metric(
            "Monthly Change",
            "N/A"
        )


with col3:

    st.metric(
        "Months Analyzed",
        len(complete_monthly_revenue)
    )


# ============================================================
# REVENUE TREND
# ============================================================

st.subheader("📈 Revenue Trend")

chart_data = complete_monthly_revenue.copy()

chart_data["Month"] = chart_data["month"].dt.strftime("%b %Y")

chart_data = chart_data.set_index("Month")

st.line_chart(
    chart_data["revenue"]
)


# ============================================================
# MONTH SELECTION
# ============================================================

st.subheader("🔎 Investigate Revenue")


# Convert available months into readable labels
month_options = complete_monthly_revenue["month"].tolist()

month_labels = [
    month.strftime("%B %Y")
    for month in month_options
]


selected_label = st.selectbox(
    "Select a month to investigate:",
    month_labels
)


selected_month = pd.to_datetime(
    selected_label
)


# ============================================================
# INVESTIGATION FUNCTION
# ============================================================

def investigate_revenue(selected_month):

    selected_month = pd.to_datetime(selected_month)

    # --------------------------------------------------------
    # Find current month
    # --------------------------------------------------------

    current_rows = monthly_revenue[
        monthly_revenue["month"] == selected_month
    ]

    if current_rows.empty:

        return None

    current_revenue = current_rows.iloc[0]["revenue"]


    # --------------------------------------------------------
    # Find previous month
    # --------------------------------------------------------

    previous_month = (
        selected_month - pd.DateOffset(months=1)
    )

    previous_rows = monthly_revenue[
        monthly_revenue["month"] == previous_month
    ]


    if previous_rows.empty:

        return None

    previous_revenue = previous_rows.iloc[0]["revenue"]


    # --------------------------------------------------------
    # Calculate revenue change
    # --------------------------------------------------------

    revenue_change = (
        current_revenue - previous_revenue
    )

    revenue_change_pct = (
        revenue_change / previous_revenue
    ) * 100


    # --------------------------------------------------------
    # Category analysis
    # --------------------------------------------------------

    items = items_products.copy()


    # Make sure order purchase timestamp is datetime
    if "order_purchase_timestamp" in items.columns:

        items["order_purchase_timestamp"] = pd.to_datetime(
            items["order_purchase_timestamp"]
        )

        items["month"] = (
            items["order_purchase_timestamp"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )


    # --------------------------------------------------------
    # Identify category column
    # --------------------------------------------------------

    category_column = None

    possible_category_columns = [
        "product_category_name_english",
        "product_category_name",
        "category",
        "product_category"
    ]

    for column in possible_category_columns:

        if column in items.columns:

            category_column = column
            break


    # --------------------------------------------------------
    # Category revenue comparison
    # --------------------------------------------------------

    category_changes = pd.DataFrame()


    if category_column is not None and "price" in items.columns:

        current_category = (
            items[
                items["month"] == selected_month
            ]
            .groupby(category_column)["price"]
            .sum()
            .reset_index()
        )

        previous_category = (
            items[
                items["month"] == previous_month
            ]
            .groupby(category_column)["price"]
            .sum()
            .reset_index()
        )


        current_category = current_category.rename(
            columns={
                "price": "current_revenue"
            }
        )

        previous_category = previous_category.rename(
            columns={
                "price": "previous_revenue"
            }
        )


        category_changes = pd.merge(
            previous_category,
            current_category,
            on=category_column,
            how="outer"
        )


        category_changes[
            ["previous_revenue", "current_revenue"]
        ] = category_changes[
            ["previous_revenue", "current_revenue"]
        ].fillna(0)


        category_changes["change"] = (
            category_changes["current_revenue"]
            -
            category_changes["previous_revenue"]
        )


        category_changes["change_pct"] = (
            category_changes["change"]
            /
            category_changes["previous_revenue"].replace(
                0,
                pd.NA
            )
        ) * 100


        # Only declining categories
        category_changes = category_changes[
            category_changes["change"] < 0
        ].copy()


        # Sort by largest absolute revenue decline
        category_changes["absolute_decline"] = (
            category_changes["change"].abs()
        )


        category_changes = category_changes.sort_values(
            "absolute_decline",
            ascending=False
        )


        category_changes = category_changes.head(10)


    # --------------------------------------------------------
    # Build evidence
    # --------------------------------------------------------

    evidence = {

        "investigated_month":
            selected_month.strftime("%B %Y"),

        "previous_month":
            previous_month.strftime("%B %Y"),

        "current_revenue":
            round(float(current_revenue), 2),

        "previous_revenue":
            round(float(previous_revenue), 2),

        "revenue_change":
            round(float(revenue_change), 2),

        "revenue_change_pct":
            round(float(revenue_change_pct), 2),

        "top_category_drivers":
            []
    }


    if not category_changes.empty:

        for _, row in category_changes.iterrows():

            evidence["top_category_drivers"].append(
                {
                    "category":
                        str(row[category_column]),

                    "previous_revenue":
                        round(
                            float(row["previous_revenue"]),
                            2
                        ),

                    "current_revenue":
                        round(
                            float(row["current_revenue"]),
                            2
                        ),

                    "change":
                        round(
                            float(row["change"]),
                            2
                        ),

                    "change_pct":
                        round(
                            float(row["change_pct"]),
                            2
                        )
                    if pd.notna(row["change_pct"])
                    else None
                }
            )


    return evidence, category_changes


# ============================================================
# INVESTIGATE BUTTON
# ============================================================

if st.button(
    "🔎 Investigate This",
    type="primary",
    use_container_width=True
):

    result = investigate_revenue(selected_month)


    if result is None:

        st.error(
            "There is not enough data to compare this month "
            "with the previous month."
        )

        st.stop()


    evidence, category_changes = result


    # ========================================================
    # INVESTIGATION SUMMARY
    # ========================================================

    st.divider()

    st.header(
        f"Investigation: {evidence['investigated_month']}"
    )


    # ========================================================
    # INVESTIGATION KPIs
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Current Revenue",
            f"₹{evidence['current_revenue']:,.2f}"
        )


    with col2:

        st.metric(
            "Previous Revenue",
            f"₹{evidence['previous_revenue']:,.2f}"
        )


    with col3:

        st.metric(
            "Revenue Change",
            f"{evidence['revenue_change_pct']:.2f}%"
        )


    # ========================================================
    # TOP REVENUE DECLINE DRIVERS
    # ========================================================

    st.subheader(
        "📉 Top Revenue Decline Drivers"
    )


    if not category_changes.empty:

        display_columns = [
            category_changes.columns[
                category_changes.columns.isin(
                    [
                        "product_category_name_english",
                        "product_category_name",
                        "category",
                        "product_category"
                    ]
                )
            ][0],
            "previous_revenue",
            "current_revenue",
            "change",
            "change_pct"
        ]


        display_df = category_changes[
            display_columns
        ].copy()


        # Rename category column
        category_name = display_columns[0]

        display_df = display_df.rename(
            columns={
                category_name: "Product Category",
                "previous_revenue": "Previous Revenue",
                "current_revenue": "Current Revenue",
                "change": "Revenue Change",
                "change_pct": "Change %"
            }
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "No category-level revenue decline drivers "
            "were identified."
        )


    # ========================================================
    # GEMINI ANALYSIS
    # ========================================================

    st.subheader(
        "🤖 AI Revenue Detective Analysis"
    )


    # --------------------------------------------------------
    # Create evidence text
    # --------------------------------------------------------

    evidence_text = f"""
Investigated Month:
{evidence['investigated_month']}

Previous Month:
{evidence['previous_month']}

Current Revenue:
₹{evidence['current_revenue']:,.2f}

Previous Revenue:
₹{evidence['previous_revenue']:,.2f}

Revenue Change:
₹{evidence['revenue_change']:,.2f}

Revenue Change Percentage:
{evidence['revenue_change_pct']:.2f}%

Top Revenue Decline Drivers:
"""


    for driver in evidence["top_category_drivers"]:

        evidence_text += f"""

Category:
{driver['category']}

Previous Revenue:
₹{driver['previous_revenue']:,.2f}

Current Revenue:
₹{driver['current_revenue']:,.2f}

Revenue Change:
₹{driver['change']:,.2f}

Change Percentage:
{driver['change_pct']}%
"""


    # --------------------------------------------------------
    # Gemini prompt
    # --------------------------------------------------------

    prompt = f"""
You are a business intelligence analyst.

Analyze the following validated analytical evidence.

IMPORTANT RULES:

1. Use ONLY the evidence provided below.
2. Do not invent numbers.
3. Do not claim that a possible explanation is a proven cause.
4. Clearly distinguish measured facts from possible explanations.
5. If the evidence does not establish the true cause, say so.
6. Recommend what the business should investigate next.
7. Keep the explanation concise and business-friendly.

Structure your response as:

## What Happened

Explain the revenue change using the provided numbers.

## Top Drivers

Identify the largest category-level contributors to the decline.

## What the Evidence Shows

State only conclusions directly supported by the data.

## Possible Explanations

Give reasonable hypotheses, clearly labeling them as hypotheses rather than confirmed causes.

## Recommended Investigation

Suggest the next dimensions or data points the business should investigate.

## Confidence

State whether the evidence provides:
- High confidence
- Moderate confidence
- Low confidence

Then briefly explain why.

VALIDATED EVIDENCE:

{evidence_text}
"""


    # --------------------------------------------------------
    # Generate Gemini response
    # --------------------------------------------------------

    try:

        with st.spinner(
            "🤖 Gemini is analyzing the validated evidence..."
        ):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )


        st.markdown(response.text)


    except Exception as e:

        st.error(
            "Gemini analysis could not be generated."
        )

        st.caption(
            f"Error: {str(e)}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Revenue Detective • Analytics determines the facts. "
    "AI explains the facts."
)
