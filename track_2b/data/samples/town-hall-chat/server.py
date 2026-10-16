import json, os, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE = os.environ.get("LLM_BASE_URL", "")


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        req = urllib.request.Request(BASE + "/chat/completions", data=body, headers={"Content-Type": "application/json"})
        self.send_response(200); self.end_headers(); self.wfile.write(urllib.request.urlopen(req).read())


HTTPServer(("", 8000), H).serve_forever()
