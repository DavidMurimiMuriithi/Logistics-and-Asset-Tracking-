import mysql.connector

def get_db_connection():
    """
    Establish and return a connection to the MySQL database.
    Update the host, user, password, and database parameters as needed.
    """
    connection = mysql.connector.connect(
   host='localhost',
        user='root',      # Replace with your MySQL username
        password='',  # Replace with your MySQL password
        database='mwea_logistics' 
    )
    return connection

def create_payment(shipment_id, payment_method, payment_status, transaction_details):
    """
    Create a new payment record for a given shipment.
    
    Parameters:
        - shipment_id: The ID of the shipment being paid for.
        - payment_method: The method of payment (e.g., 'mpesa', 'cheque').
        - payment_status: The status of the payment (e.g., 'completed', 'pending').
        - transaction_details: A text description or transaction details.
        
    Returns:
        The newly created payment record's ID.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
        INSERT INTO payments (shipment_id, payment_method, payment_status, transaction_details)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (shipment_id, payment_method, payment_status, transaction_details))
    connection.commit()
    payment_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return payment_id

def get_payment_by_id(payment_id):
    """
    Retrieve a payment record from the database using its ID.
    
    Parameters:
        - payment_id: The ID of the payment.
        
    Returns:
        A dictionary containing the payment details, or None if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM payments WHERE id = %s"
    cursor.execute(sql, (payment_id,))
    payment = cursor.fetchone()
    cursor.close()
    connection.close()
    return payment

def update_payment_status(payment_id, new_status):
    """
    Update the status of an existing payment.
    
    Parameters:
        - payment_id: The ID of the payment to update.
        - new_status: The new status value (e.g., 'completed', 'failed').
        
    Returns:
        True if the update was successful.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "UPDATE payments SET payment_status = %s WHERE id = %s"
    cursor.execute(sql, (new_status, payment_id))
    connection.commit()
    cursor.close()
    connection.close()
    return True

def get_payments_by_shipment(shipment_id):
    """
    Retrieve all payment records associated with a specific shipment.
    
    Parameters:
        - shipment_id: The ID of the shipment.
        
    Returns:
        A list of dictionaries, each containing payment details.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM payments WHERE shipment_id = %s"
    cursor.execute(sql, (shipment_id,))
    payments = cursor.fetchall()
    cursor.close()
    connection.close()
    return payments

# For testing purposes: Run this module directly to create and fetch a payment record.
if __name__ == '__main__':
    # Example usage: Create a payment record for shipment with ID 1.
    shipment_id = 1
    payment_method = "mpesa"
    payment_status = "completed"
    transaction_details = "MPESA transaction simulated"
    
    payment_id = create_payment(shipment_id, payment_method, payment_status, transaction_details)
    print("Created Payment ID:", payment_id)
    
    # Retrieve and display the payment record
    payment = get_payment_by_id(payment_id)
    print("Payment Details:", payment)
