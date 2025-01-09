from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()  # Accept JSON data from the request
    print(f"Received data: {data}")
    # Return a static response
    return jsonify({"response": "This is a placeholder response"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
