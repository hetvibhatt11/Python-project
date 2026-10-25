# Smart Budget Optimization System — DAA Mini Project

A beginner-friendly mini project with **C++ as the algorithm engine** and **Streamlit as the UI**.

## Features
- Set a monthly budget.
- Add and edit expenses in the dashboard.
- Calculate total expenses and remaining budget.
- Sort expenses using Bubble Sort implemented in C++.
- Recommend a budget plan using a greedy priority-per-rupee heuristic implemented in C++.
- Show a chart and algorithm complexity.

## Files
- `app.py` — Streamlit UI, written in Python.
- `budget_engine.cpp` — Core calculations, Bubble Sort, and greedy selection in C++.
- `requirements.txt` — Python packages.

## Run locally
1. Install Python 3.10+ and a C++ compiler (`g++`).
2. Open a terminal in this folder.
3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   streamlit run app.py
   ```

If `g++` is not recognized, install MinGW-w64 (Windows) or use a system with g++ installed. The app compiles the C++ engine when it runs.

## Deploy online with Streamlit Community Cloud
1. Upload these files to a GitHub repository.
2. Make sure the repository includes `app.py`, `budget_engine.cpp`, and `requirements.txt`.
3. In Streamlit Community Cloud, create an app from that repository and set the main file to `app.py`.
4. A hosted environment must have `g++` available. If the deployment environment does not include it, configure a suitable build environment or use the local run method.

## DAA concepts
- Bubble Sort: O(n²) time.
- Greedy strategy: sort expenses by priority/amount, O(n log n), then scan expenses in O(n).
- Total calculation: O(n).

## Important limitation
The greedy selection is a heuristic, not guaranteed to find the globally optimal subset of expenses. It is for educational demonstration, not financial advice.
