from app import create_app

app = create_app()

# This is for Vercel serverless function
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('unit loading'.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Received POST data'.encode('utf-8'))

if __name__ == '__main__':
    app.run()


####
### from app import create_app

### app = create_app()

###    @app.route('/')
###    def home():
###    return "Flask app running on Vercel"
###
### if __name__ == '__main__':
###    app.run()
 ###