import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(format='%(asctime)s - cliente mqtt - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S %z')

















async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    queue = asyncio.Queue()

    servidor = os.environ['SERVIDOR']
    topico_1 = os.environ['TOPICO_1']
    topico_2 = os.environ['TOPICO_2']
    topico_pub = os.environ['TOPICO_PUB']


    async with aiomqtt.Client(
        servidor,
        port=8883,
        tls_context=tls_context,
    ) as client:

        await client.subscribe([(topico_1, 0), (topico_2, 0)])

        # Crear tasks dentro del contexto del cliente
        tareas = [
            asyncio.create_task(recibir(client, topico_1, topico_2)),
            asyncio.create_task(contador(queue)),
            asyncio.create_task(publicar(client, topico_pub, queue))
        ]



    
        await client.subscribe(os.environ['TOPICO'])
        async for message in client.messages:
            logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))

if __name__ == "__main__":
    asyncio.run(main())
