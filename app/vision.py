"""YOLO detection + normalized Facenet512 embeddings. Imports are lazy."""
import os
from pathlib import Path
from threading import RLock
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

class Vision:
    def __init__(self):
        self.lock = RLock()
        self.model = None

    def embeddings(self, image):
        with self.lock:
            from ultralytics import YOLO
            from deepface import DeepFace
            if self.model is None:
                path = Path(os.getenv('MODEL_PATH', str(ROOT / 'models/model.pt')))
                if not path.is_file():
                    raise RuntimeError(f'YOLO model not found: {path}')
                self.model = YOLO(str(path))
            # Pillow input is RGB; YOLO ndarray and DeepFace ndarray expect BGR.
            bgr = np.asarray(image.convert('RGB'))[:, :, ::-1].copy()
            output = self.model.predict(bgr, conf=0.5, verbose=False)[0]
            h, w = bgr.shape[:2]
            found = []
            for raw in output.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, raw)
                pad = int(max(x2-x1, y2-y1) * 0.10)
                x1, y1 = max(0, x1-pad), max(0, y1-pad)
                x2, y2 = min(w, x2+pad), min(h, y2+pad)
                if x2-x1 < 30 or y2-y1 < 30:
                    continue
                crop = bgr[y1:y2, x1:x2].copy()
                rep = DeepFace.represent(img_path=crop, model_name='Facenet512',
                    detector_backend='skip', enforce_detection=False, align=False)[0]['embedding']
                vector = np.asarray(rep, dtype=float)
                norm = np.linalg.norm(vector)
                if not np.isfinite(vector).all() or norm == 0:
                    raise RuntimeError('Invalid face embedding')
                found.append({'box': [x1, y1, x2, y2], 'embedding': (vector/norm).tolist()})
            return found

vision = Vision()
