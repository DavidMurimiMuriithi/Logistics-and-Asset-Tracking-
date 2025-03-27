import os
import mysql.connector
import qrcode
from datetime import datetime

def get_db_connection():
    """
    Establish and return a connection to the MySQL database.
    Update the host, user, password, and database parameters as needed.
    """
    connection = mysql.connector.connect(
        host='localhost',
        user='root',      # Replace with your MySQL username
        password='Mwea1234',  # Replace with your MySQL password
        database='mwea_logistics'
    )
    return connection

def generate_qr_code(data, file_path):
    """
    Generate a QR code image from the provided data and save it to file_path.
    """
    qr = qrcode.QRCode(
        version=1,       # controls the size of the QR Code; higher number means larger code
        box_size=10,     # size of each box in pixels
        border=5         # thickness of the border (default is 4)
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    return file_path

def create_inventory(product_name, batch_number, quantity, packaging_date):
    """
    Creates a new inventory record with a generated QR code.
    
    Parameters:
        product_name: Name of the product.
        batch_number: Batch identifier.
        quantity: Quantity available.
        packaging_date: Packaging date (in YYYY-MM-DD format).
        
    Returns:
        A tuple (inventory_id, qr_data) where:
          - inventory_id is the database-generated ID.
          - qr_data is the unique string stored in the QR code.
    """
    # Generate unique QR code data string
    qr_data = f"inventory_{batch_number}_{datetime.now().timestamp()}"
    
    # Ensure the directory for QR codes exists
    qr_dir = os.path.join('static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Define the file path to save the QR code image
    qr_image_path = os.path.join(qr_dir, f"{qr_data}.png")
    generate_qr_code(qr_data, qr_image_path)
    
    # Insert the new inventory item into the database
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
        INSERT INTO inventory (product_name, batch_number, quantity, packaging_date, qr_code)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (product_name, batch_number, quantity, packaging_date, qr_data))
    connection.commit()
    inventory_id = cursor.lastrowid
    cursor.close()
    connection.close()
    
    return inventory_id, qr_data

def get_inventory_by_id(inventory_id):
    """
    Retrieve a single inventory item from the database using its ID.
    Returns a dictionary with the inventory details or None if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM inventory WHERE id = %s"
    cursor.execute(sql, (inventory_id,))
    inventory_item = cursor.fetchone()
    cursor.close()
    connection.close()
    return inventory_item

def get_all_inventory():
    """
    Retrieve all inventory items from the database.
    Returns a list of dictionaries, each representing an inventory item.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM inventory"
    cursor.execute(sql)
    inventory_items = cursor.fetchall()
    cursor.close()
    connection.close()
    return inventory_items

# For testing purposes: Run this module directly to create a sample inventory record.
if __name__ == '__main__':
    product_name = "Mwea Rice"
    batch_number = "BATCH001"
    quantity = 1000
    packaging_date = "2025-03-01"
    
    inv_id, qr_data = create_inventory(product_name, batch_number, quantity, packaging_date)
    print("Created inventory with ID:", inv_id)
    print("QR Code Data:", qr_data)
import os
import mysql.connector
import qrcode
from datetime import datetime

def get_db_connection():
    """
    Establish and return a connection to the MySQL database.
    Update the host, user, password, and database parameters as needed.
    """
    connection = mysql.connector.connect(
        host='localhost',
        user='your_username',      # Replace with your MySQL username
        password='your_password',  # Replace with your MySQL password
        database='mwea_logistics'
    )
    return connection

def generate_qr_code(data, file_path):
    """
    Generate a QR code image from the provided data and save it to file_path.
    """
    qr = qrcode.QRCode(
        version=1,       # controls the size of the QR Code; higher number means larger code
        box_size=10,     # size of each box in pixels
        border=5         # thickness of the border (default is 4)
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    return file_path

def create_inventory(product_name, batch_number, quantity, packaging_date):
    """
    Creates a new inventory record with a generated QR code.
    
    Parameters:
        product_name: Name of the product.
        batch_number: Batch identifier.
        quantity: Quantity available.
        packaging_date: Packaging date (in YYYY-MM-DD format).
        
    Returns:
        A tuple (inventory_id, qr_data) where:
          - inventory_id is the database-generated ID.
          - qr_data is the unique string stored in the QR code.
    """
    # Generate unique QR code data string
    qr_data = f"inventory_{batch_number}_{datetime.now().timestamp()}"
    
    # Ensure the directory for QR codes exists
    qr_dir = os.path.join('static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Define the file path to save the QR code image
    qr_image_path = os.path.join(qr_dir, f"{qr_data}.png")
    generate_qr_code(qr_data, qr_image_path)
    
    # Insert the new inventory item into the database
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
        INSERT INTO inventory (product_name, batch_number, quantity, packaging_date, qr_code)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (product_name, batch_number, quantity, packaging_date, qr_data))
    connection.commit()
    inventory_id = cursor.lastrowid
    cursor.close()
    connection.close()
    
    return inventory_id, qr_data

def get_inventory_by_id(inventory_id):
    """
    Retrieve a single inventory item from the database using its ID.
    Returns a dictionary with the inventory details or None if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM inventory WHERE id = %s"
    cursor.execute(sql, (inventory_id,))
    inventory_item = cursor.fetchone()
    cursor.close()
    connection.close()
    return inventory_item

def get_all_inventory():
    """
    Retrieve all inventory items from the database.
    Returns a list of dictionaries, each representing an inventory item.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM inventory"
    cursor.execute(sql)
    inventory_items = cursor.fetchall()
    cursor.close()
    connection.close()
    return inventory_items

# For testing purposes: Run this module directly to create a sample inventory record.
if __name__ == '__main__':
    product_name = "Mwea Rice"
    batch_number = "BATCH001"
    quantity = 1000
    packaging_date = "2025-03-01"
    
    inv_id, qr_data = create_inventory(product_name, batch_number, quantity, packaging_date)
    print("Created inventory with ID:", inv_id)
    print("QR Code Data:", qr_data)
