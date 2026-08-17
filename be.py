from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so our HTML frontend can communicate with this API
CORS(app) 

# A simple Python list to store names in memory
visitors = []

@app.route('/api/greet', methods=['POST'])
def greet_user():
    # Get the JSON data sent from the frontend
    data = request.json
    name = data.get('name', 'Guest')
    
    # Add the name to our visitors list
    if name not in visitors:
        visitors.append(name)
    
    # Send a JSON response back to the frontend
    return jsonify({
        "message": f"Hello, {name}! Your data was processed by Python.",
        "visitors": visitors
    })

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)
