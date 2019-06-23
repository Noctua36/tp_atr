from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock
import logging
import time
import random

mutex = Lock()
logging.basicConfig(level=logging.DEBUG)

mutex.acquire()
client_socket = socket(AF_INET, SOCK_STREAM)
mutex.release()

bufSize = 1024


class ReceiveThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging.debug("Receive Thread iniciada")
        global client_socket
        while True:
            try:
                msg = client_socket.recv(bufSize).decode()
                # if not msg: break
                logging.debug(msg)
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
            # setpoint = round(random.uniform(0, 10), 2)
            setpoint = input('')
            logging.info('new setpoint: {}\n'.format(setpoint))
            try:
                client_socket.send(str(setpoint).encode())
                if setpoint == "exit":
                    client_socket.close()
            except OSError:
                pass
                # break

            # time.sleep(30)


class Synoptic:
    
    def __init__(self):
        Thread.__init__(self)
        self.host = "127.0.0.1"
        self.port = 30000
        self.addr = (self.host, self.port)
        
    def run(self):
        
        client_socket.connect(self.addr)
       
        receiveThread = ReceiveThread()
        receiveThread.setDaemon(True)
        receiveThread.setName("receiveThread")
        receiveThread.start()

        sendThread = SendThread()
        sendThread.setDaemon(True)
        sendThread.setName("SendThread")
        sendThread.start()

        sendThread.join()
        receiveThread.join()


main = Synoptic()
main.run()
