"""
trading_engine.py
-----------------
added watchlist logic and better history logging.
"""
import yfinance as yf
from datetime import datetime, timedelta
from models import db, User, Portfolio, History, TradeType, Watchlist

FEE = 0.001 
MY_STOCKS = {'RELIANCE', 'TCS', 'INFY', 'SBIN', 'TATAMOTORS'}

def fix_t(t):
    t = t.strip().upper()
    if any(t.endswith(s) for s in ['.NS', '.BO']): return t
    if t in MY_STOCKS: return f"{t}.NS"
    return t

p_cache = {}

def get_p(s):
    s = fix_t(s)
    if s in p_cache:
        val, ts = p_cache[s]
        if datetime.now() - ts < timedelta(minutes=5):
            return {'ok': True, 'p': val, 's': s}
    try:
        t = yf.Ticker(s)
        df = t.history(period='1d')
        if df.empty: return {'ok': False, 'err': "err"}
        val = round(float(df['Close'].iloc[-1]), 2)
        p_cache[s] = (val, datetime.now())
        return {'ok': True, 'p': val, 's': s}
    except:
        return {'ok': False, 'err': "yf error"}

def buy(uid, s, q):
    if q <= 0: return {'status': 'err', 'msg': "qty?"}
    u = User.query.get(uid)
    res = get_p(s)
    if not res['ok']: return {'status': 'err', 'msg': res['err']}
    price, s = res['p'], res['s']
    net = price * q
    fees = net * FEE
    total = net + fees
    if u.balance < total: return {'status': 'err', 'msg': "no cash"}
    u.balance -= total
    hold = Portfolio.query.filter_by(uid=uid, symbol=s).first()
    if hold:
        old_val = hold.qty * hold.avg_p
        new_val = q * price
        hold.avg_p = (old_val + new_val) / (hold.qty + q)
        hold.qty += q
    else:
        hold = Portfolio(uid=uid, symbol=s, qty=q, avg_p=price)
        db.session.add(hold)
    log = History(uid=uid, symbol=s, otype=TradeType.BUY, qty=q, price=price)
    db.session.add(log)
    db.session.commit()
    return {'status': 'ok', 'msg': f"bought {q} {s}"}

def sell(uid, s, q):
    if q <= 0: return {'status': 'err', 'msg': "qty?"}
    u = User.query.get(uid)
    s = fix_t(s)
    hold = Portfolio.query.filter_by(uid=uid, symbol=s).first()
    if not hold or hold.qty < q: return {'status': 'err', 'msg': "no shares"}
    res = get_p(s)
    if not res['ok']: return {'status': 'err', 'msg': res['err']}
    price = res['p']
    raw, fees = price * q, (price * q) * FEE
    u.balance += (raw - fees)
    hold.qty -= q
    if hold.qty == 0: db.session.delete(hold)
    log = History(uid=uid, symbol=s, otype=TradeType.SELL, qty=q, price=price)
    db.session.add(log)
    db.session.commit()
    return {'status': 'ok', 'msg': f"sold {q} {s}"}

# --- Watchlist Logic ---

def toggle_watch(uid, s):
    s = fix_t(s)
    w = Watchlist.query.filter_by(uid=uid, symbol=s).first()
    if w:
        db.session.delete(w)
        db.session.commit()
        return {'status': 'ok', 'msg': f"removed {s}"}
    else:
        w = Watchlist(uid=uid, symbol=s)
        db.session.add(w)
        db.session.commit()
        return {'status': 'ok', 'msg': f"added {s}"}

def get_watchlist(uid):
    ws = Watchlist.query.filter_by(uid=uid).all()
    rows = []
    for w in ws:
        p_res = get_p(w.symbol)
        rows.append({'s': w.symbol, 'p': p_res['p'] if p_res['ok'] else '--'})
    return rows

# --- Snapshot Logic ---

def get_snapshot(uid):
    u = User.query.get(uid)
    if not u: return None
    data = Portfolio.query.filter_by(uid=uid).all()
    rows = []
    v_total, pnl_total = 0, 0
    for d in data:
        p_res = get_p(d.symbol)
        now_p = p_res['p'] if p_res['ok'] else d.avg_p
        m_val, total_c = d.qty * now_p, d.qty * d.avg_p
        pnl = m_val - total_c
        v_total += m_val
        pnl_total += pnl
        rows.append({
            's': d.symbol, 'q': d.qty, 'avg': round(d.avg_p, 2),
            'p': now_p, 'val': round(m_val, 2), 'pnl': round(pnl, 2),
            'pct': round((pnl/total_c*100), 2) if total_c > 0 else 0
        })
    # history
    hist = [h.to_json() for h in History.query.filter_by(uid=uid).order_by(History.dt.desc()).limit(10).all()]
    return {
        'cash': round(u.balance, 2),
        'portfolio': round(v_total, 2),
        'net': round(u.balance + v_total, 2),
        'pnl': round(pnl_total, 2),
        'stocks': rows,
        'history': hist,
        'watchlist': get_watchlist(uid)
    }
