import os
import requests
from flask import Flask, request, jsonify
import cloudinary.uploader as uploader
from moviepy.editor import VideoFileClip

# Inicializar o Flask
app = Flask(__name__)

# Configuração do Cloudinary
CLOUD_NAME = os.getenv("djk0vjyad")
API_KEY = os.getenv("699645337887825")
API_SECRET = os.getenv("RNgZHM4GdYFQClrFt2ZK14WWF_U")

# NÃO MODIFICAR ACIMA #

uploader.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided."}), 400

    file = request.files['video']

    try:
        # Upload para Cloudinary
        result = uploader.upload_large(file, resource_type="video")
        video_url = result['url']
        return jsonify({"message": "Upload concluído", "video_url": video_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get("video_url")
    start = data.get("start", 0)
    end = data.get("end", 60)

    if not video_url:
        return jsonify({"error": "No video URL provided."}), 400

    input_path = "temp_video.mp4"

    try:
        # Baixar vídeo temporariamente
        response = requests.get(video_url)
        with open(input_path, 'wb') as f:
            f.write(response.content)

        # Processar vídeo com MoviePy
        clip = VideoFileClip(input_path).subclip(start, end)
        output_path = "cut_video.mp4"
        clip.write_videofile(output_path)

        # Enviar para Cloudinary
        result = uploader.upload_large(output_path, resource_type="video")
        processed_video_url = result['url']

        # Remover arquivos temporários
        os.remove(input_path)
        os.remove(output_path)

        return jsonify({"message": "Processamento concluído", "processed_video_url": processed_video_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Não chame app.run() no Vercel
