from flask import Flask, jsonify, request, render_template
import random
import requests
import json
import os

app = Flask(__name__)

# Path to quotes.json
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "quotes.json")

# Helper functions
def load_quotes():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_quotes(quotes):
    with open(DATA_FILE, "w") as f:
        json.dump(quotes, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/quotes/random', methods=['GET'])
def get_random_quote():
    quotes = load_quotes()
    return jsonify(random.choice(quotes))

@app.route('/api/quotes', methods=['GET'])
def get_all_quotes():
    quotes = load_quotes()
    return jsonify(quotes)

@app.route('/api/quotes/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    quotes = load_quotes()
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if quote:
        return jsonify(quote)
    return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

@app.route('/api/quotes', methods=['POST'])
def add_quote():
    quotes = load_quotes()
    data = request.json
    if not data or "author" not in data or "text" not in data:
        return jsonify({"error": "Author and text are required"}), 400

    new_quote = {
        "id": max(q["id"] for q in quotes) + 1 if quotes else 1,
        "author": data["author"],
        "text": data["text"]
    }
    quotes.append(new_quote)
    save_quotes(quotes)
    return jsonify(new_quote), 201

def seed_quotes_from_api(count=5):
    """fect quotes from external API and store them in quotes.json"""
    quotes = []
    try:
        for _ in range(count):
            response = request.get("https://api.quotable.io/random")
            if response.status_code == 200:
                data = response.json()
                quotes.append({
                "id": len(quotes) + 1,
                "author": data.get("author"),
                "text": data.get("content")
            })
    except Exception as e:
        print("Error fetching external quotes:", e)

    if quotes:
        save_quotes(quotes)
        print(f"Seeded {len(quotes)} quotes from API")

@app.route('/api/quotes/<int:quote_id>', methods=['DELETE'])
def delete_quote(quote_id):
    quotes = load_quotes()
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

    quotes = [q for q in quotes if q["id"] != quote_id]
    save_quotes(quotes)
    return jsonify({"message": f"Quote with id {quote_id} deleted successfully"}), 200

@app.route('/api/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    quotes = load_quotes()
    data = request.json
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

    quote["text"] = data.get("text", quote["text"])
    quote["author"] = data.get("author", quote["author"])
    save_quotes(quotes)

    return jsonify({
        "message": f"Quote with id {quote_id} updated successfully",
        "quote": quote
    }), 200

@app.route('/api/quotes/external', methods=['GET'])
def fetch_external_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "author": data.get("author"),
                "text": data.get("content")
            })
        else:
            return jsonify({"error": "Failed to fetch external quote"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quotes/save', methods=['POST'])
def save_external_quote():
    data = request.json
    if not data or "author" not in data or "text" not in data:
        return jsonify({"error": "Author and text are required"}), 400

    quotes = load_quotes()
    new_quote = {
        "id": max(q["id"] for q in quotes) + 1 if quotes else 1,
        "author": data["author"],
        "text": data["text"]
    }
    quotes.append(new_quote)
    save_quotes(quotes)

    return jsonify({"message": "Quote saved successfully", "quote": new_quote}), 201

if __name__ == '__main__':
    # Run this once to pupopulate quotes.jsopn
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        seed_quotes_from_api(count=10) #fetch 10 quotes on first run
        
    app.run(debug=True)
