import importlib.util
from pathlib import Path
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location('launcher',Path(__file__).parents[1]/'launcher.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

def test_ready_server_opens_browser_and_waits(monkeypatch):
    process=Mock()
    process.poll.return_value=None
    process.returncode=0
    monkeypatch.setattr(launcher.subprocess,'Popen',Mock(return_value=process))
    response=Mock()
    response.__enter__=Mock(return_value=response)
    response.__exit__=Mock(return_value=False)
    response.read.return_value=b'{"status":"ok"}'
    monkeypatch.setattr(launcher.urllib.request,'urlopen',Mock(return_value=response))
    browser=Mock()
    monkeypatch.setattr(launcher.webbrowser,'open',browser)
    assert launcher.main()==0
    assert browser.call_args.args[0].startswith('http://127.0.0.1:')
    process.wait.assert_called()
    process.terminate.assert_called_once()

def test_dead_server_does_not_open_browser(monkeypatch):
    process=Mock()
    process.poll.return_value=1
    monkeypatch.setattr(launcher.subprocess,'Popen',Mock(return_value=process))
    browser=Mock()
    monkeypatch.setattr(launcher.webbrowser,'open',browser)
    assert launcher.main()==1
    browser.assert_not_called()
