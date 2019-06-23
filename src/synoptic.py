from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import logging
import time
import random

logging.basicConfig(level=logging.DEBUG)

client_socket = socket(AF_INET, SOCK_STREAM)
bufSize = 1024


class ReceiveThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging.debug("Receive Thread iniciada")
        global client_socket
        while True:
            try:
                msg = client_socket.recv(bufSize).decode("utf8")
                if not msg: break
                print("mensagem recebida: %s" % msg)
            except OSError: 
                pass
                # break


class SendThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging.debug("Send Thread iniciada")
        global client_socket
        while True:
            #TODO: ler entrada do usuário
            setpoint = round(random.uniform(0, 10), 2)
            try:
                client_socket.send(bytes(str(setpoint), "utf8"))
                if setpoint == "exit":
                    client_socket.close()
            except OSError:
                pass
                # break

            time.sleep(30)


class Synoptic:
    
    def __init__(self):
        Thread.__init__(self)
        self.host = "127.0.0.1"
        self.port = 30000
        self.addr = (self.host, self.port)
        
    def run(self):
        
        client_socket.connect(self.addr)
        while True:
            
            # try:
            msg = client_socket.recv(bufSize).decode()
            # if not msg: break
            logging.debug( msg)
            # except OSError: 
            #     logging.debug('erro')

        # receiveThread = ReceiveThread()
        # receiveThread.setDaemon(True)
        # receiveThread.setName("receiveThread")
        # receiveThread.start()

        # sendThread = SendThread()
        # sendThread.setDaemon(True)
        # sendThread.setName("SendThread")
        # sendThread.start()

        # sendThread.join()
        # receiveThread.join()


main = Synoptic()
main.run()
