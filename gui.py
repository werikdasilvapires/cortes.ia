import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import threading
import time

# URL da API hospedada no Vercel
API_URL_UPLOAD = "https://cortes-ia.vercel.app/upload"
API_URL_PROCESS = "https://cortes-ia.vercel.app/process"

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processor - Cloud Automation")
        self.root.geometry("500x300")

        # Variáveis
        self.video_path = None
        self.upload_url = None

        # Componentes da Interface
        self.create_widgets()

    def create_widgets(self):
        # Botão para Selecionar Vídeo
        btn_select = tk.Button(self.root, text="Selecionar Vídeo", command=self.select_video)
        btn_select.pack(pady=10)

        # Label para mostrar caminho do vídeo
        self.lbl_video = tk.Label(self.root, text="Nenhum vídeo selecionado")
        self.lbl_video.pack()

        # Entradas para tempo inicial e final do corte
        frame_times = tk.Frame(self.root)
        frame_times.pack(pady=10)
        tk.Label(frame_times, text="Início (s):").grid(row=0, column=0, padx=5)
        self.entry_start = tk.Entry(frame_times, width=5)
        self.entry_start.grid(row=0, column=1, padx=5)

        tk.Label(frame_times, text="Fim (s):").grid(row=0, column=2, padx=5)
        self.entry_end = tk.Entry(frame_times, width=5)
        self.entry_end.grid(row=0, column=3, padx=5)

        # Botão de Upload
        btn_upload = tk.Button(self.root, text="Upload", command=self.upload_video)
        btn_upload.pack(pady=10)

        # Barra de progresso
        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Botão para Processar Vídeo
        btn_process = tk.Button(self.root, text="Processar Vídeo", command=self.process_video)
        btn_process.pack(pady=10)

        # Label para Link do Vídeo Processado
        self.lbl_result = tk.Label(self.root, text="")
        self.lbl_result.pack(pady=10)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if self.video_path:
            self.lbl_video.config(text=f"Selecionado: {self.video_path}")

    def upload_video(self):
        if not self.video_path:
            messagebox.showwarning("Aviso", "Por favor, selecione um vídeo.")
            return

        # Subir vídeo em uma thread para não travar a GUI
        threading.Thread(target=self.upload_video_thread).start()

    def upload_video_thread(self):
        self.progress["value"] = 0
        self.lbl_result.config(text="Fazendo upload...")

        with open(self.video_path, "rb") as f:
            files = {"video": f}
            response = requests.post(API_URL_UPLOAD, files=files)

        if response.status_code == 200:
            self.upload_url = response.json().get("video_url")
            self.lbl_result.config(text="Upload concluído!")
            self.progress["value"] = 100
        else:
            messagebox.showerror("Erro", "Falha no upload do vídeo.")

    def process_video(self):
        if not self.upload_url:
            messagebox.showwarning("Aviso", "Por favor, faça o upload do vídeo primeiro.")
            return

        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira tempos válidos.")
            return

        # Processar vídeo em uma thread separada
        threading.Thread(target=self.process_video_thread, args=(start, end)).start()

    def process_video_thread(self, start, end):
        self.progress["value"] = 0
        self.lbl_result.config(text="Processando vídeo...")

        data = {"video_url": self.upload_url, "start": start, "end": end}
        response = requests.post(API_URL_PROCESS, json=data)

        if response.status_code == 200:
            video_url = response.json().get("processed_video_url")
            self.lbl_result.config(text=f"Processado! [Baixar vídeo]( {video_url} )")
            self.progress["value"] = 100
        else:
            messagebox.showerror("Erro", "Falha no processamento do vídeo.")

# Inicializar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
