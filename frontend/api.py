import logging

from flask import Flask, request, jsonify
import threading
from werkzeug.serving import make_server


class Api:
    def __init__(self, func, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.func = func
        self.host = host
        self.port = port
        self.server_thread = None
        self.server = None

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self.app.route('/ga_info', methods=['POST'])
        def parse_ga_info():
            data = request.json
            self.func(data)
            return jsonify({'status': 'ok'})

    def run(self):
        if self.server_thread is None:
            self.server_thread = threading.Thread(target=self._serve)
            self.server_thread.start()
            print(f"Server is running on port {self.port}")

    def _serve(self):
        self.server = make_server(self.host, self.port, self.app)
        self.server.serve_forever()

    def stop(self):
        if self.server_thread is not None:
            self.server.shutdown()
            self.server_thread.join()
            self.server_thread = None
            print("Server has stopped")
