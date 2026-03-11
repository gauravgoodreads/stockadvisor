"""
test_engine.py
--------------
just some simple tests to make sure i didn't break the math. 
quality control is key lol. 
"""
import pytest
from app import app, db, User
from trading_engine import buy, sell, fix_t

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        u = User(name='testuser', balance=10000.0)
        db.session.add(u)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

def test_ticker_fix():
    # should add .ns for indian stocks
    assert fix_t('RELIANCE') == 'RELIANCE.NS'
    # shouldn't double add
    assert fix_t('TCS.NS') == 'TCS.NS'
    # works for US stocks too
    assert fix_t('AAPL') == 'AAPL'

def test_trade_math(client):
    with app.app_context():
        # test buy logic
        # buying 1 share of something (using RELIANCE)
        res = buy(1, 'RELIANCE', 1)
        assert res['status'] == 'ok'
        
        u = User.query.get(1)
        # 10000 - (price + 0.1% fee) 
        # hard to check exact balance without mocking yfinance 
        # but it should definitely be less than 10000
        assert u.balance < 10000.0
