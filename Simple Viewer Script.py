import mysql.connector

# Database connection details
db_config = {
    'host': '56.125.31.152',
    'user': 'root',
    'password': '88942604',
    'database': 'food_delivery_service'
}

def read_table_data(table_name):
    """Reads and prints all data from a specified table."""
    cnx = None  # Initialize cnx to None
    cursor = None # Initialize cursor to None
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = f"SELECT * FROM `{table_name}`"
        cursor.execute(query)

        print(f"\n--- Data from table: {table_name} ---")
        columns = [column[0] for column in cursor.description]
        print(f"Columns: {', '.join(columns)}")
        for row in cursor:
            print(row)

    except mysql.connector.Error as err:
        print(f"Error reading table {table_name}: {err}")
    finally:
        if cnx is not None and cnx.is_connected():
            cursor.close()
            cnx.close()
        elif cursor is not None:
            cursor.close() # Close cursor even if connection failed

if __name__ == "__main__":
    tables_to_read = [
        'users',
        'restaurants',
        'categories',
        'menu_items',
        'orders',
        'order_items',
        'delivery_addresses',
        'promotions',
        'order_promotions'
    ]

    for table in tables_to_read:
        read_table_data(table)