"""
models.py
---------
database models for the advisor. added a watchlist.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class TradeType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Float, default=100000.0) 
    
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)
    history = db.relationship('History', backref='user', lazy=True)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)
    avg_p = db.Column(db.Float, nullable=False, default=0.0)
    __table_args__ = (db.UniqueConstraint('uid', 'symbol', name='_u_s_uc'),)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    __table_args__ = (db.UniqueConstraint('uid', 'symbol', name='_u_w_uc'),)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    otype = db.Column(db.Enum(TradeType), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    dt = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'symbol': self.symbol,
            'type': self.otype.value,
            'qty': self.qty,
            'price': self.price,
            'date': self.dt.strftime('%H:%M:%S') # just time is cooler for terminal
        }
