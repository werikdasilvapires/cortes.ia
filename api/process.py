from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/process', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get("video_url")
    start = data.get("start")
    end = data.get("end")

    # Aqui você deve incluir sua lógica de processamento de vídeo

    return jsonify({"processed_video_url": video_url}), 200

if __name__ == "__main__":
    app.run()
