import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import threading
import time
import os

# URLs da API hospedada no Vercel
API_URL_UPLOAD = "https://cortes-ia.vercel.app/upload"
API_URL_PROCESS = "https://cortes-ia.vercel.app/process"
API_URL_HEALTHCHECK = "https://cortes-ia.vercel.app/healthcheck"  # Rota para checar API

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processor - Cloud Automation")
        self.root.geometry("500x400")

        # Variáveis
        self.video_path = None
        self.upload_url = None
        self.start_time = None  # Para calcular a velocidade e o tempo restante

        # Componentes da Interface
        self.create_widgets()
        self.check_api_status()

    def create_widgets(self):
        # Botão para Selecionar Vídeo
        btn_select = tk.Button(self.root, text="Selecionar Vídeo", command=self.select_video)
        btn_select.pack(pady=10)

        # Label para mostrar o caminho do vídeo
        self.lbl_video = tk.Label(self.root, text="Nenhum vídeo selecionado")
        self.lbl_video.pack()

        # Frame para selecionar a duração do corte
        frame_duration = tk.Frame(self.root)
        frame_duration.pack(pady=10)

        tk.Label(frame_duration, text="Escolha a duração (minutos):").grid(row=0, column=0, padx=5)
        self.duration_var = tk.IntVar(value=1)
        self.duration_dropdown = ttk.Combobox(
            frame_duration, textvariable=self.duration_var, values=[1, 2, 3, 4, 5], width=5
        )
        self.duration_dropdown.grid(row=0, column=1, padx=5)

        # Barra de progresso
        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Exibir status em tempo real
        self.lbl_status = tk.Label(self.root, text="Status: Aguardando ação do usuário")
        self.lbl_status.pack(pady=5)

        # Botão de Upload
        btn_upload = tk.Button(self.root, text="Upload", command=self.upload_video)
        btn_upload.pack(pady=10)

        # Botão para Processar Vídeo
        btn_process = tk.Button(self.root, text="Processar Vídeo", command=self.process_video)
        btn_process.pack(pady=10)

        # Label para exibir o link do vídeo processado
        self.lbl_result = tk.Label(self.root, text="")
        self.lbl_result.pack(pady=10)

    def check_api_status(self):
        """Verifica se a API está online."""
        try:
            response = requests.get(API_URL_HEALTHCHECK, timeout=5)
            if response.status_code == 200:
                self.lbl_status.config(text="API Online")
            else:
                self.lbl_status.config(text="API Offline ou com Problemas")
        except requests.exceptions.RequestException:
            self.lbl_status.config(text="Erro: Não foi possível conectar à API")

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if self.video_path:
            self.lbl_video.config(text=f"Selecionado: {self.video_path}")

    def upload_video(self):
        if not self.video_path:
            messagebox.showwarning("Aviso", "Por favor, selecione um vídeo.")
            return

        # Upload em thread separada para não travar a GUI
        threading.Thread(target=self.upload_video_thread).start()

    def upload_video_thread(self):
        self.start_time = time.time()  # Inicia o cronômetro
        file_size = os.path.getsize(self.video_path)  # Tamanho do arquivo em bytes
        uploaded_size = 0

        # Faz upload usando requests
        with open(self.video_path, "rb") as f:
            response = requests.post(API_URL_UPLOAD, files={"video": f}, stream=True)

            if response.status_code == 200:
                self.upload_url = response.json().get("video_url")
                self.lbl_status.config(text="Upload concluído!")
                return
            else:
                messagebox.showerror("Erro", "Falha no upload do vídeo.")
                return

            # Monitora o progresso
            while uploaded_size < file_size:
                chunk = f.read(1024)  # Lê em pedaços de 1 KB
                if not chunk:
                    break
                uploaded_size += len(chunk)

                # Calcula progresso e tempo estimado
                percent = (uploaded_size / file_size) * 100
                elapsed_time = time.time() - self.start_time
                speed = uploaded_size / elapsed_time if elapsed_time > 0 else 0  # Bytes por segundo
                remaining_time = (file_size - uploaded_size) / speed if speed > 0 else 0

                # Atualiza a GUI com as informações
                self.progress["value"] = percent
                self.lbl_status.config(
                    text=f"Upload: {percent:.2f}% - Velocidade: {speed / 1024:.2f} KB/s - Restante: {remaining_time:.2f} s"
                )
                self.root.update_idletasks()

    def process_video(self):
        if not self.upload_url:
            messagebox.showwarning("Aviso", "Por favor, faça o upload do vídeo primeiro.")
            return

        # Recuperar a duração selecionada
        duration = self.duration_var.get()
        start = 0
        end = duration * 60  # Converter minutos para segundos

        # Processamento em thread separada
        threading.Thread(target=self.process_video_thread, args=(start, end)).start()

    def process_video_thread(self, start, end):
        self.progress["value"] = 0
        self.lbl_status.config(text="Processando vídeo...")

        data = {"video_url": self.upload_url, "start": start, "end": end}
        response = requests.post(API_URL_PROCESS, json=data)

        if response.status_code == 200:
            video_url = response.json().get("processed_video_url")
            self.lbl_result.config(text=f"Processado! [Baixar vídeo]({video_url})")
            self.progress["value"] = 100
        else:
            messagebox.showerror("Erro", "Falha no processamento do vídeo.")

# Inicializar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()