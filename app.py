from flask import Flask, jsonify, request, render_template
import random
import requests

app = Flask(__name__)

# in-memory list of quotes
quotes = [
    {"id": 1, "text": "The best way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
    {"id": 2, "text": "Don't let yesterday take up too much of today.", "author": "Will Rogers"},
    {"id": 3, "text": "It's not whether you get knocked down, it's whether you get up.", "author": "Vince Lombardi"},
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/quotes/random', methods=['GET'])
def get_random_quote():
    return jsonify(random.choice(quotes))

@app.route('/api/quotes', methods=['GET'])
def get_all_quotes():
    return jsonify(quotes)

@app.route('/api/quotes/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if quote:
        return jsonify(quote)
    return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

@app.route('/api/quotes', methods=['POST'])
def add_quote():
    data = request.json
    if not data or "author" not in data or "text" not in data:
        return jsonify({"error": "Author and text are required"}), 400

    new_quote = {
        "id": len(quotes) + 1,
        "author": data["author"],
        "text": data["text"]
    }
    quotes.append(new_quote)
    return jsonify(new_quote), 201

@app.route('/api/quotes/<int:quote_id>', methods=['DELETE'])
def delete_quote(quote_id):
    global quotes
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

    quotes = [q for q in quotes if q["id"] != quote_id]
    return jsonify({"message": f"Quote with id {quote_id} deleted successfully"}), 200

@app.route('/api/quotes/<int:quote_id>', methods=['PUT'])
def update_quote(quote_id):
    data = request.json
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        return jsonify({"error": f"Quote with id {quote_id} not found"}), 404

    quote["text"] = data.get("text", quote["text"])
    quote["author"] = data.get("author", quote["author"])

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

    new_quote = {
        "id": len(quotes) + 1,
        "author": data["author"],
        "text": data["text"]
    }

    quotes.append(new_quote)
    return jsonify({"message": "Quote saved successfully", "quote": new_quote}), 201


if __name__ == '__main__':
    app.run(debug=True)
