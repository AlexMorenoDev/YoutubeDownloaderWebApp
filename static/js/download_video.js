document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("download-modal");

    document.querySelectorAll(".download-btn").forEach(button => {
        button.addEventListener("click", async () => {
            const allButtons = document.querySelectorAll(".download-btn");
            const resolution = button.dataset.resolution;
            const video_url = button.dataset.videoUrl;
            const title = button.dataset.title; 

            // Mostrar spinner y deshabilitar todos los botones
            modal.style.display = "flex";
            allButtons.forEach(btn => btn.disabled = true);

            try {
                // Llamada al backend
                const response = await fetch(`/download?video_url=${encodeURIComponent(video_url)}&resolution=${encodeURIComponent(resolution)}`, {
                    method: 'GET'
                });

                if (!response.ok) throw new Error("Error al procesar el vídeo");

                // Crear blob para descarga
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `${title}_${resolution}.mp4`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } catch (err) {
                alert("Ha ocurrido un error: " + err.message);
            } finally {
                // Ocultar modal y habilitar todos los botones
                modal.style.display = "none";
                allButtons.forEach(btn => btn.disabled = false);
            }
        });
    });
});