import importlib
import io
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv('DATA_DIR', str(tmp_path))
    import app.main as module
    module = importlib.reload(module)
    faces = []
    monkeypatch.setattr(module.vision, 'embeddings', lambda image: faces.copy())
    return TestClient(module.app), faces

def photo():
    f = io.BytesIO()
    Image.new('RGB',(100,100)).save(f,format='JPEG')
    return {'photo':('face.jpg',f.getvalue(),'image/jpeg')}

def vector(n):
    v = np.zeros(4); v[n]=1
    return {'box':[1,1,90,90],'embedding':v.tolist()}

def enroll(client, faces, code, n, role='student'):
    faces[:] = [vector(n)]
    return client.post('/people',data={'code':code,'name':code,'role':role},files=photo())

def test_complete_workflow(api):
    c, f = api
    a = enroll(c,f,'S1',0).json()
    b = enroll(c,f,'T1',1,'teacher').json()
    s = c.post('/sessions',json={'title':'AI class','person_ids':[a['id'],b['id']]}).json()['id']
    assert c.get(f'/sessions/{s}/report').json()['counts']['pending']==2
    f[:] = [vector(0)]
    assert c.post(f'/sessions/{s}/recognize',files=photo()).json()['faces'][0]['status']=='present'
    assert c.post(f'/sessions/{s}/recognize',files=photo()).json()['faces'][0]['status']=='already_present'
    c.post(f'/sessions/{s}/close')
    report = c.get(f'/sessions/{s}/report').json()
    assert report['counts']=={'present':1,'absent':1,'pending':0}
    assert c.post(f'/sessions/{s}/recognize',files=photo()).status_code==409
    assert 'S1' in c.get(f'/sessions/{s}/export.csv').text

def test_validation(api):
    c,f=api
    a=enroll(c,f,'S1',0)
    assert a.status_code==201
    assert enroll(c,f,'S1',1).status_code==409
    assert enroll(c,f,'S2',0).status_code==409
    f[:]=[]
    assert c.post('/people',data={'code':'S3','name':'X','role':'student'},files=photo()).status_code==422
    f[:]=[vector(1),vector(2)]
    assert c.post('/people',data={'code':'S3','name':'X','role':'student'},files=photo()).status_code==422
    assert c.post('/sessions',json={'title':'X','person_ids':['missing']}).status_code==404
    assert c.post('/people',data={'code':'S3','name':'X','role':'student'},files={'photo':('x.jpg',b'bad')}).status_code==422

def test_unknown_and_outside_roster(api):
    c,f=api
    a=enroll(c,f,'S1',0).json()
    enroll(c,f,'T1',1,'teacher')
    s=c.post('/sessions',json={'title':'test','person_ids':[a['id']]}).json()['id']
    f[:]=[vector(1),vector(2)]
    r=c.post(f'/sessions/{s}/recognize',files=photo()).json()
    assert [x['status'] for x in r['faces']]==['not_in_roster','unknown']
    assert c.get(f'/sessions/{s}/report').json()['counts']['present']==0

def test_persistence(api):
    c,f=api
    enroll(c,f,'S1',0)
    import app.main as module
    module=importlib.reload(module)
    assert len(TestClient(module.app).get('/people').json())==1

def test_ambiguous(api):
    c,f=api
    a=enroll(c,f,'S1',0).json()
    enroll(c,f,'S2',1)
    s=c.post('/sessions',json={'title':'test','person_ids':[a['id']]}).json()['id']
    # Deliberately create two near-identical templates to exercise ambiguity guard.
    import app.main as module
    import json
    with module.db() as db:
        db.execute('UPDATE persons SET embedding=? WHERE code=?',(json.dumps([.9999,.01414,0,0]),'S2'))
    f[:]=[vector(0)]
    assert c.post(f'/sessions/{s}/recognize',files=photo()).json()['faces'][0]['status']=='ambiguous'

def test_react_and_api_share_origin(api):
    c, _ = api
    response = c.get('/')
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text
    assert '/assets/' in response.text
    assert c.get('/docs').status_code == 200
    assert c.get('/health').json()['status'] == 'ok'
    import re
    asset = re.search(r'src="(/assets/[^\"]+)"', response.text).group(1)
    assert c.get(asset).status_code == 200
