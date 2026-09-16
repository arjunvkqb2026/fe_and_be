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

# --- USER PROFILE & IN-HAND SALARY ---
@app.route('/api/profile', methods=['GET', 'POST'])
def manage_profile():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'POST':
        data = request.json
        salary = float(data.get("in_hand_salary", 0))
        res = supabase.table("user_settings").upsert({
            "user_id": user.id,
            "in_hand_salary": salary
        }).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        res = supabase.table("user_settings").select("*").eq("user_id", user.id).execute()
        salary = res.data[0]['in_hand_salary'] if res.data else 0
        return jsonify({"in_hand_salary": salary})

# --- RECURRING EXPENSES (EMIs, RENT, etc.) ---
@app.route('/api/recurring', methods=['GET', 'POST'])
def manage_recurring():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'POST':
        data = request.json
        payload = {
            "user_id": user.id,
            "name": data.get("name"),
            "amount": float(data.get("amount", 0)),
            "category": data.get("category", "Bills"),
            "active": data.get("active", True)
        }
        # If ID is provided, update existing
        if data.get("id"):
            res = supabase.table("recurring_expenses").update(payload).eq("id", data.get("id")).eq("user_id", user.id).execute()
        else:
            res = supabase.table("recurring_expenses").insert(payload).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        res = supabase.table("recurring_expenses").select("*").eq("user_id", user.id).order('created_at', desc=False).execute()
        return jsonify(res.data)

@app.route('/api/recurring/<rec_id>', methods=['DELETE'])
def delete_recurring(rec_id):
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    supabase.table("recurring_expenses").delete().eq("id", rec_id).eq("user_id", user.id).execute()
    return jsonify({"success": True})

# --- EXPENSE LOGS ---
@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'POST':
        data = request.json
        new_expense = {
            "user_id": user.id,
            "category": data.get("category"),
            "date": data.get("date"),
            "cost": float(data.get("cost", 0)),
            "details": data.get("details", "")
        }
        res = supabase.table("expenses").insert(new_expense).execute()
        return jsonify(res.data)

    elif request.method == 'GET':
        res = supabase.table("expenses").select("*").eq("user_id", user.id).order('date', desc=True).execute()
        return jsonify(res.data)

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    user = get_user_from_token(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", user.id).execute()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(port=5000)
