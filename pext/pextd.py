import socketserver
import threading
import queue
import functools
import json


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for request in self.rfile:
            request = json.loads(request[:-1])
            procedure = self.parse_request(request)
            queue.put(procedure)

    def parse_request(self, request):
        command = commands[request[0]]
        args = request[1:]
        return (functools.partial(command, *args), self.request)
                

def version():
    return "1.0"

commands = [
        version, # 0
        ]

def response_wrapper(f, sock):
    response = json.dumps(f())
    sock.send((response + "\n").encode())

queue = queue.Queue()

unix_server = socketserver.UnixStreamServer("/tmp/pext", ClientHandler)
unix_thread = threading.Thread(target=unix_server.serve_forever)
unix_thread.daemon = True
unix_thread.start()

tcp_server = socketserver.ThreadingTCPServer(("localhost", 9999), ClientHandler)
tcp_thread = threading.Thread(target=tcp_server.serve_forever)
tcp_thread.daemon = True
tcp_thread.start()

while True:
    command, sock = queue.get()
    response_wrapper(command, sock)
