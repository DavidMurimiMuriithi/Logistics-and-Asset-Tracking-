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
        version=1,   # Controls the size of the QR Code (higher number = larger code)
        box_size=10, # Size of each box in pixels
        border=5     # Thickness of the border (default is 4)
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    return file_path

def create_shipment(inventory_id, customer_name, destination_address, 
                    shipment_status="dispatched", assigned_vehicle_id=None):
    """
    Create a shipment record for a given inventory item, generate a QR code for it,
    and insert the record into the shipments table.
    
    Parameters:
      - inventory_id: ID of the inventory item being shipped.
      - customer_name: Name of the customer.
      - destination_address: Destination address for the shipment.
      - shipment_status: Status of the shipment (default "dispatched").
      - assigned_vehicle_id: (Optional) ID of the vehicle assigned to the shipment.
    
    Returns:
      A tuple (shipment_id, qr_data) where:
        - shipment_id: The auto-generated ID of the shipment.
        - qr_data: The unique string stored in the QR code.
    """
    # Generate unique QR code data string using timestamp
    qr_data = f"shipment_{inventory_id}_{datetime.now().timestamp()}"
    
    # Ensure the directory for QR codes exists
    qr_dir = os.path.join("static", "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)
    
    # Define the file path to save the QR code image
    qr_image_path = os.path.join(qr_dir, f"{qr_data}.png")
    generate_qr_code(qr_data, qr_image_path)
    
    # Insert the shipment record into the database
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
        INSERT INTO shipments (inventory_id, customer_name, destination_address, 
                               shipment_status, assigned_vehicle_id, qr_code)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (inventory_id, customer_name, destination_address, 
                           shipment_status, assigned_vehicle_id, qr_data))
    connection.commit()
    shipment_id = cursor.lastrowid
    cursor.close()
    connection.close()
    
    return shipment_id, qr_data

def get_shipment_by_qr(qr_code):
    """
    Retrieve a shipment record from the database using its QR code.
    
    Parameters:
      - qr_code: The unique QR code string associated with the shipment.
    
    Returns:
      A dictionary containing the shipment details or None if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM shipments WHERE qr_code = %s"
    cursor.execute(sql, (qr_code,))
    shipment = cursor.fetchone()
    cursor.close()
    connection.close()
    return shipment

def get_shipment_by_id(shipment_id):
    """
    Retrieve a shipment record from the database using its shipment ID.
    
    Parameters:
      - shipment_id: The ID of the shipment.
    
    Returns:
      A dictionary containing the shipment details or None if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM shipments WHERE id = %s"
    cursor.execute(sql, (shipment_id,))
    shipment = cursor.fetchone()
    cursor.close()
    connection.close()
    return shipment

def update_shipment_status(shipment_id, new_status):
    """
    Update the status of a shipment.
    
    Parameters:
      - shipment_id: The ID of the shipment to update.
      - new_status: The new status value (e.g., 'in-transit', 'delivered').
    
    Returns:
      True if the update was successful.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "UPDATE shipments SET shipment_status = %s WHERE id = %s"
    cursor.execute(sql, (new_status, shipment_id))
    connection.commit()
    cursor.close()
    connection.close()
    return True

# For testing purposes, run this module directly
if __name__ == '__main__':
    # Example usage: create a new shipment
    inventory_id = 1  # Example inventory ID (replace with a valid ID from your database)
    customer_name = "John Doe"
    destination_address = "123 Rice Road, Nairobi, Kenya"
    shipment_id, qr_data = create_shipment(inventory_id, customer_name, destination_address)
    print("Created shipment with ID:", shipment_id)
    print("QR Code Data:", qr_data)
