from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided."}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Salvar o arquivo
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)

    # Aqui você deve incluir sua lógica para processar o vídeo

    return jsonify({"video_url": f"http://your-storage-url.com/{file.filename}"}), 200

if __name__ == "__main__":
    app.run()
