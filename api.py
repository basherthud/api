from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship,Mapped ,mapped_column
from sqlalchemy import ForeignKey, Table, Column, String, Integer, select,UniqueConstraint, DateTime
from marshmallow import ValidationError
from typing import List, Optional
from datetime import datetime,timezone


# Initialize Flask app
app = Flask(__name__)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Ma878807j34u#@localhost/ecommerce_api_db2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

#MODELS

order_product = Table(
    "order_product",
    Base.metadata,
    Column("user_id", ForeignKey("user_account.id"), primary_key=True),
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)

)

class User(Base):
    __tablename__ = 'user_account'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
#relationship
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    order_date: Mapped[str] = mapped_column(DateTime ,default= datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey('user_account.id'), nullable=False)

#relationship
    user: Mapped[List["User"]]  = relationship("User",  back_populates="orders")
    products: Mapped[List["Product"]]  = relationship("Product", secondary="order_product", back_populates="orders")
    

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column( nullable=False)

#relationship
    orders: Mapped[List["Order"]]  = relationship("Order", secondary="order_product", back_populates="products")

    # User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
    # Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    #  user_id = fields.Int(required=False)
    #  order_date = fields.String(required=False)
     class Meta:
        # fields = ("id",DateTime)
        model = Order

    # Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
       
       
# Initialize Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True) 
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#User Endpoints 
#READ USERS
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

#READ INDIVIDUAL USER
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

#create a new
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'],address=user_data['address'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201
    
#UPDATE INDIVIDUAL USER
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200

#Delete A User
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"succefully deleted user {id}"}), 200

#Product Endpoints
#READ PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    users = db.session.execute(query).scalars().all()

    return products_schema.jsonify(users), 200

#READ INDIVIDUAL PRODUCT
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    user = db.session.get(Product, id)
    return product_schema.jsonify(user), 200

#CREATE A NEW PRODUCT
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201
    
#UPDATE INDIVIDUAL PRODUCT
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']

    db.session.commit()
    return product_schema.jsonify(product), 200

#Delete A PRODUCT
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(User, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"succefully deleted product {id}"}), 200

#ORDER ENDPOINTS
# creation of a new order with user ID and order date
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(order_date=order_data['order_date'], user_id=order_data['user_id'])
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201

#ADD PRODUCT TO ORDER
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['GET'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order not in product:
        return jsonify({"message": "Order not found"}), 404

    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400
    
    new_product = Product['product_id'].append(order_id)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify({"message": f"Product {product.id} added to your order {order_id}"}), 200
    
#DELETE PRODUCT FROM ORDER
@app.route('/orders/<int:order_id>/remove_product', methods=['DELETE'])
def remove_product_from_order(order_id,product_id):
    product = db.session.get(Product, product_id)
    order = db.session.get(Order,order_id)

    if not order or not product:
        return jsonify({"message": "Invalid product/order id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"succefully deleted product {order.id}"}), 200

#GET ALL ORDERS FOR USER
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_for_user(user_id):
    orders = db.session.get(User,user_id)

    if not orders:
        return jsonify({'message''Not Found'}),404
    
    return orders_schema.jsonify(orders), 200

# GETTING ALL PRODUCTS FOR ORDER
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_for_order(order_id,product_id):
    query = select(Product,product_id, Order,order_id)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify({"message": f"Products for order {products}"}), 200

if __name__ == '__main__':

    with app.app_context():
        #db.drop_all()
        db.create_all()

    app.run(debug=True)