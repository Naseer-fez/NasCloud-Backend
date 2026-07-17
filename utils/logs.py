def logs(app):
    @app.after_request
    def log_request_info(response):
        from flask import request
        from datetime import datetime
        import sys
        
        # Get IP address, respecting X-Forwarded-For if behind a proxy (like cloudflared/ngrok)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
            
        date_str = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
        protocol = request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
        
        # Construct path info with query string if present
        path_info = request.path
        if request.query_string:
            path_info = f"{path_info}?{request.query_string.decode('utf-8', errors='ignore')}"
            
        # Log format like Flask dev server: 127.0.0.1 - - [17/Jul/2026 10:45:00] "GET /health HTTP/1.1" 200 -
        log_line = f'{ip} - - [{date_str}] "{request.method} {path_info} {protocol}" {response.status_code} -'
        print(log_line, file=sys.stdout, flush=True)
        return response
