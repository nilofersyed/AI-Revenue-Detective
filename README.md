
# 🔎 AI Revenue Detective

### Automated Revenue Root-Cause & Business Intelligence System

> **Business Question:** Revenue changed. Why?

AI Revenue Detective is an interactive analytics application that detects revenue changes, identifies the major drivers behind those changes, and uses Generative AI to explain validated business evidence.

## 🚀 Project Workflow

Raw E-Commerce Data  
↓  
Data Preparation  
↓  
Revenue Analysis  
↓  
Anomaly Detection  
↓  
Root-Cause Analysis  
↓  
Validated Evidence  
↓  
Gemini AI Explanation  
↓  
Streamlit Application

## 📊 What the System Does

- Calculates monthly revenue
- Detects month-over-month revenue changes
- Identifies categories driving revenue declines
- Compares current and previous month performance
- Provides evidence-based investigation results
- Uses Gemini to generate business-friendly explanations
- Provides recommended areas for further investigation

## 🤖 AI Design

A key design principle is:

**Analytics determines the facts.  
AI explains the validated evidence.**

Gemini does not independently determine the root cause from raw data. The Python analytics layer calculates the metrics and drivers first, and only the validated evidence is passed to the AI.

## 🛠️ Technology Stack

- Python
- Pandas
- Streamlit
- Google Gemini API
- Olist E-Commerce Dataset
- Data Analysis
- Root-Cause Analysis
- Generative AI

## 📈 Example Investigation

For August 2018, the system identified a **4.56% month-over-month revenue decline**.

The investigation highlighted categories including:

- watches_gifts
- cool_stuff
- garden_tools
- office_furniture
- fixed_telephony

The AI layer then converted these validated findings into a business investigation report while separating measured facts from possible explanations.

## 🎯 Business Value

The system helps analysts move from:

**"Revenue changed."**

to:

**"Which dimensions contributed to the change, what does the evidence show, and what should we investigate next?"**

## ⚠️ Data & AI Safety

API keys are not stored in the repository.

The Gemini API key should be supplied through an environment variable:

`GEMINI_API_KEY`

## 👩‍💻 Author

Syed Nilofer

Computer Science Engineering | Data Analytics | Business Intelligence | Generative AI
