from flask import Flask, render_template, request, redirect, url_for, jsonify,  session, flash
from modules.shipments import create_shipment as create_shipment_record  # Import your shipment creation function
from modules.mpesa import lipa_na_mpesa_stk_push
import json
import mysql.connector
import qrcode
import os
from datetime import datetime
import pdfkit
from flask import make_response

app = Flask(__name__)
app.secret_key = '5797230ab95b595dd6e643d954f0460bb9f587b313e81f73' 
app.config['QR_CODES_DIR'] = os.path.join(os.getcwd(), 'static', 'qr_codes')
os.makedirs(app.config['QR_CODES_DIR'], exist_ok=True)
# -------------------------
# Database Connection Setup
# -------------------------



def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',      # Replace with your MySQL username
        password='davie1234',  # Replace with your MySQL password
        database='mwea_logistics'
    )
    return connection


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Successfully logged in as admin.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')
# -------------------------
# QR Code Generation Helper
# -------------------------
def generate_qr(data, file_path):
    """Generate a QR code image from provided data and save to file_path."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(file_path)
    return file_path

# -------------------------
# Flask Routes / Endpoints
# -------------------------

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/fleet_track')  # Or just '/' if it's your main page
def fleet_track():
    return render_template('fleet_track.html')


# Endpoint: Create a new inventory item with QR code generation
@app.route('/inventory/create', methods=['GET', 'POST'])
def create_inventory():
    if request.method == 'POST':
        product_name = request.form['product_name']
        batch_number = request.form['batch_number']
        quantity = request.form['quantity']
        packaging_date = request.form['packaging_date']  # Expected format: YYYY-MM-DD

        # Generate a unique QR code data string
        qr_data = f"inventory_{batch_number}_{datetime.now().timestamp()}"
        # Define directory and file path to save the QR code image
        qr_dir = os.path.join('static', 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        qr_image_path = os.path.join(qr_dir, f"{qr_data}.png")

        # Generate the QR Code image
        generate_qr(qr_data, qr_image_path)

        # Insert the inventory item into the database
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
            INSERT INTO inventory (product_name, batch_number, quantity, packaging_date, qr_code)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (product_name, batch_number, quantity, packaging_date, qr_data))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('index'))

    # For GET requests, render a template to create inventory
    return render_template('create_inventory.html')


# Endpoint: Retrieve shipment details based on QR code (for QR scanning)
# Route to display all shipments
@app.route('/shipments', methods=['GET'])
def shipments():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments")
    shipments = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('shipments.html', shipments=shipments)

# Route to delete a shipment by ID
@app.route('/delete_shipment/<int:shipment_id>', methods=['POST'])
def delete_shipment(shipment_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM shipments WHERE id = %s", (shipment_id,))
        connection.commit()
        flash("Shipment deleted successfully.", "success")
    except Exception as e:
        connection.rollback()
        flash(f"Error deleting shipment: {str(e)}", "danger")
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('shipments'))

# For testing: simple dashboard route (you can redirect to shipments if desired)
@app.route('/')
def dashboard():
    return redirect(url_for('shipments'))



# Endpoint: Process payment for a shipment (simplified example)
@app.route('/pay/<int:shipment_id>', methods=['GET', 'POST'])
def process_payment(shipment_id):
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        connection = get_db_connection()
        cursor = connection.cursor()

        # Simulate payment processing logic
        if payment_method == 'mpesa':
            transaction_details = "MPESA Transaction Simulated"
            payment_status = "completed"
        elif payment_method == 'cheque':
            transaction_details = "Cheque Payment Submitted"
            payment_status = "pending"
        else:
            transaction_details = "Unknown Payment Method"
            payment_status = "failed"

        sql = """
            INSERT INTO payments (shipment_id, payment_method, payment_status, transaction_details)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (shipment_id, payment_method, payment_status, transaction_details))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('shipment_details', qr_code=shipment_id))

    return render_template('payment.html', shipment_id=shipment_id)
