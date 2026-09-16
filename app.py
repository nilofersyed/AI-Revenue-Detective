import os
import pickle
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Revenue Detective",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

    /* PAGE */
    .stApp {
        background: #f6f8fc;
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* HERO */
    .hero {
        background: linear-gradient(135deg, #ffffff, #eef2ff);
        border: 1px solid #e3e7ef;
        border-radius: 22px;
        padding: 30px 34px;
        margin-bottom: 22px;
        box-shadow: 0 6px 25px rgba(30, 41, 59, 0.06);
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        color: #172033;
        margin: 0;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #667085;
        margin-top: 7px;
    }

    .hero-question {
        display: inline-block;
        margin-top: 18px;
        padding: 9px 15px;
        border-radius: 10px;
        background: #e9edff;
        color: #4338ca;
        font-size: 14px;
        font-weight: 700;
    }

    .status {
        float: right;
        background: #eafaf2;
        color: #087443;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    /* KPI */
    .kpi {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px 24px;
        min-height: 125px;
        box-shadow: 0 4px 18px rgba(30, 41, 59, 0.045);
    }

    .kpi-label {
        color: #667085;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .6px;
    }

    .kpi-value {
        color: #172033;
        font-size: 30px;
        font-weight: 800;
        margin-top: 9px;
    }

    .kpi-sub {
        color: #98a2b3;
        font-size: 12px;
        margin-top: 4px;
    }

    /* SECTION */
    .section-title {
        color: #172033;
        font-size: 24px;
        font-weight: 800;
        margin-top: 32px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #667085;
        font-size: 14px;
        margin-bottom: 14px;
    }

    /* INVESTIGATION */
    .investigation {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px 25px;
        box-shadow: 0 4px 18px rgba(30, 41, 59, 0.045);
    }

    .investigation-label {
        color: #667085;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .investigation-month {
        color: #172033;
        font-size: 27px;
        font-weight: 800;
        margin-top: 5px;
    }

    .investigation-sub {
        color: #667085;
        font-size: 14px;
        margin-top: 3px;
    }

    /* AI */
    .ai-box {
        background: linear-gradient(135deg, #eef2ff, #f7f5ff);
        border: 1px solid #d9d5ff;
        border-radius: 18px;
        padding: 20px 24px;
        margin-top: 28px;
    }

    .ai-title {
        color: #3730a3;
        font-size: 21px;
        font-weight: 800;
    }

    .ai-subtitle {
        color: #667085;
        font-size: 13px;
        margin-top: 4px;
    }

    /* FOOTER */
    .footer {
        text-align: center;
        color: #98a2b3;
        font-size: 12px;
        padding: 30px 0 10px 0;
    }

</style>
""")


# ============================================================
# LOAD DATA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "revenue_data.pkl"
)

with open(DATA_PATH, "rb") as f:
    data = pickle.load(f)

monthly_revenue = data["monthly_revenue"].copy()
items_products = data["items_products"].copy()


# ============================================================
# PREPARE MONTHLY DATA
# ============================================================

monthly_revenue["month"] = pd.to_datetime(
    monthly_revenue["month"]
)

monthly_revenue = (
    monthly_revenue
    .sort_values("month")
    .reset_index(drop=True)
)


# ============================================================
# REMOVE INCOMPLETE FINAL MONTH
# ============================================================

if len(monthly_revenue) > 1:

    complete_monthly_revenue = (
        monthly_revenue.iloc[:-1].copy()
    )

else:

    complete_monthly_revenue = (
        monthly_revenue.copy()
    )


latest_row = complete_monthly_revenue.iloc[-1]

latest_revenue = float(
    latest_row["revenue"]
)

latest_change = latest_row.get(
    "revenue_change_pct",
    None
)

latest_month = latest_row["month"]


# ============================================================
# GEMINI
# ============================================================

api_key = None

try:

    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]

except Exception:
    pass

if not api_key:

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

if not api_key:

    st.error(
        "Gemini API key is not configured."
    )

    st.stop()

client = genai.Client(
    api_key=api_key
)


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="status">
        ● AI ANALYTICS
    </div>

    <div class="hero-title">
        🔎 AI Revenue Detective
    </div>

    <div class="hero-subtitle">
        Revenue Intelligence & Root-Cause Analysis
    </div>

    <div class="hero-question">
        Revenue changed. Why?
    </div>

</div>
""")


st.html("""
<div style="
    color:#667085;
    font-size:15px;
    line-height:1.6;
    margin-bottom:22px;
">
    Investigate revenue changes, identify major contributing
    factors, and generate evidence-based business explanations
    using Generative AI.
</div>
""")


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3 = st.columns(3)


with kpi1:

    st.html(f"""
    <div class="kpi">

        <div class="kpi-label">
            💰 Latest Complete Revenue
        </div>

        <div class="kpi-value">
            ₹{latest_revenue:,.0f}
        </div>

        <div class="kpi-sub">
            {latest_month.strftime("%B %Y")}
        </div>

    </div>
    """)


with kpi2:

    if pd.notna(latest_change):

        change_text = (
            f"{float(latest_change):.2f}%"
        )

    else:

        change_text = "N/A"

    st.html(f"""
    <div class="kpi">

        <div class="kpi-label">
            📉 Month-over-Month Change
        </div>

        <div class="kpi-value">
            {change_text}
        </div>

        <div class="kpi-sub">
            Compared with previous month
        </div>

    </div>
    """)


with kpi3:

    st.html(f"""
    <div class="kpi">

        <div class="kpi-label">
            📅 Months Analyzed
        </div>

        <div class="kpi-value">
            {len(complete_monthly_revenue)}
        </div>

        <div class="kpi-sub">
            Complete reporting periods
        </div>

    </div>
    """)


# ============================================================
# REVENUE TREND
# ============================================================

st.html("""
<div class="section-title">
    📈 Revenue Performance
</div>

<div class="section-subtitle">
    Monthly revenue trend across complete reporting periods
</div>
""")


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=complete_monthly_revenue["month"],
        y=complete_monthly_revenue["revenue"],
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=
            "<b>%{x|%B %Y}</b><br>"
            "Revenue: ₹%{y:,.0f}"
            "<extra></extra>"
    )
)

fig.update_layout(
    height=400,

    margin=dict(
        l=10,
        r=10,
        t=10,
        b=10
    ),

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    xaxis=dict(
        title=None,
        showgrid=False
    ),

    yaxis=dict(
        title="Revenue",
        tickprefix="₹",
        separatethousands=True,
        gridcolor="#e5e7eb"
    ),

    hovermode="x unified",

    font=dict(
        family="Arial"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INVESTIGATION SECTION
# ============================================================

st.html("""
<div class="section-title">
    🔎 Investigate a Revenue Change
</div>

<div class="section-subtitle">
    Select a month to identify the largest contributors
    to its revenue movement.
</div>
""")


select_col, button_col = st.columns(
    [3, 1]
)


month_options = (
    complete_monthly_revenue["month"]
    .tolist()
)

month_labels = [
    month.strftime("%B %Y")
    for month in month_options
]


with select_col:

    selected_label = st.selectbox(
        "Select reporting month",
        month_labels,
        index=len(month_labels) - 1
    )


selected_month = pd.to_datetime(
    selected_label
)


with button_col:

    st.write("")

    investigate = st.button(
        "🔎 Investigate",
        type="primary",
        use_container_width=True
    )


# ============================================================
# INVESTIGATION FUNCTION
# ============================================================

def investigate_revenue(selected_month):

    selected_month = pd.to_datetime(
        selected_month
    )

    current_rows = monthly_revenue[
        monthly_revenue["month"]
        == selected_month
    ]

    if current_rows.empty:
        return None

    current_revenue = float(
        current_rows.iloc[0]["revenue"]
    )

    previous_month = (
        selected_month
        - pd.DateOffset(months=1)
    )

    previous_rows = monthly_revenue[
        monthly_revenue["month"]
        == previous_month
    ]

    if previous_rows.empty:
        return None

    previous_revenue = float(
        previous_rows.iloc[0]["revenue"]
    )

    revenue_change = (
        current_revenue
        - previous_revenue
    )

    revenue_change_pct = (
        revenue_change
        / previous_revenue
    ) * 100

    items = items_products.copy()

    if "order_purchase_timestamp" in items.columns:

        items["order_purchase_timestamp"] = (
            pd.to_datetime(
                items["order_purchase_timestamp"]
            )
        )

        items["month"] = (
            items["order_purchase_timestamp"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

    category_column = None

    possible_columns = [
        "product_category_name_english",
        "product_category_name",
        "category",
        "product_category"
    ]

    for column in possible_columns:

        if column in items.columns:

            category_column = column
            break

    category_changes = pd.DataFrame()

    if (
        category_column
        and "price" in items.columns
        and "month" in items.columns
    ):

        current_category = (
            items[
                items["month"]
                == selected_month
            ]
            .groupby(category_column)["price"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "price":
                    "current_revenue"
                }
            )
        )

        previous_category = (
            items[
                items["month"]
                == previous_month
            ]
            .groupby(category_column)["price"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "price":
                    "previous_revenue"
                }
            )
        )

        category_changes = pd.merge(
            previous_category,
            current_category,
            on=category_column,
            how="outer"
        )

        category_changes[
            [
                "previous_revenue",
                "current_revenue"
            ]
        ] = (
            category_changes[
                [
                    "previous_revenue",
                    "current_revenue"
                ]
            ].fillna(0)
        )

        category_changes["change"] = (
            category_changes["current_revenue"]
            -
            category_changes["previous_revenue"]
        )

        category_changes["change_pct"] = (
            category_changes["change"]
            /
            category_changes[
                "previous_revenue"
            ].replace(0, pd.NA)
        ) * 100

        category_changes = (
            category_changes[
                category_changes["change"] < 0
            ].copy()
        )

        category_changes[
            "absolute_decline"
        ] = (
            category_changes["change"]
            .abs()
        )

        category_changes = (
            category_changes
            .sort_values(
                "absolute_decline",
                ascending=False
            )
            .head(5)
        )

    return {
        "selected_month": selected_month,
        "previous_month": previous_month,
        "current_revenue": current_revenue,
        "previous_revenue": previous_revenue,
        "revenue_change": revenue_change,
        "revenue_change_pct": revenue_change_pct,
        "category_changes": category_changes,
        "category_column": category_column
    }


# ============================================================
# INVESTIGATION RESULT
# ============================================================

if investigate:

    result = investigate_revenue(
        selected_month
    )

    if result is None:

        st.error(
            "Not enough data to investigate this month."
        )

        st.stop()


    # --------------------------------------------------------
    # INVESTIGATION HEADER
    # --------------------------------------------------------

    st.divider()

    st.html(f"""
    <div class="investigation">

        <div class="investigation-label">
            Revenue Investigation
        </div>

        <div class="investigation-month">
            {result["selected_month"].strftime("%B %Y")}
        </div>

        <div class="investigation-sub">
            Compared with
            {result["previous_month"].strftime("%B %Y")}
        </div>

    </div>
    """)


    # --------------------------------------------------------
    # INVESTIGATION KPIs
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Current Revenue",
            f"₹{result['current_revenue']:,.0f}"
        )

    with c2:

        st.metric(
            "Previous Revenue",
            f"₹{result['previous_revenue']:,.0f}"
        )

    with c3:

        st.metric(
            "Revenue Change",
            f"{result['revenue_change_pct']:.2f}%"
        )


    # --------------------------------------------------------
    # TOP DRIVERS
    # --------------------------------------------------------

    st.html("""
    <div class="section-title">
        📉 Top Revenue Decline Drivers
    </div>

    <div class="section-subtitle">
        Product categories with the largest negative
        revenue contribution.
    </div>
    """)


    category_changes = result[
        "category_changes"
    ]

    category_column = result[
        "category_column"
    ]


    if (
        not category_changes.empty
        and category_column
    ):

        driver_chart = (
            category_changes
            .copy()
            .sort_values(
                "change",
                ascending=True
            )
        )

        driver_chart[
            "category_display"
        ] = (
            driver_chart[
                category_column
            ].astype(str)
        )


        fig_driver = go.Figure()

        fig_driver.add_trace(
            go.Bar(
                x=driver_chart["change"],
                y=driver_chart["category_display"],
                orientation="h",
                text=driver_chart["change"],
                texttemplate="₹%{x:,.0f}",
                textposition="outside",
                hovertemplate=
                    "<b>%{y}</b><br>"
                    "Revenue Change: ₹%{x:,.0f}"
                    "<extra></extra>"
            )
        )


        fig_driver.update_layout(
            height=350,

            margin=dict(
                l=10,
                r=100,
                t=10,
                b=10
            ),

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            xaxis=dict(
                title=None,
                tickprefix="₹",
                separatethousands=True,
                gridcolor="#e5e7eb"
            ),

            yaxis=dict(
                title=None
            ),

            font=dict(
                family="Arial"
            )
        )


        st.plotly_chart(
            fig_driver,
            use_container_width=True
        )


        with st.expander(
            "View detailed driver data"
        ):

            display_df = (
                category_changes[
                    [
                        category_column,
                        "previous_revenue",
                        "current_revenue",
                        "change",
                        "change_pct"
                    ]
                ].copy()
            )

            display_df.columns = [
                "Product Category",
                "Previous Revenue",
                "Current Revenue",
                "Revenue Change",
                "Change %"
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


    else:

        st.info(
            "No category-level revenue decline "
            "drivers were identified."
        )


    # ========================================================
    # GEMINI ANALYSIS
    # ========================================================

    st.html("""
    <div class="ai-box">

        <div class="ai-title">
            🤖 AI Business Analysis
        </div>

        <div class="ai-subtitle">
            Gemini explanation based only on validated
            analytical evidence.
        </div>

    </div>
    """)


    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    evidence_text = f"""

Investigated Month:
{result['selected_month'].strftime('%B %Y')}

Previous Month:
{result['previous_month'].strftime('%B %Y')}

Current Revenue:
₹{result['current_revenue']:,.2f}

Previous Revenue:
₹{result['previous_revenue']:,.2f}

Revenue Change:
₹{result['revenue_change']:,.2f}

Revenue Change Percentage:
{result['revenue_change_pct']:.2f}%

Top Category Decline Drivers:
"""


    for _, row in category_changes.iterrows():

        evidence_text += f"""

Category:
{row[category_column]}

Previous Revenue:
₹{row['previous_revenue']:,.2f}

Current Revenue:
₹{row['current_revenue']:,.2f}

Revenue Change:
₹{row['change']:,.2f}

Change Percentage:
{row['change_pct']:.2f}%
"""


    # --------------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a Business Intelligence Analyst.

Analyze the validated evidence below.

IMPORTANT RULES:

1. Use ONLY the provided evidence.
2. Do not invent numbers.
3. Do not invent facts.
4. Do not claim correlation proves causation.
5. Clearly separate facts from hypotheses.
6. If the evidence does not establish the actual cause,
   explicitly say that.
7. Recommend what should be investigated next.
8. Keep the response concise and business-friendly.

Use exactly this structure:

## What Happened

Explain the measured revenue change.

## Top Drivers

Explain the largest category-level contributors.

## Evidence

List the key facts directly supported by the data.

## Possible Explanations

Provide reasonable hypotheses, clearly labeling them
as possible explanations rather than confirmed causes.

## Recommended Investigation

Suggest the next business dimensions or data points
that should be investigated.

## Confidence

State High, Moderate, or Low confidence and explain
why based on the available evidence.

VALIDATED EVIDENCE:

{evidence_text}
"""


    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        with st.spinner(
            "🤖 Analyzing validated evidence..."
        ):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

        st.markdown(
            response.text
        )

    except Exception as e:

        st.error(
            "The AI analysis could not be generated."
        )

        st.caption(
            f"Technical error: {str(e)}"
        )


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">

    🔎 AI Revenue Detective
    &nbsp;•&nbsp;
    Analytics determines the facts. AI explains the facts.

</div>
""")
