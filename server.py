#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header
import logging
import traceback
import json

logging.basicConfig(level=logging.INFO,
                    format="%(created)-15s %(msecs)d %(levelname)8s %(thread)d %(name)s %(message)s")
logger = logging.getLogger(__name__)


HOST = ''
PORT = 4000

SET_OP = "set"
COMMIT_OP = "commit"

# TODO - Build backend datastore (must handle reboots/service shutdown)
# TODO - Build pending cache layer (may require a class wrapper to indicate if update or not)


class simpleRequestHandler(BaseHTTPRequestHandler):
    """Handle individual client HTTP requests."""

    def strip_path(self):
        """
        Remove all instances of / to determine if the path is multilevel.

        :returns: str
        """
        return self.path.replace('/', '')

    def bytes_to_str(self, data):
        """
        Convert data from bytes to string.

        :returns: str
        """
        if isinstance(data, str):
            return data
        return data.decode("utf-8")

    def str_to_bytes(self, data):
        """
        Convert data from string to bytes

        :returns: bytes[]
        """
        if isinstance(data, bytes):
            return data
        return data.encode("utf-8")

    def parse_data(self):
        """
        Parse the content-type field into a dictionary.

        :returns: dict
        """
        data = {}
        content = self.headers.get('content-type', None)
        if content:
            ctype, pdict = parse_header(content)
            if ctype == 'application/json':
                length = int(self.headers['content-length'])
                data = json.loads(self.bytes_to_str(self.rfile.read(length)))
        return data

    def do_GET(self):
        """Handle a get key request.

        If the key does not exist the response code will be 404.
        """
        logger.info("Received a GET request: {}".format(self.path))
        response_code = 404
        if(self.path.count('/') == 1):
            path = self.strip_path()
            if not (path == SET_OP or path == COMMIT_OP):
                response_code = 200

        self.send_response(response_code)
        """
        If Key is in cache
            self.send_response(200)
        else
            self.send_response(404)
        """

    def process_set_request(self):
        """
        Set a key/value property in the pending data.

        :returns: int (204)
        """
        response_code = 404
        try:
            data = self.parse_data()
            logger.info("Data received {}: {}".format(type(data), data))
            """
            If Key is not in cache
              response_code = 201
              add to pending
            else
              response_code = 200
              Check if more than 1 update op pending
                response_code = 400
              else
                add to pending
            """
        except Exception as ex:
            logger.error("Unable to process set request. {}:{}".format(type(ex),
                                                                       ex))
        return response_code

    def process_commit_request(self):
        """
        Push all pending data to the database.

        :returns: int (204)
        """
        # z = {**test, **test2} will merge two dictionaries based on key py3.5+
        return 204

    def do_POST(self):
        """Handle /set and /commit requests.

        /set will push a key insert (or single update) onto the pending data set.
        /commit will commit the pending data to the backing datastore.
        """
        logger.info("Received a POST request: {}".format(self.path))
        path = self.strip_path()
        if path == SET_OP:
            self.send_response(self.process_set_request())
        elif path == COMMIT_OP:
            self.send_response(self.process_commit_request())
        else:
            logger.error("Invalid POST operation {} was received.".format(path))
            self.send_response(404)

    def do_DELETE(self):
        """Uses the specified key data to indicate a pending delete operation."""
        logger.info("Received a DELETE request: {}".format(self.path))
        data = self.parse_data()
        # Data should be the key name
        logger.info("Data received {}: {}".format(type(data), data))
        path = self.strip_path()
        if path == SET_OP:
            self.send_response(self.process_delete_request())
        else:
            logger.error("Invalid DELETE operation {} was received.".format(path))
            self.send_response(404)


if __name__ == "__main__":
    server = None
    try:
        server = HTTPServer((HOST, PORT), simpleRequestHandler)
        sa = server.socket.getsockname()
        logger.info("Initializing web service at {}:{}".format(sa[0], sa[1]))
        logger.info("Press Ctrl-C to stop the service...")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down the service...")
        try:
            if server:
                server.socket.close()
        except:
            pass
    except Exception as ex:
        logger.error(traceback.format_exc())
        logger.error("Unexpected error running the service. {}: {}".format(type(ex),
                                                                           ex))
