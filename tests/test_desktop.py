import sys
from pathlib import Path
from unittest.mock import patch
import requests
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'desktop'))
from api_client import APIClient

def test_desktop_png_mime(tmp_path):
    image=tmp_path/'test.png';image.write_bytes(b'png')
    client=APIClient()
    with patch.object(client,'_request',return_value={'success':True}) as call:
        client.analyze_image(str(image))
        assert call.call_args.kwargs['files']['file'][2]=='image/png'

def test_desktop_offline_error():
    with patch('requests.request',side_effect=requests.ConnectionError):
        result=APIClient().analyze_text('test source')
        assert result['success'] is False
        assert 'backend' in result['error']
