import json
import http.server
import socketserver
import threading
import copy

class ResponseBuffer:
    __buffer = []
    __step   = 0
    __lock   = threading.Lock()

    @staticmethod
    def send(points, action):
        response = {
            'step'  : ResponseBuffer.__step,
            'points': copy.deepcopy(points),
            'action': action
        }
        ResponseBuffer.__step += 1

        with ResponseBuffer.__lock:
            ResponseBuffer.__buffer.append(response)

    @staticmethod
    def take():
        with ResponseBuffer.__lock:
            return ResponseBuffer.__buffer.pop(0) \
                if len(ResponseBuffer.__buffer) > 0 else {}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()

        json_as_bytes = \
            lambda x: bytes(json.dumps(x), 'utf-8')

        w_ = self.wfile.write
        w_(json_as_bytes(ResponseBuffer.take()))

def serve():
    httpd = socketserver.TCPServer(('', 8000), Handler)
    httpd.serve_forever()

if __name__ == '__main__':
    serve()
