from flask import Flask, jsonify

app = Flask(__name__)

# --- General API Endpoints ---


# --- Restaurant Endpoints ---

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """
    Lists all restaurants.
    """
    # In a real application, you would fetch data from a database.
    restaurants_data = [
        {"id": 1, "name": "Pizza Place A", "cuisine": "Italian"},
        {"id": 2, "name": "Burger Joint B", "cuisine": "American"}
    ]
    return jsonify(restaurants_data)

@app.route('/api/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """
    Retrieves details of a specific restaurant.
    """
    # In a real application, you would fetch data from a database based on restaurant_id.
    restaurant_data = {"id": restaurant_id, "name": f"Restaurant {restaurant_id}", "cuisine": "Example"}
    return jsonify(restaurant_data)

@app.route('/api/restaurants', methods=['POST'])
# In a real application, you would implement authentication and authorization here.
# Example: @jwt_required()
# Example: @has_role('admin')
def create_restaurant():
    """
    Creates a new restaurant (admin only).
    """
    # In a real application, you would:
    # 1. Get data from the request body (e.g., using request.get_json()).
    # 2. Validate the data.
    # 3. Save the new restaurant to the database.
    # 4. Return a success response (e.g., status code 201).
    new_restaurant = {"name": "New Restaurant", "cuisine": "Another Type"}
    return jsonify({"message": "Restaurant created successfully", "restaurant": new_restaurant}), 201

# ... (other endpoints) ...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



@app.route('/', methods=['GET'])
def home():
    """
    A simple welcome message for the API root.
    """
    return jsonify({"message": "Welcome to the Food Delivery Service API!"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint to check the health and status of the API.
    """
    return jsonify({"status": "OK", "message": "API is up and running"})

# --- Test Endpoint ---

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """
    A simple test endpoint to verify basic API functionality.
    """
    data = {"message": "This is a test endpoint response.", "timestamp": "now"}
    return jsonify(data)

if __name__ == '__main__':
    # In a real application, you would configure the host and port properly.
    # For development, running on localhost:5000 is common.
    app.run(debug=True, host='0.0.0.0', port=5000)