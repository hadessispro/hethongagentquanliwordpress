import sys
from typing import Optional
from pyngrok import ngrok, conf
from mcp_server.config import settings

def start_ngrok(port: int, authtoken: str = '', domain: str = '') -> Optional[str]:
    '''Start an ngrok HTTP tunnel to the local port and return the public URL.'''
    token = authtoken or settings.NGROK_AUTHTOKEN
    if token:
        try:
            ngrok.set_auth_token(token)
        except Exception as e:
            print(f'[Ngrok Warning] Failed to set authtoken: {e}')

    try:
        connect_kwargs = {'addr': port, 'proto': 'http'}
        dom = domain or settings.NGROK_DOMAIN
        if dom:
            connect_kwargs['domain'] = dom

        tunnel = ngrok.connect(**connect_kwargs)
        public_url = tunnel.public_url
        if public_url.startswith('http://'):
            public_url = public_url.replace('http://', 'https://', 1)
        return public_url
    except Exception as e:
        err_msg = str(e)
        print('\n' + '=' * 65)
        print('[NGROK TUNNEL ERROR]')
        print(f'Error starting ngrok tunnel: {err_msg}')
        if 'authtoken' in err_msg.lower() or 'err_ngrok_4018' in err_msg.lower():
            print('\n-> Bạn cần có Ngrok Authtoken để mở tunnel ra ngoài!')
            print('-> Các bước lấy token miễn phí:')
            print('   1. Đăng ký tại: https://dashboard.ngrok.com/signup')
            print('   2. Lấy Authtoken tại: https://dashboard.ngrok.com/get-started/your-authtoken')
            print('   3. Điền vào file .env: NGROK_AUTHTOKEN=your_token_here')
        print('=' * 65 + '\n')
        return None

def stop_ngrok():
    '''Kill all active ngrok tunnels.'''
    try:
        ngrok.kill()
    except Exception:
        pass
