# 🔎 AI Revenue Detective

### Automated Revenue Root-Cause & Business Intelligence System

**Revenue changed. Why?**

AI Revenue Detective is an AI-powered business intelligence application designed to investigate changes in revenue and identify the underlying business drivers.

The system combines **Python-based data analysis, root-cause investigation, evidence validation, Generative AI, and Streamlit** to transform raw e-commerce data into structured, explainable business insights.

Rather than asking an LLM to interpret raw data directly, the system follows an **evidence-first architecture**:

> **Analytics determines the facts. Generative AI explains the facts.**

---

## 🌐 Live Application

### 🚀 [Launch AI Revenue Detective](https://ai-revenue-detective-pdkjd9znqwu5pxhjh7eryk.streamlit.app/)

## 💻 Source Code

### [GitHub Repository](https://github.com/nilofersyed/AI-Revenue-Detective)

---

# 📌 Project Overview

Revenue dashboards typically answer:

> **"What happened?"**

However, business teams often need to answer:

> **"Why did it happen?"**

AI Revenue Detective addresses this problem by automatically investigating revenue changes across multiple business dimensions.

The application detects revenue changes, identifies the largest contributing factors, validates the analytical evidence, and then uses Gemini to generate a concise business explanation.

---

# 🎯 Business Problem

Unexpected revenue changes can be difficult to investigate manually when the underlying data contains thousands of transactions across multiple products, sellers, customers, and locations.

A business analyst may need to investigate:

- When did revenue change?
- How large was the change?
- Which product categories contributed?
- Which sellers were affected?
- Which states contributed to the movement?
- What are the major revenue drivers?
- How can the findings be communicated clearly?

This project automates that analytical workflow.

---

# 💡 Solution

The system follows a structured pipeline:

```text
                 ┌─────────────────────┐
                 │  Olist E-Commerce   │
                 │       Dataset       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Data Preparation   │
                 │   Python / Pandas   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Revenue & KPI       │
                 │     Analysis        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Change Detection    │
                 │    Month-over-      │
                 │    Month Analysis   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Root-Cause Analysis │
                 │ Category / State /  │
                 │       Seller        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Evidence Validation │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     Gemini AI       │
                 │ Business Explanation│
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Streamlit App    │
                 └─────────────────────┘
