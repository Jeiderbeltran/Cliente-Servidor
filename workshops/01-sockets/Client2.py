# client.py
import socket
from PIL import Image
import io
import typer

def image_to_bytes(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_bytes = img_byte_arr.getvalue()

    return img_bytes

def send_bytes(sock, data):
    total_sent = 0
    while total_sent < len(data):
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise RuntimeError("La conexión del socket está rota")
        total_sent += sent

app = typer.Typer()

@app.command()
def send_image(server_ip: str, image_path: str, client_host: str, port: int = 12299):
    """
    Envía una imagen y el host del cliente a través de TCP.

    Parameters
    ----------
    server_ip : str
        IP del servidor al que conectar.
    image_path : str
        Ruta de la imagen a enviar.
    client_host : str
        Host del cliente que se enviará al servidor.
    port : int, optional
        Puerto donde el servidor está escuchando (el valor predeterminado es 12299).
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, port))

    # Enviar el host del cliente (opcionalmente puedes enviar primero el tamaño del host)
    host_bytes = client_host.encode('utf-8')
    client.sendall(len(host_bytes).to_bytes(4, 'big'))
    send_bytes(client, host_bytes)

    # Enviar la imagen
    img_bytes = image_to_bytes(image_path)
    size = len(img_bytes)
    client.sendall(size.to_bytes(4, 'big'))
    send_bytes(client, img_bytes)

    client.close()

if __name__ == "__main__":
    app()