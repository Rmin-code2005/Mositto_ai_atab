import csv
import io
import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Literal
from uuid import uuid4

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field
from .vision import vision

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv('DATA_DIR', str(ROOT / 'data')))
DATA.mkdir(parents=True, exist_ok=True)
DB = DATA / 'attendance.sqlite3'
# These are prototype operating thresholds, not accuracy guarantees. Calibrate locally.
THRESHOLD = float(os.getenv('FACE_THRESHOLD', '0.30'))
MARGIN = float(os.getenv('FACE_MARGIN', '0.05'))
LOCK = RLock()
Role = Literal['student', 'teacher']

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    conn = sqlite3.connect(DB, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

with db() as c:
    c.executescript('''
    CREATE TABLE IF NOT EXISTS persons (
      id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('student','teacher')),
      embedding TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL,
      closed_at TEXT);
    CREATE TABLE IF NOT EXISTS roster (
      session_id TEXT REFERENCES sessions(id), person_id TEXT REFERENCES persons(id),
      PRIMARY KEY(session_id, person_id));
    CREATE TABLE IF NOT EXISTS attendance (
      session_id TEXT, person_id TEXT, first_seen TEXT NOT NULL,
      distance REAL NOT NULL, PRIMARY KEY(session_id, person_id),
      FOREIGN KEY(session_id,person_id) REFERENCES roster(session_id,person_id));
    ''')

app = FastAPI(title='Mositto Attendance API', version='1.0.0', description='Local prototype: enroll students/teachers, create a roster, recognize attendance, close and export. No authentication; bind to localhost.')

@app.get('/', include_in_schema=False)
def root():
    index = ROOT / 'frontend/dist/index.html'
    return FileResponse(index) if index.is_file() else RedirectResponse('/docs')

@app.get('/health', tags=['System'])
def health():
    return {'status': 'ok', 'recognition_model': 'Facenet512', 'ai_loaded': vision.model is not None}

def extract(photo):
    raw = photo.file.read(10 * 1024 * 1024 + 1)
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(413, 'Maximum image size is 10 MiB')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.width * im.height > 20_000_000:
                raise HTTPException(413, 'Maximum image dimensions are 20 megapixels')
            if im.format not in ('JPEG', 'PNG', 'WEBP'):
                raise HTTPException(422, 'Use JPEG, PNG or WebP')
            image = ImageOps.exif_transpose(im).convert('RGB')
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(422, 'Invalid image')
    try:
        result = vision.embeddings(image)
    except Exception:
        logging.exception('Face processing failed')
        raise HTTPException(503, 'Face engine failed. Check server logs, dependencies and model weights.')
    if not result:
        raise HTTPException(422, 'No usable face detected; try a clear, front-facing image')
    if len(result) > 30:
        raise HTTPException(422, 'Maximum 30 faces per request')
    return result

def distance(a, b):
    return float(np.clip(1 - np.dot(a, b), 0, 2))

def person_public(row):
    return {k: row[k] for k in ('id','code','name','role','created_at')}

@app.post('/people', status_code=201, tags=['People'])
def enroll(code: str = Form(..., min_length=1, max_length=80),
           name: str = Form(..., min_length=1, max_length=150),
           role: Role = Form(...), photo: UploadFile = File(...)):
    code, name = code.strip(), name.strip()
    if not code or not name:
        raise HTTPException(422, 'Name and code cannot be blank')
    with LOCK:
        with db() as c:
            if c.execute('SELECT 1 FROM persons WHERE code=?', (code,)).fetchone():
                raise HTTPException(409, 'Code already exists')
        found = extract(photo)
        if len(found) != 1:
            raise HTTPException(422, 'Enrollment requires exactly one face')
        emb = found[0]['embedding']
        with db() as c:
            for row in c.execute('SELECT embedding FROM persons'):
                if distance(emb, json.loads(row['embedding'])) <= THRESHOLD:
                    raise HTTPException(409, 'Similar face already enrolled; review existing people')
            pid = str(uuid4())
            try:
                c.execute('INSERT INTO persons VALUES (?,?,?,?,?,?)',
                    (pid,code,name,role,json.dumps(emb),now()))
            except sqlite3.IntegrityError:
                raise HTTPException(409, 'Code already exists')
            return person_public(c.execute('SELECT * FROM persons WHERE id=?',(pid,)).fetchone())

@app.get('/people', tags=['People'])
def people(role: Role | None = None):
    with db() as c:
        rows = c.execute('SELECT * FROM persons WHERE (? IS NULL OR role=?) ORDER BY created_at',(role,role))
        return [person_public(r) for r in rows]

class SessionInput(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    person_ids: list[str] = Field(min_length=1, max_length=1000)

@app.post('/sessions', status_code=201, tags=['Sessions'])
def create_session(body: SessionInput):
    if not body.title.strip():
        raise HTTPException(422, 'Title cannot be blank')
    ids = list(dict.fromkeys(body.person_ids))
    with db() as c:
        for pid in ids:
            if not c.execute('SELECT 1 FROM persons WHERE id=?',(pid,)).fetchone():
                raise HTTPException(404, f'Person not found: {pid}')
        sid = str(uuid4())
        c.execute('INSERT INTO sessions VALUES (?,?,?,NULL)',(sid,body.title.strip(),now()))
        c.executemany('INSERT INTO roster VALUES (?,?)',[(sid,pid) for pid in ids])
    return {'id':sid, 'title':body.title.strip(), 'person_ids':ids}

@app.get('/sessions', tags=['Sessions'])
def sessions():
    with db() as c:
        return [dict(r) for r in c.execute('SELECT * FROM sessions ORDER BY created_at DESC')]

def session_row(c, sid):
    row = c.execute('SELECT * FROM sessions WHERE id=?',(sid,)).fetchone()
    if not row:
        raise HTTPException(404, 'Session not found')
    return row

@app.post('/sessions/{session_id}/recognize', tags=['Attendance'])
def recognize(session_id: str, photo: UploadFile = File(...)):
    with LOCK:
        with db() as c:
            session = session_row(c, session_id)
            if session['closed_at']:
                raise HTTPException(409, 'Session is closed')
            # Search all enrolled people, then check membership to avoid assigning an
            # out-of-roster person to their nearest in-roster lookalike.
            all_people = [dict(r) for r in c.execute('SELECT * FROM persons')]
            members = {r[0] for r in c.execute('SELECT person_id FROM roster WHERE session_id=?',(session_id,))}
        found = extract(photo)
        results = []
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if session_row(c,session_id)['closed_at']:
                raise HTTPException(409, 'Session is closed')
            for face in found:
                ranked = sorted([(distance(face['embedding'],json.loads(p['embedding'])),p) for p in all_people], key=lambda item:item[0])
                item = {'box':face['box'], 'status':'unknown'}
                if ranked and ranked[0][0] <= THRESHOLD:
                    best, p = ranked[0]
                    if len(ranked)>1 and ranked[1][0]-best < MARGIN:
                        item['status']='ambiguous'
                    elif p['id'] not in members:
                        item['status']='not_in_roster'
                    else:
                        inserted = c.execute('INSERT OR IGNORE INTO attendance VALUES (?,?,?,?)',
                            (session_id,p['id'],now(),best)).rowcount
                        item.update(status='present' if inserted else 'already_present',
                            person=person_public(p), distance=round(best,5))
                results.append(item)
        return {'session_id':session_id,'faces':results}

@app.post('/sessions/{session_id}/close', tags=['Sessions'])
def close_session(session_id: str):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        session_row(c,session_id)
        c.execute('UPDATE sessions SET closed_at=COALESCE(closed_at,?) WHERE id=?',(now(),session_id))
        return dict(session_row(c,session_id))

@app.get('/sessions/{session_id}/report', tags=['Attendance'])
def report(session_id: str):
    with db() as c:
        session = dict(session_row(c,session_id))
        rows = c.execute('''SELECT p.id,p.code,p.name,p.role,a.first_seen,a.distance
          FROM roster r JOIN persons p ON p.id=r.person_id
          LEFT JOIN attendance a ON a.session_id=r.session_id AND a.person_id=r.person_id
          WHERE r.session_id=? ORDER BY p.role,p.name''',(session_id,)).fetchall()
        members = [dict(r) | {'status':'present' if r['first_seen'] else ('absent' if session['closed_at'] else 'pending')} for r in rows]
        return {'session':session,'counts':{s:sum(p['status']==s for p in members) for s in ('present','absent','pending')},'members':members}

@app.get('/sessions/{session_id}/export.csv', tags=['Attendance'])
def export(session_id: str):
    data = report(session_id)
    output = io.StringIO(newline='')
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(['code','name','role','status','first_seen_utc'])
    for p in data['members']:
        # Prevent spreadsheet formula execution for user-controlled text.
        def safe(value):
            value = str(value or '')
            return "'"+value if value.startswith(('=','+','-','@','\t','\r','\n')) else value
        writer.writerow([safe(p[k]) for k in ('code','name','role','status','first_seen')])
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition':f'attachment; filename="attendance-{session_id}.csv"'})

# Mount only compiled assets; keep all API routes and /docs accessible.
ASSETS = ROOT / 'frontend/dist/assets'
if ASSETS.is_dir():
    app.mount('/assets', StaticFiles(directory=ASSETS), name='frontend-assets')
