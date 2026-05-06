# AlgoTrade Engine

## Overview
**AlgoTrade Engine** is a comprehensive, full-stack algorithmic trading backtester and analytical platform. It goes beyond standard trading platforms by explicitly integrating and demonstrating core **Design and Analysis of Algorithms (DAA)** paradigms to solve common computational bottlenecks in quantitative finance. 

This project features a high-performance **FastAPI (Python)** backend responsible for executing complex financial algorithms, paired with a premium, minimalist **React (Vite)** frontend dashboard designed to visualize algorithmic performance, theoretical time complexities, and trading signals in real-time.

---

## 🧠 Design and Analysis of Algorithms (DAA) Paradigms

The core of AlgoTrade Engine is built around optimizing standard trading operations using advanced algorithmic techniques. Here is an in-depth breakdown of the DAA paradigms utilized, how they are implemented, and why they are essential for high-frequency trading and backtesting.

### 1. Data Layer: Range Queries
**Algorithms:** Segment Trees & Sparse Tables
- **How it's used:** Financial time-series data requires constant querying over specific historical windows (e.g., "What was the lowest price in the last 14 days?"). We implement Segment Trees for dynamic data (where recent prices might update) and Sparse Tables for static, historical data.
- **Why it's used:** A naive approach to finding a minimum or maximum over a range of size `N` takes `O(N)` time. When running backtests over millions of ticks, this becomes a severe bottleneck `O(Q * N)`. 
  - **Segment Trees** reduce range queries and point updates to **`O(log N)`**, allowing rapid calculation of rolling metrics.
  - **Sparse Tables** allow for **`O(1)`** range minimum/maximum queries on immutable historical data after an `O(N log N)` preprocessing step.

### 2. Signal Engine: Pattern Matching & Signal Processing
**Algorithms:** Knuth-Morris-Pratt (KMP), Rabin-Karp, and Fast Fourier Transform (FFT)
- **How it's used (String Matching):** Candlestick patterns (e.g., Doji, Hammer, Engulfing) are encoded into string sequences representing directional movements (Up/Down). KMP and Rabin-Karp algorithms search for these specific sequences within the massive string of historical price action.
- **Why it's used:** Brute-force substring search takes `O(N * M)` time. **KMP** and **Rabin-Karp** optimize this to **`O(N + M)`**, ensuring that searching for complex multi-candle patterns across decades of tick data happens almost instantaneously without redundant backtracking.
- **How it's used (FFT):** The Fast Fourier Transform is applied to price sequences to transform them from the time domain to the frequency domain. 
- **Why it's used:** Markets often exhibit cyclical behavior. FFT extracts dominant cyclical frequencies in **`O(N log N)`** time (compared to the naive `O(N^2)` Discrete Fourier Transform), allowing the engine to generate predictive signals based on underlying market harmonics.

### 3. Signal Engine: Maximum Profit
**Algorithms:** Kadane's Algorithm & Divide and Conquer
- **How it's used:** Used to find the Maximum Subarray (the period of greatest contiguous price increase/drawdown). 
- **Why it's used:** Finding the maximum potential profit if one had bought and sold perfectly within a given timeframe. Kadane's algorithm solves this in strict **`O(N)`** time and `O(1)` space, making it vastly superior to the brute-force `O(N^2)` combination checking.

### 4. Portfolio Construction: Optimization & Diversification
**Algorithms:** 0/1 Knapsack (Dynamic Programming) & Minimum Spanning Tree (MST)
- **How it's used (0/1 Knapsack):** Capital allocation is treated as a Knapsack problem. Given a limited capital budget (weight capacity), the algorithm selects a combination of trading signals/assets that maximize expected return (value) without exceeding risk limits.
- **Why it's used:** Dynamic Programming solves the 0/1 Knapsack problem in pseudo-polynomial time **`O(N * W)`**, avoiding the exponential `O(2^N)` time of trying all possible portfolio combinations, thereby finding the mathematically optimal capital distribution efficiently.
- **How it's used (MST):** To ensure portfolio diversification, assets are represented as a graph where edge weights are the historical correlations between them. Kruskal's or Prim's algorithm (supported by Disjoint Set Union) finds the Minimum Spanning Tree.
- **Why it's used:** Selecting assets that form the MST ensures we pick a subset of assets that are least correlated with each other in **`O(E log V)`** time, mathematically minimizing systemic portfolio risk.

### 5. Execution Layer: Order Management
**Algorithms:** Priority Queues (Heaps) & Greedy Algorithms
- **How it's used (Priority Queues):** Order books and execution queues utilize Min/Max Heaps to manage Bid and Ask prices.
- **Why it's used:** Heaps guarantee **`O(1)`** access to the best available price and **`O(log N)`** insertion/deletion, which is critical for the microsecond-latency requirements of order matching.
- **How it's used (Greedy Activity Selection):** For scheduling non-overlapping trades or execution windows to minimize market impact.
- **Why it's used:** The Greedy approach provides an optimal solution for the activity selection problem in **`O(N log N)`** time (dominated by sorting), ensuring maximum utilization of trading windows.

---

## 🚀 Setup Documentation

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Clone the Repository
```bash
git clone https://github.com/Lokaksha25/Algotrade-.git
cd Algotrade-
```

### 2. Backend Setup (FastAPI)
Navigate to the `backend` directory and install the required Python packages.

```bash
cd backend
pip install -r requirements.txt
```

Start the FastAPI backend server:
```bash
python -m uvicorn main:app --reload
```
The backend API will be available at `http://127.0.0.1:8000`.

### 3. Frontend Setup (React / Vite)
Open a new terminal window, navigate to the `frontend` directory, install dependencies, and start the development server.

```bash
cd frontend
npm install
npm run dev
```
The interactive web dashboard will be available at `http://localhost:5173/`.

---

*Built with precision for advanced algorithmic backtesting and financial analytics.*
