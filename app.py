import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
# Allow your Render frontend URL in production
CORS(app)

# Securely load credentials from Render's Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper function to verify the user token
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

@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized. Please log in."}), 401
        
    if request.method == 'POST':
        data = request.json
        new_expense = {
            "user_id": user.id,
            "category": data.get("category"),
            "date": data.get("date"),
            "km": data.get("km", 0),
            "cost": data.get("cost", 0),
            "liters": data.get("liters"), # Will be None if not provided
            "details": data.get("details") # Will be None if not provided
        }
        res = supabase.table("expenses").insert(new_expense).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        # Fetch only the logged-in user's expenses, sorted by date
        res = supabase.table("expenses").select("*").eq("user_id", user.id).order('date', desc=True).execute()
        return jsonify(res.data)

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    # Security check: Ensure we only delete if the expense matches the logged-in user_id
    res = supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", user.id).execute()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(port=5000)
