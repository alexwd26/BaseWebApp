from flask import Flask, jsonify, request
import mysql.connector
import os # For potentially using environment variables for credentials

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Database Configuration ---
# IMPORTANT: Replace placeholders with your actual database credentials.
# Consider using environment variables for better security in production.
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),      # Replace 'localhost' if needed
    'user': os.getenv('DB_USER', 'your_api_user'), # Replace with your specific API user
    'password': os.getenv('DB_PASSWORD', 'your_api_password'), # Replace with the user's password
    'database': os.getenv('DB_NAME', 'food_delivery_service') # Your database name
}

# --- Database CRUD Helper Functions ---

def db_connect():
    """Establishes a database connection."""
    try:
        cnx = mysql.connector.connect(**db_config)
        return cnx
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        # In a real app, you'd likely log this error more formally
        return None

def create_record(table_name, data):
    """Creates a new record in the specified table."""
    cnx = db_connect()
    if not cnx:
        return None, "Database connection failed"

    cursor = None
    try:
        cursor = cnx.cursor()
        columns = ', '.join(f"`{col}`" for col in data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        values = list(data.values())

        cursor.execute(query, values)
        cnx.commit()
        return cursor.lastrowid, None # Return the ID of the new row
    except mysql.connector.Error as err:
        print(f"Error creating record in {table_name}: {err}")
        return None, str(err)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

def read_records(table_name, record_id=None, condition=None):
    """Reads records from the specified table based on ID or condition."""
    cnx = db_connect()
    if not cnx:
        return None, "Database connection failed"

    cursor = None
    try:
        # dictionary=True returns results as dictionaries (JSON-friendly)
        cursor = cnx.cursor(dictionary=True)
        query = f"SELECT * FROM `{table_name}`"
        params = []

        if record_id is not None:
            query += " WHERE `id` = %s"
            params.append(record_id)
        elif condition:
            # WARNING: Directly using 'condition' can be risky.
            # For production, implement safer filtering (e.g., parse specific fields).
            query += f" WHERE {condition}" # Example: "role = 'customer'"

        cursor.execute(query, params)
        results = cursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        print(f"Error reading records from {table_name}: {err}")
        return None, str(err)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

def update_record(table_name, record_id, data):
    """Updates a record in the specified table based on its ID."""
    cnx = db_connect()
    if not cnx:
        return None, "Database connection failed"

    cursor = None
    try:
        cursor = cnx.cursor()
        set_clauses = ', '.join(f"`{col}` = %s" for col in data.keys())
        query = f"UPDATE `{table_name}` SET {set_clauses} WHERE `id` = %s"
        values = list(data.values()) + [record_id]

        cursor.execute(query, values)
        cnx.commit()
        return cursor.rowcount, None # Return number of affected rows
    except mysql.connector.Error as err:
        print(f"Error updating record in {table_name} (ID {record_id}): {err}")
        return None, str(err)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

def delete_record(table_name, record_id):
    """Deletes a record from the specified table based on its ID."""
    cnx = db_connect()
    if not cnx:
        return None, "Database connection failed"

    cursor = None
    try:
        cursor = cnx.cursor()
        query = f"DELETE FROM `{table_name}` WHERE `id` = %s"
        cursor.execute(query, (record_id,))
        cnx.commit()
        return cursor.rowcount, None # Return number of affected rows
    except mysql.connector.Error as err:
        print(f"Error deleting record from {table_name} (ID {record_id}): {err}")
        return None, str(err)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

# --- API Endpoints ---

# List of tables allowed for API operations (for basic security)
ALLOWED_TABLES = {
    'users', 'restaurants', 'menu_items', 'orders',
    'order_items', 'delivery_addresses', 'promotions'
    # Add 'order_promotions' if needed
}

def validate_table_name(table_name):
    if table_name not in ALLOWED_TABLES:
        return False, jsonify({'error': f'Access to table "{table_name}" is forbidden'}), 403
    return True, None

@app.route('/api/<string:table_name>', methods=['POST'])
def api_create(table_name):
    """API Endpoint: Create a new record."""
    allowed, error_response = validate_table_name(table_name)
    if not allowed:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid or missing JSON data in request body'}), 400

    new_id, err = create_record(table_name, data)

    if err:
        # Check for specific errors if needed (e.g., duplicate entry)
        return jsonify({'error': f'Database error creating record: {err}'}), 500
    if new_id is not None:
        # Fetch the newly created record to return it
        created_record, fetch_err = read_records(table_name, record_id=new_id)
        if fetch_err:
             return jsonify({'id': new_id, 'message': 'Record created, but failed to fetch details.'}), 201 # Return 201 Created
        if created_record:
             return jsonify(created_record[0]), 201 # Return 201 Created
        else:
             return jsonify({'id': new_id, 'message': 'Record created, but could not be found immediately.'}), 201
    else:
        # Should not happen if err is None, but as a safeguard
        return jsonify({'error': 'Failed to create record for an unknown reason'}), 500

@app.route('/api/<string:table_name>', methods=['GET'])
def api_read_all(table_name):
    """API Endpoint: Read all records (with optional filter)."""
    allowed, error_response = validate_table_name(table_name)
    if not allowed:
        return error_response

    # Basic filtering example (use with caution)
    condition = request.args.get('where')
    records, err = read_records(table_name, condition=condition)

    if err:
        return jsonify({'error': f'Database error reading records: {err}'}), 500
    if records is not None:
        return jsonify(records)
    else:
         # This case might indicate the db connection failed initially in read_records
        return jsonify({'error': 'Failed to retrieve records'}), 500


@app.route('/api/<string:table_name>/<int:record_id>', methods=['GET'])
def api_read_one(table_name, record_id):
    """API Endpoint: Read a specific record by ID."""
    allowed, error_response = validate_table_name(table_name)
    if not allowed:
        return error_response

    records, err = read_records(table_name, record_id=record_id)

    if err:
        return jsonify({'error': f'Database error reading record: {err}'}), 500

    if records is not None:
        if records:
            return jsonify(records[0]) # Return the single record found
        else:
            return jsonify({'error': f'Record with ID {record_id} not found in {table_name}'}), 404
    else:
        return jsonify({'error': 'Failed to retrieve record'}), 500


@app.route('/api/<string:table_name>/<int:record_id>', methods=['PUT', 'PATCH'])
def api_update(table_name, record_id):
    """API Endpoint: Update an existing record by ID."""
    allowed, error_response = validate_table_name(table_name)
    if not allowed:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid or missing JSON data in request body'}), 400

    rows_affected, err = update_record(table_name, record_id, data)

    if err:
        return jsonify({'error': f'Database error updating record: {err}'}), 500

    if rows_affected is not None:
        if rows_affected > 0:
             # Fetch the updated record to return it
            updated_record, fetch_err = read_records(table_name, record_id=record_id)
            if fetch_err:
                return jsonify({'message': f'Record {record_id} updated, but failed to fetch details.'}), 200 # OK
            if updated_record:
                return jsonify(updated_record[0]), 200 # OK
            else:
                 # Should not happen if rows_affected > 0 but record now missing
                 return jsonify({'message': f'Record {record_id} updated, but could not be found immediately.'}), 200
        else:
            # Check if the record actually exists before saying "not found"
            existing_record, _ = read_records(table_name, record_id=record_id)
            if not existing_record:
                 return jsonify({'error': f'Record with ID {record_id} not found in {table_name}'}), 404
            else:
                 # Record exists, but nothing was changed (e.g., same data sent)
                 return jsonify(existing_record[0]), 200 # Or maybe 304 Not Modified? 200 is simpler.
    else:
        return jsonify({'error': 'Failed to update record'}), 500


@app.route('/api/<string:table_name>/<int:record_id>', methods=['DELETE'])
def api_delete(table_name, record_id):
    """API Endpoint: Delete a record by ID."""
    allowed, error_response = validate_table_name(table_name)
    if not allowed:
        return error_response

    # Optional: Check if record exists before deleting
    existing_record, _ = read_records(table_name, record_id=record_id)
    if not existing_record:
        return jsonify({'error': f'Record with ID {record_id} not found in {table_name}'}), 404

    rows_affected, err = delete_record(table_name, record_id)

    if err:
         # Check for foreign key constraints if needed
        return jsonify({'error': f'Database error deleting record: {err}'}), 500

    if rows_affected is not None:
        if rows_affected > 0:
            # Success - return No Content or a success message
            # return '', 204 # No Content is common for DELETE
            return jsonify({'message': f'Record {record_id} from {table_name} deleted successfully.'}), 200 # OK
        else:
            # Should have been caught by the check above, but handle just in case
             return jsonify({'error': f'Record with ID {record_id} not found in {table_name} (delete failed)'}), 404
    else:
        return jsonify({'error': 'Failed to delete record'}), 500


# --- Main Execution ---
if __name__ == '__main__':
    # Set debug=False for production!
    # host='0.0.0.0' makes the server accessible from your network, not just localhost.
    print("Starting Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)