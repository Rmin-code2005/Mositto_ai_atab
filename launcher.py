"""Local launcher: owns one child server, waits for readiness, opens browser."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent

def main():
    if not (ROOT/'frontend/dist/index.html').is_file():
        print('Frontend build is missing. Read README_FA.md to rebuild it.')
        return 1
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    process = subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app',
        '--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env)
    try:
        deadline = time.monotonic()+60
        while time.monotonic()<deadline:
            if process.poll() is not None:
                print('Server stopped. Check the error above.')
                return 1
            try:
                with urllib.request.urlopen(url+'/health',timeout=1) as response:
                    if json.load(response).get('status')=='ok':
                        print(f'\nMositto is ready: {url}\nKeep this window open. Ctrl+C stops the server.\n')
                        webbrowser.open(url)
                        process.wait()
                        return process.returncode
            except (OSError, ValueError):
                time.sleep(.25)
        print('Server was not ready within 60 seconds. Check the error above.')
        return 1
    except KeyboardInterrupt:
        print('\nStopping Mositto...')
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

if __name__=='__main__':
    raise SystemExit(main())
