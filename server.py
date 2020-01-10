#  coding: utf-8
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import http404
import os.path


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        reqfile = self.request.makefile("rw")
        req = http404.Request.read_from(reqfile)
        self.handleHTTP(req).write_to(reqfile)

    def response404(self):
        message = "404: file not found\n"
        return http404.Response(
            status=(404, "Not Found"),
            headers={
                "Content-Length": len(message),
                "Content-Type": "text/plain",
            },
            body=message)

    def response405(self):
        message = "405: method not allowed\n"
        return http404.Response(
            status=(405, "Method Not Allowed"),
            headers={
                "Content-Length": len(message),
                "Content-Type": "text/plain",
            },
            body=message)

    def response301(self, redirect):
        message = "301: moved permanently"
        return http404.Response(
            status=(301, "Moved Permanently"),
            headers={
                "Location": redirect,
                "Content-Length": len(message),
                "Content-Type": "text/plain",
            },
            body=message)

    ftypes = {
        ".html": "text/html",
        ".htm": "text/html",
        ".css": "text/css",
    }

    def serve_file(self, path, uri):
        names = path.split("/")
        # don't allow unix relative paths
        if "." in names or ".." in names:
            return self.response404()

        try:
            truepath = "./www/" + path
            if os.path.isdir(truepath):
                if not uri.endswith("/"):
                    return self.response301(uri + "/")
                truepath += "/index.html"

            size = os.path.getsize(truepath)
            _, extension = os.path.splitext(truepath)


            return http404.Response(
                headers={
                    "Content-Length": size,
                    "Content-Type": self.ftypes.get(
                        extension, "text/plain")
                },
                body = open(truepath))
        except FileNotFoundError:
            return self.response404()

    def handleHTTP(self, req):
        if req.method == "GET":
            return self.serve_file(
                req.path,
                "http://" + req.headers["Host"] + req.path)
        else:
            return self.response405()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
