from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Define the model for the items table
class Item(db.Model):
    __tablename__ = 'items'
    Item_Id = db.Column(db.Integer, primary_key=True, unique=True)
    Category = db.Column(db.String(50), nullable=False)
    Category_Id = db.Column(db.Integer, nullable=False)
    Item_name = db.Column(db.String(100), nullable=False)
    Quantity_Available = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

# Create the database
def create_tables():
    db.create_all()

# Categories Create Endpoint
@app.route('/categories/create', methods=['POST'])
def create_category():
    data = request.json
    category = data.get('Category')
    category_id = data.get('Category_Id')

    # Create a new item with category info, even if no item yet
    item = Item(Category=category, Category_Id=category_id, Item_name='', Item_Id=0, Quantity_Available=0, unit_price=0)
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Category created successfully!'})

# Categories Delete Endpoint
@app.route('/categories/delete', methods=['DELETE'])
def delete_category():
    data = request.json
    category_id = data.get('Category_Id')

    Item.query.filter_by(Category_Id=category_id).delete()
    db.session.commit()

    return jsonify({'message': 'Category deleted successfully!'})

# Items Create Endpoint
@app.route('/categories/items/create', methods=['POST'])
def create_item():
    data = request.json
    item = Item(
        Category=data['Category'],
        Category_Id=data['Category_Id'],
        Item_name=data['Item_name'],
        Item_Id=data['Item_Id'],
        Quantity_Available=data['Quantity_Available'],
        unit_price=data['unit_price']
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Item created successfully!'})

# Items Delete Endpoint
@app.route('/categories/items/delete', methods=['DELETE'])
def delete_item():
    data = request.json
    item_id = data.get('Item_Id')

    Item.query.filter_by(Item_Id=item_id).delete()
    db.session.commit()

    return jsonify({'message': 'Item deleted successfully!'})

# Inventory List Endpoint
@app.route('/categories/items/inventory/list', methods=['GET'])
def list_inventory():
    items = Item.query.all()
    inventory_list = [
        {
            "Category": item.Category,
            "Category_Id": item.Category_Id,
            "Item_name": item.Item_name,
            "Item_Id": item.Item_Id,
            "Quantity_Available": item.Quantity_Available,
            "unit_price": item.unit_price
        }
        for item in items
    ]
    return jsonify(inventory_list)

# Append Object to Inventory Endpoint
@app.route('/categories/items/inventory/append_object', methods=['PUT'])
def append_inventory():
    data = request.json
    item = Item.query.filter_by(Item_Id=data['Item_Id']).first()

    if item:
        item.Quantity_Available += data.get('Quantity', 0)
        db.session.commit()

    return jsonify({'message': 'Inventory updated successfully!'})

# Remove Object from Inventory Endpoint
@app.route('/categories/items/inventory/remove_object', methods=['PUT'])
def remove_inventory():
    data = request.json
    item = Item.query.filter_by(Item_Id=data['Item_Id']).first()

    if item:
        item.Quantity_Available -= data.get('Quantity', 0)
        if item.Quantity_Available < 0:
            item.Quantity_Available = 0
        db.session.commit()

    return jsonify({'message': 'Inventory reduced successfully!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)