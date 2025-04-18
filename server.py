from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/get_categories')
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        categories = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify(categories)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/get_menu_items')
def get_menu_items():
    try:
        category_id = request.args.get('id', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not category_id:
            return jsonify([])
        
        cursor.execute("SELECT * FROM menu_items WHERE category_id = ?", (category_id,))
        items = [{'name': row[1], 'price': row[2]} for row in cursor.fetchall()]
        return jsonify(items)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)