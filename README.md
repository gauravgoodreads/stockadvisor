# stock advisor 📈

yo, this is my stock advisor project. i built it to be a mix of a trading sim and an ai-powered research tool. it's meant to look and feel like a professional terminal but with a personal touch.

## how it works (under the hood)
i wanted to make this more than just a simple crud app, so i added some actual math and ml:

- the engine: it's all in python/flask. i used sqlalchemy for the database. every time you buy or sell, it calculates a 0.1% brokerage fee (just like real brokers) and uses weighted average for the buy price. so if you buy 10 shares at 100 and 10 at 120, your avg is 110. pretty realistic.
- the ai (ml_pipeline.py): 
    - i used an lstm neural net (built with pytorch) to look at the last 60 days of prices and guess the next move. 
    - there's also a random forest classifier that checks the stock's volatility (annualized standard deviation) to label it as "high" or "low" risk.
    - it even calculates sma20 and sma50 on the fly and runs a sentiment heuristic to give you better context.
- the ui: it’s a custom "green-on-black" terminal. i used bootstrap for the grid but custom css to give it that hft (high frequency trading) vibe.

## features (the impressive stuff)
- ai scanner: lstm + random forest predictions.
- pro trading engine: handles fees, weighted averages, and real-time p&l.
- watchlist & history: persistent tracking across sessions.
- csv export: you can download your entire trade history as a .csv with one click.
- modern terminal: live system logs and status indicators.
- unit tests: i included test_engine.py to prove the core logic is solid.

## how to use it
it's super easy to get going:

1. setup: 
   - run pip install -r requirements.txt to get all the libraries (torch, yfinance, etc.).
   - run python app.py. it'll auto-create the database (advisor.db) and a demo user for you.
2. trading:
   - use real symbols like RELIANCE, TCS, or AAPL. if it’s an indian stock, you can just type the name and it'll auto-add .ns for you.
   - in the cmd: trade box, put the ticker, choose buy/sell, and hit execute.
3. watchlists & scanning:
   - add stocks to the watchlist sidebar.
   - hit scan in the advisor box to run the ai. it'll give you a confidence score, a target move, and the current market sentiment.
4. exporting & testing:
   - hit the export_csv link above the history to get your trade logs.
   - run pytest test_engine.py if you want to see the tests in action.

## project notes
- i used sqlite so you don't need to setup a big db.
- the data is live from yahoo finance, so it only works when you're online.

*made by gauravgoodreads*
