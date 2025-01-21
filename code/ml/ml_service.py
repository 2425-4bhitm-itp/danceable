from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    #print(f"Received data: {data}")
    return jsonify({"response": data.get('fileName', 'No filename found')}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy", message="Service is running"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
