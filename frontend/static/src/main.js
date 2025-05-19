// Lógica JavaScript separada para Gesture-Play
let player;

function extraerID(url) {
    const regExp = /(?:v=|\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regExp);
    return match ? match[1] : null;
}

function cargarVideo() {
    const url = document.getElementById('videoURL').value;
    const videoId = extraerID(url);
    if (!videoId) {
        alert("URL no válida");
        return;
    }

    if (player) {
        player.loadVideoById(videoId);
    } else {
        player = new YT.Player('player', {
            height: '100%',
            width: '100%',
            videoId: videoId,
            playerVars: {
                controls: 0,
                modestbranding: 1,
                rel: 0,
                showinfo: 0
            },
            events: {
                'onReady': onPlayerReady
            }
        });
    }
}

function onPlayerReady(event) {
    setTimeout(actualizarVolumen, 500);
}

function ajustarVolumen(delta) {
    const nuevoVolumen = Math.max(0, Math.min(100, player.getVolume() + delta));
    player.setVolume(nuevoVolumen);
    setTimeout(actualizarVolumen, 200);
}

function actualizarVolumen() {
    const volumen = player.getVolume();
    document.getElementById("volumen-num").innerText = volumen;
    document.getElementById("volumen-fill").style.width = volumen + "%";
}

const video = document.getElementById("video");
const prediccionTexto = document.getElementById("prediccion-live");
const imagenProcesada = document.getElementById("imagen-procesada");

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("No se pudo acceder a la cámara", err);
    });

setInterval(() => {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataURL = canvas.toDataURL("image/jpeg");

    fetch("http://localhost:5000/predecir", {
        method: "POST",
        body: convertirDataURLaFormData(dataURL)
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                prediccionTexto.innerText = "⚠️ " + data.error;
            } else {
                const porcentaje = Math.round(data.confianza * 100);
                prediccionTexto.innerText = `✋ Letra: ${data.prediccion} (${porcentaje}%)`;
                imagenProcesada.src = "data:image/jpeg;base64," + data.imagen_procesada;

                if (porcentaje >= 70) {
                    switch (data.prediccion) {
                        case 'P':
                            const estado = player.getPlayerState();
                            if (estado === 1) {
                                player.pauseVideo();
                            } else if (estado === 2) {
                                player.playVideo();
                            }
                            break;
                        case 'U':
                            ajustarVolumen(+10);
                            break;
                        case 'D':
                            ajustarVolumen(-10);
                            break;
                        case 'B':
                            player.seekTo(Math.max(player.getCurrentTime() - 10, 0), true);
                            break;
                        case 'A':
                            player.seekTo(player.getCurrentTime() + 10, true);
                            break;
                        default:
                            console.log("Gesto no mapeado:", data.prediccion);
                    }
                } else {
                    console.log(`Confianza insuficiente (${porcentaje}%), no se ejecuta acción.`);
                }
            }

        })
        .catch(err => console.error("Error al enviar imagen", err));
}, 1000);

function convertirDataURLaFormData(dataURL) {
    const formData = new FormData();
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeString });
    formData.append("imagen", blob, "frame.jpg");
    return formData;
}

window.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("modoReproductorSolo") === "true") {
        const rightPanel = document.querySelector(".right-panel");
        if (rightPanel) {
            rightPanel.style.display = "none";
        }
        const leftPanel = document.querySelector(".left-panel");
        if (leftPanel) {
            leftPanel.style.flex = "1";
        }
    }
});
