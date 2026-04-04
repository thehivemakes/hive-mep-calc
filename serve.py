import http.server, socketserver, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 3910))
with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"Serving MEPCalc on http://localhost:{port}")
    httpd.serve_forever()
