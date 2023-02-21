import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from data.raw_data import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


def commit_updated_data(data, table):
    """
    Update data and commit
    :param data:    - data for update
    :param table:   - table to be updated
    """
    with app.app_context():
        for k, v in data.items():
            setattr(table, k, v)
            db.session.add(table)
            db.session.commit()


def delete_row(row_data):
    with app.app_context():
        db.session.delete(row_data)
        db.session.commit()


def convert_date_format(data):
    result = []

    for dict_element in data:
        temp_dict = {}
        for k, v in dict_element.items():
            if k not in ('start_date', 'end_date'):
                temp_dict[k] = v
            else:
                temp_dict[k] = datetime.strptime(v, '%m/%d/%Y').date()
        result.append(temp_dict)
    return result


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name}"

    def data_pkg(self):
        return {column.name: getattr(self, column.name) for column in
                self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    order = db.relationship("Order", foreign_keys=[order_id])
    executor = db.relationship("User", foreign_keys=[executor_id])

    def data_pkg(self):
        return {column.name: getattr(self, column.name) for column in
                self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    customer = db.relationship("User", foreign_keys=[customer_id])
    executor = db.relationship("User", foreign_keys=[executor_id])

    def data_pkg(self):
        return {column.name: getattr(self, column.name) for column in
                self.__table__.columns}


with app.app_context():
    db.drop_all()
    db.create_all()

users_data = json.loads(users, strict=False)
offers_data = json.loads(offers, strict=False)
orders_data = json.loads(orders, strict=False)

all_users_to_model = [
    User(**user)
    for user in users_data
]

all_offers_to_model = [
    Offer(**offer)
    for offer in offers_data
]

all_orders_to_model = [
    Order(**order)
    for order in convert_date_format(orders_data)
]

with app.app_context():
    db.session.add_all(all_users_to_model)
    db.session.add_all(all_orders_to_model)
    db.session.add_all(all_offers_to_model)

    db.session.commit()


@app.route('/users/', methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'GET':
        user = [
            user.data_pkg()
            for user in User.query.all()
        ]
        return jsonify(user)
    elif request.method == 'POST':
        data = request.json
        user = User(**data)
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        return data


@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if request.method == 'GET':
        return jsonify(user.data_pkg())
    elif request.method == 'PUT':
        data_dict = request.json
        commit_updated_data(data_dict, user)
        return "success"
    elif request.method == 'DELETE':
        delete_row(user)
        return "success"
    return "failed"


@app.route('/orders/', methods=['GET', 'POST'])
def get_all_orders():
    if request.method == 'GET':
        all_orders = [
            all_orders.data_pkg()
            for all_orders in Order.query.all()
        ]
        return jsonify(all_orders)
    elif request.method == 'POST':
        data = request.json
        data['end_date'] = datetime.strptime(
            data['end_date'], '%m/%d/%Y'
        ).date()
        data['start_date'] = datetime.strptime(
            data['start_date'], '%m/%d/%Y'
        ).date()

        get_order = Order(**data)
        with app.app_context():
            db.session.add(get_order)
            db.session.commit()
        return data


@app.route('/orders/<int:order_id>', methods=['GET', 'PUT', 'DELETE'])
def get_order_by_id(order_id):
    one_order = Order.query.get(order_id)
    if request.method == 'GET':
        return jsonify(one_order.data_pkg())
    elif request.method == 'PUT':
        data_dict = request.json
        commit_updated_data(data_dict, one_order)
    elif request.method == 'DELETE':
        delete_row(one_order)
    return "success"


@app.route('/offers/', methods=['GET', 'POST'])
def get_all_offers():
    if request.method == 'GET':
        all_offers = [
            all_offers.data_pkg()
            for all_offers in Offer.query.all()
        ]
        return jsonify(all_offers)
    elif request.method == 'POST':
        data = request.json
        get_offer = Offer(**data)
        with app.app_context():
            db.session.add(get_offer)
            db.session.commit()
        return data


@app.route('/offers/<int:offer_id>', methods=['GET', 'PUT', 'DELETE'])
def get_offers_by_id(offer_id):
    one_offer = Offer.query.get(offer_id)
    if request.method == 'GET':

        return jsonify(one_offer.data_pkg())
    elif request.method == 'PUT':
        data_dict = request.json
        commit_updated_data(data_dict, one_offer)
        return "success"
    elif request.method == 'DELETE':
        delete_row(one_offer)
        return "success"
    return "failed"


if __name__ == '__main__':
    app.run(debug=True)
