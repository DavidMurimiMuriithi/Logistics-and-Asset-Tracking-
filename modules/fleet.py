import mysql.connector
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

def update_fleet_route(vehicle_id, shipment_id, latitude, longitude, timestamp=None):
    """
    Insert a new fleet route record into the fleet_routes table with GPS data.
    
    Parameters:
      - vehicle_id: ID of the vehicle.
      - shipment_id: (Optional) ID of the shipment associated with the route.
      - latitude: Latitude coordinate.
      - longitude: Longitude coordinate.
      - timestamp: (Optional) Timestamp of the GPS data. If not provided, the current time is used.
    
    Returns:
      True if the insertion is successful.
    """
    # Use current time if timestamp is not provided
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
        INSERT INTO fleet_routes (vehicle_id, shipment_id, latitude, longitude, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (vehicle_id, shipment_id, latitude, longitude, timestamp))
    connection.commit()
    cursor.close()
    connection.close()
    
    return True

def get_routes_by_vehicle(vehicle_id):
    """
    Retrieve all fleet route records for a specific vehicle.
    
    Parameters:
      - vehicle_id: The ID of the vehicle.
    
    Returns:
      A list of dictionaries, each representing a route record.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM fleet_routes WHERE vehicle_id = %s ORDER BY timestamp ASC"
    cursor.execute(sql, (vehicle_id,))
    routes = cursor.fetchall()
    cursor.close()
    connection.close()
    return routes

def get_routes_by_shipment(shipment_id):
    """
    Retrieve all fleet route records associated with a specific shipment.
    
    Parameters:
      - shipment_id: The ID of the shipment.
    
    Returns:
      A list of dictionaries, each representing a route record.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM fleet_routes WHERE shipment_id = %s ORDER BY timestamp ASC"
    cursor.execute(sql, (shipment_id,))
    routes = cursor.fetchall()
    cursor.close()
    connection.close()
    return routes

# For testing purposes: Run this module directly to insert a sample route record.
if __name__ == '__main__':
    # Sample data to update fleet route
    vehicle_id = 1        # Replace with a valid vehicle ID from your database
    shipment_id = 1       # Replace with a valid shipment ID (or None if not applicable)
    latitude = -1.2921    # Example: Latitude for Nairobi, Kenya
    longitude = 36.8219   # Example: Longitude for Nairobi, Kenya
    
    success = update_fleet_route(vehicle_id, shipment_id, latitude, longitude)
    if success:
        print("Fleet route updated successfully.")
    
    # Retrieve and display routes for the sample vehicle
    routes = get_routes_by_vehicle(vehicle_id)
    for route in routes:
        print(route)
