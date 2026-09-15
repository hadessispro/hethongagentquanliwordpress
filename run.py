import sys
import os
import argparse
import signal
import uvicorn
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp_server.config import settings
from mcp_server.server import app
from mcp_server.tunnel import start_ngrok, stop_ngrok

def print_banner(public_url: str = None):
    port = settings.PORT
    ws = settings.WORKSPACE_DIR
    mode = settings.PONYTAIL_MODE
    cmd_status = 'BAT (Enabled)' if settings.ENABLE_COMMAND_EXECUTION else 'TAT (Disabled)'
    
    print('\n' + '=' * 72)
    print('   LOCAL MCP & REST SERVER FOR GPT WITH NGROK & PONYTAIL')
    print('=' * 72)
    print(f' Thu muc lam viec (Workspace): {ws}')
    print(f' Che do Ponytail (Intensity) : {mode}')
    print(f' Cong noi bo (Local Port)   : {port}')
    print(f' Quyen chay PowerShell      : {cmd_status}')
    print('-' * 72)
    
    if public_url:
        print(f' Public Ngrok Base URL: {public_url}')
        print('\n [1] CAU HINH CHATGPT DEVELOPER MODE (MCP CONNECTOR):')
        print(f'     - MCP Endpoint (SSE):  {public_url}/sse')
        print(f'     - MCP Streamable HTTP: {public_url}/mcp')
        print('\n [2] CAU HINH CUSTOM GPT (ACTIONS / OPENAPI):')
        print(f'     - OpenAPI Schema URL:  {public_url}/openapi.json')
        print(f'     - API Docs (Swagger):  {public_url}/docs')
        print(f'     - Health Check:        {public_url}/health')
    else:
        print(f' Local Base URL: http://127.0.0.1:{port}')
        print(f' Local OpenAPI:  http://127.0.0.1:{port}/openapi.json')
        print(f' Local MCP SSE:  http://127.0.0.1:{port}/sse')
        print(f' Local MCP HTTP: http://127.0.0.1:{port}/mcp')
        print(f' Local Swagger:  http://127.0.0.1:{port}/docs')
    
    print('=' * 72 + '\n')

def main():
    parser = argparse.ArgumentParser(description='Local MCP & REST Server for GPT with Ngrok')
    parser.add_argument('--port', type=int, default=settings.PORT, help='Port to run the server on')
    parser.add_argument('--no-ngrok', action='store_true', help='Do not launch ngrok tunnel (local only)')
    parser.add_argument('--workspace', type=str, default=None, help='Target workspace directory path')
    parser.add_argument('--mode', type=str, default=None, choices=['lite', 'full', 'ultra'], help='Ponytail intensity')
    args = parser.parse_args()

    if args.port:
        settings.PORT = args.port
    if args.workspace:
        settings.WORKSPACE_DIR = Path(args.workspace).resolve()
    if args.mode:
        settings.PONYTAIL_MODE = args.mode

    public_url = None
    if not args.no_ngrok:
        print('Dang mo Ngrok tunnel ra ngoai internet...')
        public_url = start_ngrok(settings.PORT)
        if not public_url:
            print('-> Chay server o che do LOCAL do chua mo duoc ngrok (vui long kiem tra NGROK_AUTHTOKEN).')

    print_banner(public_url)

    def handle_exit(signum, frame):
        print('\nDang dung server va ngrok...')
        stop_ngrok()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level='info')
    finally:
        stop_ngrok()

if __name__ == '__main__':
    main()
