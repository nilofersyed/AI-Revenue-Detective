
# Project Summary

## Problem

Business teams can see that revenue changed, but identifying why it changed often requires manually exploring multiple dimensions.

## Solution

AI Revenue Detective automates the first stage of revenue investigation.

The system calculates revenue trends, detects changes, compares periods, identifies major category-level drivers, and sends validated evidence to Gemini for natural-language explanation.

## Key Feature

### Investigate This

A user selects a month and clicks **Investigate This**.

The system:

1. Compares the selected month with the previous month.
2. Calculates the revenue change.
3. Identifies the largest category-level changes.
4. Displays the evidence.
5. Generates an AI investigation report.

## Architecture

Python Analytics Layer → Evidence Package → Gemini → Streamlit

## Dataset

Olist Brazilian E-Commerce dataset.

## Future Enhancements

- SQL database integration
- Seller-level investigation in the UI
- State-level investigation in the UI
- Statistical significance testing
- Revenue anomaly scoring
- Power BI executive dashboard
