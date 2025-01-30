# Trade It 📈  
**A Virtual Stock Trading Platform**  

Trade It is a web application that lets users simulate stock trading with real-time market data. Buy/sell company shares, track your portfolio, and analyze transaction history—all with a $10,000 virtual starting balance!  

![Demo Preview](https://github.com/user-attachments/assets/04194587-1479-4c29-8108-25e9130718da)  
*(Replace with actual screenshot of your app)*  

---

## Features 🚀  
- **Real-Time Stock Quotes**: Fetch live prices using Yahoo Finance API  
- **Buy & Sell Stocks**: Execute trades with instant portfolio updates  
- **Portfolio Dashboard**: View holdings, cash balance, and total net worth  
- **Transaction History**: Detailed log of all buys/sells with timestamps  
- **Secure Authentication**: Password hashing and session management  
- **Responsive Design**: Works flawlessly on all devices via Bootstrap  

---

## Technologies Used 🛠️  
- **Backend**: Python/Flask, SQLite  
- **Frontend**: HTML/CSS, JavaScript, Bootstrap  
- **APIs**: Yahoo Finance (for stock price data)  
- **Security**: Werkzeug password hashing, Flask-Session  
- **Database**: CS50 SQL wrapper for SQLite  

---

## Installation & Setup 💻  

### Prerequisites  
- Python 3.8+  
- pip package manager  


### Steps  
1. **Clone Repository**  
   ```bash
   git clone https://github.com/yourusername/trade-it.git
   cd trade-it
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database**  
   - Create `finance.db` using this schema:  
     ```sql
     CREATE TABLE users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT NOT NULL UNIQUE,
         hash TEXT NOT NULL,
         cash NUMERIC NOT NULL DEFAULT 10000.00
     );

     CREATE TABLE transactions (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         symbol TEXT NOT NULL,
         shares INTEGER NOT NULL,
         price NUMERIC NOT NULL,
         total_price NUMERIC NOT NULL,
         balance NUMERIC NOT NULL,
         datetime DATETIME NOT NULL,
         sold_bought TEXT NOT NULL,
         FOREIGN KEY(user_id) REFERENCES users(id)
     );
     ```
   - Save as `schema.sql` and run:  
     ```bash
     sqlite3 finance.db < schema.sql
     ```

4. **Configure Environment**  
   ```bash
   export FLASK_APP=app.py      # Unix/Mac
   set FLASK_APP=app.py         # Windows
   ```

5. **Run Application**  
   ```bash
   flask run --debug
   ```  
   Access at: `http://localhost:5000`

---

## Usage Guide 📖  

1. **Registration**  
   - Visit `/register` to create an account  
   - Start with $10,000 virtual cash  

2. **Buy Stocks**  
   - Go to **Buy** tab  
   - Enter stock symbol (e.g., `AAPL` for Apple)  
   - Specify shares (whole numbers only)  
   - Confirm purchase  

3. **Sell Stocks**  
   - Navigate to **Sell** tab  
   - Select owned stock from dropdown  
   - Enter shares to sell  
   - Confirm transaction  

4. **Get Quotes**  
   - Visit **Quote** tab  
   - Enter any valid stock symbol  
   - See current price in USD  

5. **Portfolio**  
   - Homepage shows:  
     - Current stock holdings  
     - Available cash  
     - Total portfolio value  

6. **History**  
   - View all transactions in reverse chronological order  
   - Filter by buy/sell actions  

---

## Project Structure 📂  

```
trade-it/
├── app.py                 # Main Flask application
├── helpers.py             # Utility functions (quotes, auth)
├── requirements.txt       # Dependencies
├── finance.db             # SQLite database (auto-updated)
├── static/                # CSS/JS assets
├── templates/             # HTML templates
│   ├── layout.html        # Base template
│   ├── index.html         # Portfolio dashboard
│   ├── login.html         # Login form
│   ├── register.html      # Registration form
│   ├── buy.html           # Stock purchase interface
│   └── sell.html          # Stock selling interface
```

---

## Configuration ⚙️  
Customize in `app.py`:  
- `app.config["SESSION_TYPE"]`: Change session storage  
- `DEFAULT_CASH = 10000.00`: Adjust starting balance  
- `db = SQL("sqlite:///finance.db")`: Modify database path  

---

## Troubleshooting 🔧  

**Common Issues**:  
- **No Stock Data**: Ensure valid ticker symbol (e.g., `GOOG` not `GOOGLE`)  
- **Insufficient Funds**: Check cash balance before buying  
- **Missing Transactions**: Verify stock ownership before selling  
- **Database Errors**: Delete `finance.db` and reinitialize schema  

---

## Acknowledgments 🙏  
- CS50 for foundational code structure  
- Yahoo Finance for market data API  
- Flask community for web framework  

---

**Happy Trading!** 💸  
*Remember: Past performance is not indicative of future results.*
