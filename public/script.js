document.getElementById('uploadBtn').addEventListener('click', async () => {
    const videoInput = document.getElementById('videoInput');
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;

    if (!videoInput.files.length) {
        alert('Por favor, selecione um vídeo.');
        return;
    }

    const formData = new FormData();
    formData.append('video', videoInput.files[0]);

    try {
        // Enviar vídeo para upload
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        const uploadData = await uploadResponse.json();

        // Processar vídeo
        const processResponse = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_url: uploadData.video_url,
                start: start,
                end: end
            })
        });
        const processData = await processResponse.json();

        // Mostrar resultado
        document.getElementById('downloadLink').href = processData.processed_video_url;
        document.getElementById('result').classList.remove('hidden');
    } catch (error) {
        console.error('Erro:', error);
        alert('Ocorreu um erro. Tente novamente.');
    }
});
