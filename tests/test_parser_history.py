import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from backend.services.parser_service import validate_url
from backend.services.history_service import HistoryService

@pytest.mark.parametrize('url',['http://127.0.0.1','https://n8n.io.evil.test','https://user:pass@n8n.io','file:///x','https://n8n.io:443/','https://albato.ru/?redirect=bad'])
def test_disallowed_url(url):
    with pytest.raises(ValueError): validate_url(url)

@pytest.mark.parametrize('url',['https://n8n.io/','https://www.make.com/en','https://albato.ru/'])
def test_configured_url(url):
    assert validate_url(url)==url

def test_history_survives_restart_and_keeps_full_result(tmp_path):
    path=tmp_path/'history.json'
    service=HistoryService(path)
    service.add_entry('text','input','summary',result={'summary':'complete'},source='https://n8n.io/',duration_s=1.25)
    item=HistoryService(path).get_history()[0]
    assert item.result=={'summary':'complete'}
    assert item.source=='https://n8n.io/'
    assert item.duration_s==1.25

def test_concurrent_history_retains_entries(tmp_path):
    service=HistoryService(tmp_path/'history.json')
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda i: service.add_entry('text',str(i),'ok'),range(10)))
    assert len(service.get_history())==10
    assert len({item.request_summary for item in service.get_history()})==10

def test_corrupt_history_preserved(tmp_path):
    path=tmp_path/'history.json';path.write_text('broken')
    with pytest.raises(ValueError):
        HistoryService(path).add_entry('text','x','y')
    assert path.read_text()=='broken'
