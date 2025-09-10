# 📊 Real-Time Stock Market Dashboard  

I built this project as part of my **Data Science learning journey** 🚀.  
It’s an interactive **Stock Market Dashboard** made with **Streamlit, Python, Yahoo Finance API, and Altair**.  

The idea was simple: I wanted a tool where I could quickly search for any company (like Tesla, Apple, or NVIDIA) and instantly see how its stock is performing — both visually and in raw numbers.  

---

## ✨ What this dashboard can do
- 📈 Show real-time stock prices (with caching so it stays fast)  
- 📊 Visualize **Closing Price trends** and **Trading Volume** using Altair charts  
- 🔍 Search any company by name or ticker (or pick from a quick list of popular ones)  
- 🕒 Explore different time periods (`5d`, `1mo`, `3mo`, `6mo`, `1y`, `5y`, `max`)  
- 📅 See the latest stock data in a neat table  

---

## 🛠️ Tech behind it
- **Streamlit** → to build the interactive dashboard  
- **yfinance** → to fetch stock data  
- **Altair** → for clean, interactive charts  
- **Pandas** → to shape the data  
- **Requests** → for extra API calls  

---

## ⚡ How to run it
1. Clone this repo:  
   ```bash
   git clone https://github.com/your-username/stock-dashboard.git
   cd stock-dashboard
