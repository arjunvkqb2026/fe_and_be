import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def health_check():
    return jsonify({"status": "API is running successfully"}), 200

def get_user_from_token(req):
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        return None

# --- NEW: VEHICLE ROUTES ---
@app.route('/api/vehicles', methods=['GET', 'POST'])
def manage_vehicles():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'POST':
        data = request.json
        res = supabase.table("vehicles").insert({"user_id": user.id, "name": data.get("name")}).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        res = supabase.table("vehicles").select("*").eq("user_id", user.id).execute()
        return jsonify(res.data)

# --- UPDATED: EXPENSE ROUTES ---
@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'POST':
        data = request.json
        new_expense = {
            "user_id": user.id,
            "vehicle_id": data.get("vehicle_id"), # Now links to the specific car
            "category": data.get("category"),
            "date": data.get("date"),
            "km": data.get("km", 0),
            "cost": data.get("cost", 0),
            "liters": data.get("liters"),
            "details": data.get("details")
        }
        res = supabase.table("expenses").insert(new_expense).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        vehicle_id = request.args.get('vehicle_id')
        if not vehicle_id:
            return jsonify([])
        # Fetch expenses ONLY for the selected vehicle
        res = supabase.table("expenses").select("*").eq("user_id", user.id).eq("vehicle_id", vehicle_id).order('date', desc=True).execute()
        return jsonify(res.data)

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    res = supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", user.id).execute()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(port=5000)
