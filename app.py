import os
import pickle
import textwrap

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Revenue Detective",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        /* =========================
           MAIN PAGE
        ========================= */

        .stApp {
            background: #f7f8fc;
        }

        .main .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* =========================
           HERO HEADER
        ========================= */

        .hero {
            background: linear-gradient(
                135deg,
                #ffffff 0%,
                #f1f4ff 100%
            );

            border: 1px solid #e5e7eb;
            border-radius: 20px;

            padding: 30px 35px;
            margin-bottom: 20px;

            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
        }

        .status {
            float: right;

            background: #ecfdf5;
            color: #047857;

            padding: 7px 13px;

            border-radius: 20px;

            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }

        .hero-title {
            font-size: 38px;
            font-weight: 800;

            color: #171b2e;

            margin-bottom: 5px;
        }

        .hero-subtitle {
            font-size: 16px;

            color: #6b7280;

            margin-bottom: 17px;
        }

        .hero-question {
            display: inline-block;

            background: #eef2ff;
            color: #4338ca;

            padding: 9px 15px;

            border-radius: 10px;

            font-size: 14px;
            font-weight: 700;
        }


        /* =========================
           DESCRIPTION
        ========================= */

        .description {
            color: #6b7280;

            font-size: 15px;

            margin-bottom: 25px;

            line-height: 1.6;
        }


        /* =========================
           KPI CARDS
        ========================= */

        .kpi-card {
            background: #ffffff;

            border: 1px solid #e5e7eb;

            border-radius: 18px;

            padding: 22px 24px;

            min-height: 135px;

            box-shadow: 0 3px 15px rgba(0, 0, 0, 0.035);
        }

        .kpi-label {
            color: #6b7280;

            font-size: 12px;

            font-weight: 700;

            text-transform: uppercase;

            letter-spacing: 0.6px;
        }

        .kpi-value {
            color: #171b2e;

            font-size: 30px;

            font-weight: 800;

            margin-top: 9px;
        }

        .kpi-description {
            color: #9ca3af;

            font-size: 12px;

            margin-top: 5px;
        }


        /* =========================
           SECTION HEADERS
        ========================= */

        .section-title {
            font-size: 24px;

            font-weight: 800;

            color: #171b2e;

            margin-top: 32px;

            margin-bottom: 5px;
        }

        .section-subtitle {
            color: #6b7280;

            font-size: 14px;

            margin-bottom: 15px;
        }


        /* =========================
           INVESTIGATION CARD
        ========================= */

        .investigation-card {
            background: #ffffff;

            border: 1px solid #e5e7eb;

            border-radius: 18px;

            padding: 24px;

            margin-top: 10px;

            box-shadow: 0 3px 15px rgba(0, 0, 0, 0.035);
        }

        .investigation-label {
            color: #6b7280;

            font-size: 12px;

            font-weight: 700;

            text-transform: uppercase;

            letter-spacing: 0.5px;
        }

        .investigation-month {
            color: #171b2e;

            font-size: 27px;

            font-weight: 800;

            margin-top: 5px;
        }

        .investigation-compare {
            color: #6b7280;

            font-size: 14px;

            margin-top: 4px;
        }


        /* =========================
           AI HEADER
        ========================= */

        .ai-header {
            background: linear-gradient(
                135deg,
                #eef2ff,
                #f5f3ff
            );

            border: 1px solid #ddd6fe;

            border-radius: 18px;

            padding: 20px 24px;

            margin-top: 30px;

            margin-bottom: 15px;
        }

        .ai-title {
            color: #3730a3;

            font-size: 21px;

            font-weight: 800;
        }

        .ai-subtitle {
            color: #6b7280;

            font-size: 13px;

            margin-top: 5px;
        }


        /* =========================
           FOOTER
        ========================= */

        .footer {
            text-align: center;

            color: #9ca3af;

            font-size: 12px;

            padding-top: 30px;

            padding-bottom: 10px;
        }

        </style>
        """
    ),
    unsafe_allow_html=True
)


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
        monthly_revenue
        .iloc[:-1]
        .copy()
    )

else:

    complete_monthly_revenue = (
        monthly_revenue.copy()
    )


# ============================================================
# LATEST COMPLETE MONTH
# ============================================================

latest_row = (
    complete_monthly_revenue
    .iloc[-1]
)


latest_revenue = float(
    latest_row["revenue"]
)


latest_change = latest_row.get(
    "revenue_change_pct",
    None
)


latest_month = latest_row["month"]


# ============================================================
# GEMINI API
# ============================================================

api_key = None


# Streamlit Secrets
try:

    if "GEMINI_API_KEY" in st.secrets:

        api_key = st.secrets[
            "GEMINI_API_KEY"
        ]

except Exception:

    pass


# Environment variable fallback
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
# HERO HEADER
# ============================================================

st.markdown(
    textwrap.dedent(
        """
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
        """
    ),
    unsafe_allow_html=True
)


st.markdown(
    textwrap.dedent(
        """
        <div class="description">

            Investigate revenue changes, identify major contributing
            factors, and generate evidence-based business explanations
            using Generative AI.

        </div>
        """
    ),
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3 = st.columns(3)


# ------------------------------------------------------------
# KPI 1
# ------------------------------------------------------------

with kpi1:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    💰 Latest Complete Revenue
                </div>

                <div class="kpi-value">
                    ₹{latest_revenue:,.0f}
                </div>

                <div class="kpi-description">
                    {latest_month.strftime("%B %Y")}
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI 2
# ------------------------------------------------------------

with kpi2:

    if pd.notna(latest_change):

        change_text = (
            f"{float(latest_change):.2f}%"
        )

    else:

        change_text = "N/A"


    st.markdown(
        textwrap.dedent(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    📉 Month-over-Month Change
                </div>

                <div class="kpi-value">
                    {change_text}
                </div>

                <div class="kpi-description">
                    Compared with previous month
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI 3
# ------------------------------------------------------------

with kpi3:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    📅 Months Analyzed
                </div>

                <div class="kpi-value">
                    {len(complete_monthly_revenue)}
                </div>

                <div class="kpi-description">
                    Complete monthly periods
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# ============================================================
# REVENUE PERFORMANCE
# ============================================================

st.markdown(
    textwrap.dedent(
        """
        <div class="section-title">
            📈 Revenue Performance
        </div>

        <div class="section-subtitle">
            Monthly revenue trend across complete reporting periods
        </div>
        """
    ),
    unsafe_allow_html=True
)


chart_df = (
    complete_monthly_revenue.copy()
)


fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=chart_df["month"],
        y=chart_df["revenue"],

        mode="lines+markers",

        line=dict(
            width=3
        ),

        marker=dict(
            size=7
        ),

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
        t=15,
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

st.markdown(
    textwrap.dedent(
        """
        <div class="section-title">
            🔎 Investigate a Revenue Change
        </div>

        <div class="section-subtitle">
            Select a month to identify the largest contributors
            to its revenue movement.
        </div>
        """
    ),
    unsafe_allow_html=True
)


select_col, button_col = st.columns(
    [3, 1]
)


# ============================================================
# MONTH SELECTOR
# ============================================================

month_options = (
    complete_monthly_revenue[
        "month"
    ].tolist()
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

def investigate_revenue(
    selected_month
):

    selected_month = pd.to_datetime(
        selected_month
    )


    # --------------------------------------------------------
    # CURRENT MONTH
    # --------------------------------------------------------

    current_rows = monthly_revenue[
        monthly_revenue["month"]
        == selected_month
    ]


    if current_rows.empty:

        return None


    current_revenue = float(
        current_rows.iloc[0]["revenue"]
    )


    # --------------------------------------------------------
    # PREVIOUS MONTH
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # REVENUE CHANGE
    # --------------------------------------------------------

    revenue_change = (
        current_revenue
        - previous_revenue
    )


    revenue_change_pct = (
        revenue_change
        / previous_revenue
    ) * 100


    # --------------------------------------------------------
    # PREPARE ITEMS
    # --------------------------------------------------------

    items = items_products.copy()


    if "order_purchase_timestamp" in items.columns:

        items[
            "order_purchase_timestamp"
        ] = pd.to_datetime(
            items[
                "order_purchase_timestamp"
            ]
        )


        items["month"] = (
            items[
                "order_purchase_timestamp"
            ]
            .dt.to_period("M")
            .dt.to_timestamp()
        )


    # --------------------------------------------------------
    # FIND CATEGORY COLUMN
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


    category_changes = pd.DataFrame()


    # --------------------------------------------------------
    # CATEGORY ANALYSIS
    # --------------------------------------------------------

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
        )


        previous_category = (
            items[
                items["month"]
                == previous_month
            ]
            .groupby(category_column)["price"]
            .sum()
            .reset_index()
        )


        current_category = (
            current_category
            .rename(
                columns={
                    "price":
                    "current_revenue"
                }
            )
        )


        previous_category = (
            previous_category
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
        ] = category_changes[
            [
                "previous_revenue",
                "current_revenue"
            ]
        ].fillna(0)


        category_changes["change"] = (
            category_changes[
                "current_revenue"
            ]
            -
            category_changes[
                "previous_revenue"
            ]
        )


        category_changes["change_pct"] = (

            category_changes["change"]

            /

            category_changes[
                "previous_revenue"
            ].replace(0, pd.NA)

        ) * 100


        # Only declining categories
        category_changes = (
            category_changes[
                category_changes["change"] < 0
            ]
            .copy()
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

        "selected_month":
            selected_month,

        "previous_month":
            previous_month,

        "current_revenue":
            current_revenue,

        "previous_revenue":
            previous_revenue,

        "revenue_change":
            revenue_change,

        "revenue_change_pct":
            revenue_change_pct,

        "category_changes":
            category_changes,

        "category_column":
            category_column
    }


# ============================================================
# RUN INVESTIGATION
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


    # ========================================================
    # INVESTIGATION HEADER
    # ========================================================

    st.divider()


    st.markdown(
        textwrap.dedent(
            f"""
            <div class="investigation-card">

                <div class="investigation-label">
                    Revenue Investigation
                </div>

                <div class="investigation-month">
                    {result["selected_month"].strftime("%B %Y")}
                </div>

                <div class="investigation-compare">
                    Compared with
                    {result["previous_month"].strftime("%B %Y")}
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


    # ========================================================
    # INVESTIGATION KPIs
    # ========================================================

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


    # ========================================================
    # TOP DRIVERS
    # ========================================================

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                📉 Top Revenue Decline Drivers
            </div>

            <div class="section-subtitle">
                Product categories with the largest negative
                revenue contribution.
            </div>
            """
        ),
        unsafe_allow_html=True
    )


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


        # ----------------------------------------------------
        # DRIVER CHART
        # ----------------------------------------------------

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


        fig_driver = px.bar(

            driver_chart,

            x="change",

            y="category_display",

            orientation="h",

            labels={
                "change":
                    "Revenue Change",

                "category_display":
                    "Product Category"
            },

            text="change"
        )


        fig_driver.update_traces(

            texttemplate=
                "₹%{x:,.0f}",

            textposition="outside",

            hovertemplate=
                "<b>%{y}</b><br>"
                "Revenue Change: ₹%{x:,.0f}"
                "<extra></extra>"
        )


        fig_driver.update_layout(

            height=330,

            margin=dict(
                l=10,
                r=80,
                t=10,
                b=10
            ),

            paper_bgcolor=
                "rgba(0,0,0,0)",

            plot_bgcolor=
                "rgba(0,0,0,0)",

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


        # ----------------------------------------------------
        # DETAILED DATA
        # ----------------------------------------------------

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
                ]
                .copy()
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
    # AI BUSINESS ANALYSIS
    # ========================================================

    st.markdown(
        textwrap.dedent(
            """
            <div class="ai-header">

                <div class="ai-title">
                    🤖 AI Business Analysis
                </div>

                <div class="ai-subtitle">
                    Gemini explanation based only on validated
                    analytical evidence
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # BUILD VALIDATED EVIDENCE
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


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

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


    # ========================================================
    # GEMINI GENERATION
    # ========================================================

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

st.markdown(
    textwrap.dedent(
        """
        <div class="footer">

            🔎 AI Revenue Detective
            &nbsp;•&nbsp;
            Analytics determines the facts. AI explains the facts.

        </div>
        """
    ),
    unsafe_allow_html=True
)
