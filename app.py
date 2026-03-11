"""
server.py
---------
flask app for stock advisor.
author: gauravgoodreads
"""
import io
import csv
from flask import Flask, jsonify, request, render_template, make_response
from flask_cors import CORS
from datetime import datetime
from models import db, User, History
import trading_engine as core
import ml_pipeline as ml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advisor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'gaurav_key'

CORS(app)
db.init_app(app)

def bootstrap():
    db.create_all()
    # using gauravgoodreads as default user
    if not User.query.filter_by(name='gauravgoodreads').first():
        u = User(name='gauravgoodreads', balance=100000.0)
        db.session.add(u)
        db.session.commit()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/api/portfolio')
def get_p():
    v = core.get_snapshot(1)
    return jsonify({"status": "ok", "data": v}) if v else (jsonify({"status": "no user"}), 404)

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json
    s, o, q = data.get('s'), data.get('o'), data.get('q')
    res = core.buy(1, s, q) if o == 'BUY' else core.sell(1, s, q)
    return jsonify(res)

@app.route('/api/watch', methods=['POST'])
def watch():
    s = request.json.get('s')
    res = core.toggle_watch(1, s)
    return jsonify(res)

@app.route('/api/export')
def export_csv():
    hist = History.query.filter_by(uid=1).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Symbol', 'Type', 'Qty', 'Price', 'Date'])
    for h in hist:
        cw.writerow([h.symbol, h.otype.value, h.qty, h.price, h.dt.isoformat()])
    
    out = make_response(si.getvalue())
    out.headers["Content-Disposition"] = "attachment; filename=history.csv"
    out.headers["Content-type"] = "text/csv"
    return out

a_cache = {}

@app.route('/api/tip/<symbol>')
def info(symbol):
    symbol = symbol.upper()
    if symbol in a_cache:
        d, ts = a_cache[symbol]
        if (datetime.now() - ts).total_seconds() < 300:
            return jsonify({"status": "ok", "cached": True, **d})
    try:
        tip = ml.get_tip(symbol)
        p_res = core.get_p(symbol)
        tip['now'] = p_res['p'] if p_res['ok'] else 0
        a_cache[symbol] = (tip, datetime.now())
        return jsonify({"status": "ok", **tip})
    except Exception as ex:
        return jsonify({"status": "err", "ex": str(ex)}), 500

if __name__ == '__main__':
    with app.app_context():
        bootstrap()
    print("starting stock advisor...")
    app.run(debug=True, port=5000)
