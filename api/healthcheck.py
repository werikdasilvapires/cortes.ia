from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "API is running"}), 200

if __name__ == "__main__":
    app.run()
