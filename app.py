from datetime import datetime
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Correct the SQL query to properly group by symbol and sum the shares and total_price
    summary = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares, AVG(price) AS price_per_share, SUM(total_price) AS total_price_of_shares "
        "FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"]
    )

    """Show portfolio of stocks"""
    # Fetch the user's cash balance
    cash_summary = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    if not cash_summary or cash_summary[0]["cash"] is None:
        return apology("Could not fetch cash balance", 403)

    cash = round(cash_summary[0]["cash"], 2)

    # Fetch the total value of stocks
    total_stock_price = db.execute("SELECT SUM(total_price) AS total_s_price FROM transactions WHERE user_id = ?", session["user_id"])
    total_s_price = total_stock_price[0]["total_s_price"] if total_stock_price[0]["total_s_price"] is not None else 0

    # Calculate the total value (cash + total stock price)
    total_value = total_s_price + cash

    return render_template("index.html", summary=summary, cash=cash, total=total_value)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate inputs
        if not symbol:
            return apology("Must provide company ticker symbol", 400)
        if not shares:
            return apology("Must provide number of shares", 400)
        if not shares.isdigit():
            return apology("Shares must be a positive integer", 400)

        shares = int(shares)
        if shares <= 0:
            return apology("Must provide a positive number of shares", 400)

        # Lookup stock information
        info = lookup(symbol)
        if info is None or "price" not in info:
            return apology("Ticker doesn't exist, please enter a valid ticker symbol", 400)

        # Calculate total price
        price = round(float(info["price"]), 2)
        total_price = round(shares * price, 2)

        # Get user's cash balance
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if not cash or cash[0]["cash"] is None:
            return apology("Could not fetch cash balance", 400)

        balance = round(cash[0]["cash"] - total_price, 2)
        if balance < 0:
            return apology("Insufficient balance", 400)

        # Update user's cash balance and record the transaction
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, total_price, balance, datetime, sold_bought) VALUES (?, ?, ?, ?, ?, ?, ?, 'BOUGHT')",
                   session["user_id"], symbol, shares, price, total_price, balance, datetime.now())

        return render_template("buy.html", balance=balance, symbol=info["symbol"], total_price=total_price, price=price, shares=shares)

    else:
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if not cash or cash[0]["cash"] is None:
            return apology("Could not fetch cash balance", 400)

        return render_template("buy.html", balance=round(cash[0]["cash"], 2))


@app.route("/history")
@login_required
def history():
    history = db.execute("SELECT symbol, shares, price, total_price, datetime, sold_bought FROM transactions WHERE user_id = ?", session["user_id"])

    if history is None or len(history) == 0:
        return apology("No transactions have been done", 400)

    """Show history of transactions"""
    for i in range(len(history)):
        history[i]['shares'] = abs(history[i]['shares'])
        history[i]['total_price'] = abs(history[i]['total_price'])

    return render_template("history.html", history=history)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide company ticker symbol", 400)
        else:
            symbol = request.form.get("symbol")
            info = lookup(symbol)
            if info is None:
                return apology("Invalid ticker symbol", 400)
            return render_template("quoted.html", symbol=info["symbol"], price=usd(info["price"]))
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if username or password fields are empty
        if not username or not password or not confirmation:
            return apology("All fields must be filled.", 400)

        # Check if the passwords match
        if password != confirmation:
            return apology("Passwords do not match.", 400)

        # Check if the username already exists
        exist = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )
        if len(exist) != 0:
            return apology("Username already exist, try different username.", 400)

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store the new user into the user table
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?,?)", username, hashed_password
        )
        # Redirect to login page or any other page
        return redirect("/login")

    # If it's a GET request, render the registration form
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate inputs
        if not symbol:
            return apology("Must provide company ticker symbol", 400)
        if not shares:
            return apology("Must provide number of shares", 400)
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Shares must be a positive number", 400)
        except ValueError:
            return apology("Shares must be an integer", 400)

        # Lookup stock information
        info = lookup(symbol)
        if info is None:
            return apology("Ticker doesn't exist", 400)

        # Check if the user owns the stock and has enough shares to sell
        user_shares = db.execute("SELECT SUM(shares) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
                                 session["user_id"], symbol)
        if not user_shares or user_shares[0]["total_shares"] < shares:
            return apology("You don't have enough shares to sell", 400)

        # Calculate total price
        shares = -shares  # Negative value to indicate selling
        total_price = shares * round(float(info["price"]), 2)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = cash[0]["cash"] - round(total_price, 2)

        # Update user's cash balance and record the transaction
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, total_price, balance, datetime, sold_bought) VALUES (?, ?, ?, ?, ?, ?, ?, 'SOLD')",
                   session["user_id"], symbol, shares, round(float(info["price"]), 2), round(total_price, 2), round(balance, 2), datetime.now())

        return redirect("/")
    else:
        # Get a list of the user's stocks to populate the dropdown in the sell form
        user_stocks = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
        return render_template("sell.html", stocks=user_stocks)