@app.route('/create_shipment', methods=['GET', 'POST'])
def create_shipment():
    if request.method == 'POST':
        # Retrieve basic shipment details from the form
        inventory_id = request.form.get('inventory_id')
        customer_name = request.form.get('customer_name')
        destination_address = request.form.get('destination_address')
        invoice_no = request.form.get('invoice_no')
        route = request.form.get('route')
        vehicle_registration_no = request.form.get('vehicle_registration_no')
        assigned_vehicle_id = request.form.get('assigned_vehicle_id') or None
        
        shipment_status = "dispatched"
        
        # Insert the shipment record with a temporary empty qr_code
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            sql = """
                INSERT INTO shipments 
                (inventory_id, customer_name, destination_address, invoice_no, route, vehicle_registration_no, assigned_vehicle_id, shipment_status, qr_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            temp_qr = ""
            cursor.execute(sql, (inventory_id, customer_name, destination_address, invoice_no, route, vehicle_registration_no, assigned_vehicle_id, shipment_status, temp_qr))
            connection.commit()
            shipment_id = cursor.lastrowid
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
        
        # Process rice types (if any)
        rice_types = request.form.getlist('rice_types')
        for rice in rice_types:
            quantity = request.form.get(f'quantity_{rice}') or 0
            weight = request.form.get(f'weight_{rice}') or 0
            price = request.form.get(f'price_{rice}') or 0
            try:
                quantity = int(quantity)
                weight = float(weight)
                price = float(price)
            except:
                continue
            total_cost = weight * price
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                sql_item = """
                    INSERT INTO shipment_items (shipment_id, rice_type, quantity, weight, price_per_kg, total_cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_item, (shipment_id, rice, quantity, weight, price, total_cost))
                connection.commit()
            except Exception as e:
                connection.rollback()
                print("Error inserting shipment item:", e)
            finally:
                cursor.close()
                connection.close()
        
        # Generate Confirmation QR Code URL (for shipment confirmation)
        confirmation_url = url_for('confirm_shipment', shipment_id=shipment_id, _external=True)
        confirm_qr_filename = f"shipment_{shipment_id}_{int(datetime.now().timestamp())}.png"
        confirm_qr_image_path = os.path.join(app.config['QR_CODES_DIR'], confirm_qr_filename)
        generate_qr(confirmation_url, confirm_qr_image_path)
        confirm_qr_code_url = url_for('static', filename=f"qr_codes/{confirm_qr_filename}")
        
        # Generate Tracking QR Code URL (for tracking the shipment)
        # Here, we assume you have a fleet_track endpoint that accepts a shipment_id (adjust as needed)
        tracking_url = url_for('fleet_track', shipment_id=shipment_id, _external=True)
        tracking_qr_filename = f"tracking_{shipment_id}_{int(datetime.now().timestamp())}.png"
        tracking_qr_image_path = os.path.join(app.config['QR_CODES_DIR'], tracking_qr_filename)
        generate_qr(tracking_url, tracking_qr_image_path)
        tracking_qr_code_url = url_for('static', filename=f"qr_codes/{tracking_qr_filename}")
        
        # Update the shipment record with the generated confirmation QR code filename
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            update_sql = "UPDATE shipments SET qr_code = %s WHERE id = %s"
            cursor.execute(update_sql, (confirm_qr_filename, shipment_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
        
        # Render the form with both QR codes displayed
        return render_template('create_shipment.html', 
                               qr_code_url=confirm_qr_code_url, 
                               tracking_qr_code_url=tracking_qr_code_url)
    
    # For GET requests, simply render the form.
    return render_template('create_shipment.html')



@app.route('/confirm_shipment/<int:shipment_id>', methods=['GET', 'POST'])
def confirm_shipment(shipment_id):
    # Fetch shipment details and shipment items from the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments WHERE id = %s", (shipment_id,))
    shipment = cursor.fetchone()
    cursor.execute("SELECT * FROM shipment_items WHERE shipment_id = %s", (shipment_id,))
    shipment_items = cursor.fetchall()
    cursor.close()
    connection.close()
    
    if not shipment:
        return f"No shipment found with id {shipment_id}", 404

    # Compute grand total from shipment items
    grand_total = sum(item['total_cost'] for item in shipment_items)
    
    # Check if shipment is already confirmed and the user is not admin.
    if shipment['shipment_status'] == 'Received' and not session.get("is_admin"):
        message = "Shipment has already been confirmed. For modifications, please contact an administrator."
        return render_template('confirm_shipment_readonly.html',
                               shipment=shipment,
                               shipment_items=shipment_items,
                               grand_total=grand_total,
                               message=message)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        deposit_reference = None
        cheque_number = None
        mpesa_transaction = None
        
        if payment_method == 'mpesa':
            mpesa_phone = request.form.get('mpesa_phone')
            mpesa_transaction = request.form.get('mpesa_transaction')
            try:
                # Adjust the amount as required (you might use grand_total or a fixed value)
                amount = 100  
                result = lipa_na_mpesa_stk_push(mpesa_phone, amount, shipment['invoice_no'], "Payment for shipment delivery")
                mpesa_transaction = result.get("CheckoutRequestID", mpesa_transaction)
            except Exception as e:
                return jsonify({"error": f"MPESA STK push failed: {str(e)}"}), 500
        elif payment_method == 'bank_deposit':
            deposit_reference = request.form.get('deposit_reference')
        elif payment_method == 'cheque':
            cheque_number = request.form.get('cheque_number')
        
        # Update the shipment record with confirmation details
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            sql = """
                UPDATE shipments
                SET shipment_status = 'Received',
                    payment_method = %s,
                    deposit_reference = %s,
                    cheque_number = %s,
                    mpesa_transaction = %s,
                    confirmed_at = %s
                WHERE id = %s
            """
            confirmed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (payment_method, deposit_reference, cheque_number, mpesa_transaction, confirmed_at, shipment_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
        
        # Redirect to the fleet track page after successful confirmation
        return redirect(url_for('fleet_track'))
    
    # For GET requests, render the confirmation page with shipment details and grand total
    return render_template('confirm_shipment.html', 
                           shipment=shipment, 
                           shipment_items=shipment_items,
                           grand_total=grand_total)

#
# Example endpoint to confirm receipt of shipment
# This endpoint would be triggered when the customer scans the QR code and confirms receipt.
@app.route('/confirm_shipment/<int:shipment_id>', methods=['GET', 'POST'])
def confirm_shipment_page(shipment_id):
    # Fetch shipment details from database (you'll need to implement this)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments WHERE id = %s", (shipment_id,))
    shipment = cursor.fetchone()
    cursor.close()
    connection.close()

    if request.method == 'POST':
        # Process the payment details and update shipment status to 'Received'
        payment_method = request.form.get('payment_method')
        deposit_reference = request.form.get('deposit_reference')
        cheque_number = request.form.get('cheque_number')
        mpesa_transaction = request.form.get('mpesa_transaction')
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            sql = """
                UPDATE shipments
                SET shipment_status = 'Received', payment_method = %s, deposit_reference = %s,
                    cheque_number = %s, mpesa_transaction = %s
                WHERE id = %s
            """
            cursor.execute(sql, (payment_method, deposit_reference, cheque_number, mpesa_transaction, shipment_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
        return jsonify({"message": "Shipment confirmed and payment recorded."}), 200

    return render_template('confirm_shipment.html', shipment=shipment)

#


@app.route('/initiate_mpesa', methods=['POST'])
def initiate_mpesa():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")
    account_ref = data.get("account_ref")
    txn_desc = data.get("txn_desc")
    
    try:
        result = lipa_na_mpesa_stk_push(phone, amount, account_ref, txn_desc)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Mapping from OwnTracks device ID to integer vehicle_id
vehicle_mapping = {
    "f5": 1,
    # add other mappings as needed
}




# Endpoint: Update fleet route with GPS data (expects JSON data)
@app.route('/update_route', methods=['POST'])
def update_route():
    try:
        data = request.json
        if not data:
            app.logger.error("No JSON data provided")
            return jsonify({'error': 'No JSON data provided'}), 400

        app.logger.debug("Received data: %s", data)

        # Process only location updates
        if data.get('_type') != 'location':
            app.logger.debug("Ignoring non-location payload of type: %s", data.get('_type'))
            return jsonify({'status': 'ignored non-location message'}), 200

        # Extract location details
        latitude = data.get('lat')
        longitude = data.get('lon')
        tst = data.get('tst')
        if tst:
            timestamp = datetime.fromtimestamp(tst).strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get the device id from the payload
        device_id = data.get('tid')
        if not device_id:
            app.logger.error("No device id ('tid') found in payload")
            return jsonify({'error': 'No device id provided'}), 400

        # Mapping from device id to vehicle_id
        vehicle_mapping = {
            "f5": 1,
            # add other mappings as needed
        }
        vehicle_id = vehicle_mapping.get(device_id)
        if vehicle_id is None:
            app.logger.error("Unknown vehicle ID for device: %s", device_id)
            return jsonify({'error': 'Unknown vehicle ID'}), 400

        shipment_id = None  # If no shipment id is provided, set to None

        # Use a buffered cursor to ensure no unread results remain.
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)

        # Check if a row already exists for this vehicle_id
        select_sql = "SELECT id FROM fleet_routes WHERE vehicle_id = %s"
        cursor.execute(select_sql, (vehicle_id,))
        row = cursor.fetchone()

        if row:
            # Update the existing record
            update_sql = """
                UPDATE fleet_routes
                SET latitude = %s, longitude = %s, timestamp = %s
                WHERE vehicle_id = %s
            """
            cursor.execute(update_sql, (latitude, longitude, timestamp, vehicle_id))
        else:
            # Insert a new record if none exists
            insert_sql = """
                INSERT INTO fleet_routes (vehicle_id, shipment_id, latitude, longitude, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (vehicle_id, shipment_id, latitude, longitude, timestamp))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        app.logger.error("Error in update_route: %s", e)
        return jsonify({'error': str(e)}), 500




@app.route('/fleet_positions')
def fleet_positions():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT vehicle_id, latitude, longitude FROM fleet_routes")
    fleet_data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    response = jsonify(fleet_data)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.route('/fleet_tracking')
def fleet_tracking():
    return render_template('dashboard.html')


@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        # Try to get JSON data; if not available, use form data
        data = request.json if request.is_json else request.form

        vehicle_number = data.get('vehicle_number')
        driver_details = data.get('driver_details')

        if not vehicle_number or not driver_details:
            return jsonify({"error": "Missing required fields"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO vehicles (vehicle_number, driver_details) VALUES (%s, %s)",
                (vehicle_number, driver_details)
            )
            connection.commit()
            return jsonify({"message": "Vehicle registered successfully"}), 201
        except Exception as e:
            connection.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        # Render the form for GET requests
        return render_template('form.html')
    
    
@app.route('/download_confirmation/<int:shipment_id>')
def download_confirmation(shipment_id):
    # Fetch shipment details and shipment items
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments WHERE id = %s", (shipment_id,))
    shipment = cursor.fetchone()
    cursor.execute("SELECT * FROM shipment_items WHERE shipment_id = %s", (shipment_id,))
    shipment_items = cursor.fetchall()
    cursor.close()
    connection.close()
    
    if not shipment:
        return f"No shipment found with id {shipment_id}", 404
    
    grand_total = sum(item['total_cost'] for item in shipment_items)
    
    # Render the HTML template for the shipment confirmation PDF
    rendered = render_template('shipment_confirmation.html', 
                               shipment=shipment, 
                               shipment_items=shipment_items, 
                               grand_total=grand_total)
    
    # Convert HTML to PDF using pdfkit
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=shipment_confirmation_{shipment_id}.pdf'
    return response  
    
    

# -------------------------
# Main entry point
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
