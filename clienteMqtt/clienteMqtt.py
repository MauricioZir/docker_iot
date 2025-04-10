import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(
    format='%(asctime)s - cliente mqtt - %(levelname)s - [%(funcName)s] %(message)s',
    level=logging.INFO,
    datefmt='%d/%m/%Y %H:%M:%S %z'
)


async def contador(contador_ref):
    while True:
        contador_ref[0] += 1
        await asyncio.sleep(3)


async def publicar(client, topic, contador_ref):
    while True:
        await client.publish(topic, str(contador_ref[0]))
        logging.info(f"Publicado en {topic}: {contador_ref[0]}")
        await asyncio.sleep(5)



async def topic_1_handler(topico_1_queue):
    while True:
        message = await topico_1_queue.get()
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))


async def topic_2_handler(topico_2_queue):
    while True:
        message = await topico_2_queue.get()
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))


async def recibir(client, topico_1, topico_2, queue_1, queue_2):
    async for message in client.messages:
        if message.topic.matches(topico_1):
            queue_1.put_nowait(message)
        elif message.topic.matches(topico_2):
            queue_2.put_nowait(message)





async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    contador_ref = [0]

    # Crear las colas dentro de main
    queue_1 = asyncio.Queue()
    queue_2 = asyncio.Queue()

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
        await client.subscribe([(topico_1, 0), (topico_2, 0)])

        # Crear tasks dentro del contexto del cliente
        tareas = [
            asyncio.create_task(recibir(client, topico_1, topico_2, queue_1, queue_2)),
            asyncio.create_task(topic_1_handler(queue_1)),
            asyncio.create_task(topic_2_handler(queue_2)),
            asyncio.create_task(contador(contador_ref)),
            asyncio.create_task(publicar(client, topico_pub, contador_ref))
        ]



if __name__ == "__main__":
    asyncio.run(main())
