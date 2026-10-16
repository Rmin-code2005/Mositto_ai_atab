# Mositto | موسیتو

**Face-based attendance for students and teachers — React + FastAPI**  
**حضور و غیاب دانش‌آموزان و معلم‌ها با تشخیص چهره**

[فارسی](#فارسی) · [English](#english) · [AI agent brief](PROJECT_BRIEF_AI.md)

## فارسی

### معرفی

موسیتو یک برنامه وب محلی برای ثبت افراد، ساخت جلسه و ثبت حضور از روی تصویر است. رابط فارسی و راست‌به‌چپ React با FastAPI ارتباط دارد؛ YOLO محل چهره را پیدا می‌کند و DeepFace با مدل Facenet512 هویت را با افراد ثبت‌شده مقایسه می‌کند. داده‌ها در SQLite نگهداری می‌شوند.

این پروژه از سناریوی برنامه دسکتاپ Tkinter توسعه یافته است. نسخه وب مستقل است و برای اجرا به فایل‌های برنامه دسکتاپ نیاز ندارد.

### امکانات موجود

- تعریف دانش‌آموز/دانشجو و معلم/استاد با نام، شناسه یکتا و عکس.
- دریافت تصویر با وبکم مرورگر یا آپلود JPEG، PNG و WebP.
- پیش‌نمایش عکس و ارسال فقط پس از تأیید کاربر؛ ویدیو به سرور استریم نمی‌شود.
- ساخت جلسه با فهرست مشخص اعضا، شامل معلم و دانش‌آموزان.
- شناسایی چند چهره در یک عکس و جلوگیری از ثبت حضور تکراری.
- گزارش حاضرها، افراد در انتظار و غایب‌ها، با خروجی CSV قابل بازشدن در Excel.
- حفظ اطلاعات پس از توقف و اجرای مجدد برنامه.

### شروع سریع در ویندوز

**پیش‌نیاز:** Python 3.11 همراه Windows Python Launcher، مرورگر دارای پشتیبانی وبکم و اینترنت برای نصب اولیه/دریافت وزن‌ها. GPU الزامی نیست.

1. بسته را کامل استخراج کنید؛ فایل BAT را از داخل ZIP اجرا نکنید.
2. وارد پوشه `mositto-web` شوید.
3. روی **`START_WINDOWS.bat`** دوبار کلیک کنید.
4. بار اول، محیط مجازی `.venv` و وابستگی‌ها خودکار نصب می‌شوند. نصب کتابخانه‌های AI حجیم است.
5. پس از آماده‌شدن سرور، سایت خودکار در مرورگر باز می‌شود. برای وبکم اجازه دسترسی دوربین را بدهید.

پورت آزاد به‌صورت خودکار انتخاب و آدرس در ترمینال چاپ می‌شود. پنجره ترمینال را باز نگه دارید؛ **Ctrl+C** سرور را متوقف می‌کند. بستن تب مرورگر به‌تنهایی سرور را متوقف نمی‌کند.

`INSTALL_WINDOWS.bat` فقط نصب اولیه را انجام می‌دهد و نتیجه را در پنجره نگه می‌دارد؛ `SETUP_WINDOWS.bat` اسکریپت داخلی نصب است. برای استفاده عادی **Node.js لازم نیست**، چون خروجی React داخل بسته موجود است. این بسته فایل اجرایی مستقل `.exe` نیست و همچنان به Python نیاز دارد.

### اجرای دستی

همه دستورهای زیر از ریشه پروژه، کنار `requirements.txt` اجرا می‌شوند.

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe launcher.py
```

**Linux، با Python 3.11 نصب‌شده:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python launcher.py
```

برای پورت ثابت، به‌جای `launcher.py` اجرا کنید:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

سایت: `http://127.0.0.1:8000/` — مستندات تعاملی: `http://127.0.0.1:8000/docs`.
در ویندوز بدون فعال‌کردن محیط، به‌جای `python` از `.\.venv\Scripts\python.exe` استفاده کنید.

### روش استفاده

1. **افراد:** نام، شناسه و نقش را وارد کنید. عکس واضح با دقیقاً یک چهره بگیرید یا انتخاب کنید؛ سپس «ثبت فرد جدید» را بزنید. شناسه بین هر دو نقش یکتا است.
2. **جلسه جدید:** عنوان جلسه و اعضای آن را انتخاب کنید. ثبت فرد جدید، او را خودکار به جلسه‌های قبلی اضافه نمی‌کند.
3. **حضور و غیاب:** جلسه را انتخاب کنید، عکس تکی یا گروهی بگیرید و «بررسی تصویر و ثبت حضور» را بزنید. گرفتن عکس به‌تنهایی آن را ارسال نمی‌کند.
4. نتیجه هر چهره و گزارش جلسه را بررسی کنید. قبل از پایان جلسه، افراد دیده‌نشده **در انتظار** هستند.
5. پس از ارسال همه تصاویر، «پایان جلسه» را تأیید کنید. افراد دیده‌نشده **غایب** گزارش می‌شوند؛ جلسه بسته، حضور جدید نمی‌پذیرد.
6. در صورت نیاز، خروجی CSV بگیرید. زمان‌های ذخیره‌شده UTC هستند؛ ساعت حضور در رابط با تنظیمات محلی مرورگر نمایش داده می‌شود.

دوربین با تغییر بخش، خروج از صفحه یا دکمه خاموش‌کردن متوقف می‌شود. استفاده وبکم روی همان دستگاه با `localhost` یا `127.0.0.1` در نظر گرفته شده است؛ دسترسی موبایل از طریق IP شبکه در این بسته تنظیم نشده است.

### داده‌ها و پشتیبان‌گیری

دیتابیس به‌صورت پیش‌فرض در `data/attendance.sqlite3` ایجاد می‌شود. عکس اصلی و ویدیوی دوربین ذخیره نمی‌شوند؛ بردار عددی چهره و مشخصات فرد در دیتابیس می‌مانند. بردار چهره نیز داده حساس است.

برای بکاپ یا انتقال، سرور را متوقف و پوشه `data` را کپی کنید. داده‌های نسخه قبلی FastAPI با همین ساختار قابل انتقال‌اند؛ روی داده موجود بدون بکاپ بازنویسی نکنید. پوشه‌های عکس `students` و `teachers` نسخه Tkinter خودکار وارد نمی‌شوند؛ عکس‌ها باید از بخش ثبت افراد اضافه شوند.

### خطاهای متداول

| وضعیت | اقدام |
|---|---|
| Python 3.11 پیدا نشد | Python 3.11 و Python Launcher را نصب و اسکریپت را دوباره اجرا کنید. |
| نصب وابستگی‌ها متوقف شد | خطای ترمینال، اینترنت و فضای دیسک را بررسی و `START_WINDOWS.bat` را دوباره اجرا کنید. |
| وبکم باز نمی‌شود | مجوز Camera مرورگر را فعال و برنامه‌های دیگر استفاده‌کننده از وبکم را ببندید. |
| اولین پردازش طولانی است / خطای 503 | وزن‌های DeepFace ممکن است نیاز به دانلود داشته باشند؛ جزئیات خطا در ترمینال سرور است. |
| کد یا چهره تکراری / خطای 409 | افراد موجود را بررسی کنید؛ برای فرد تازه، شناسه یکتا و عکس صحیح بدهید. |
| هیچ چهره‌ای پیدا نشد / خطای 422 | عکس روشن‌تر و روبه‌رو انتخاب کنید؛ ثبت فرد باید دقیقاً یک چهره داشته باشد. |
| جلسه بسته است | ثبت بیشتر ممکن نیست؛ برای نوبت بعد جلسه جدید بسازید. |

حد تصویر: **۱۰ MiB و ۲۰ مگاپیکسل**؛ حداکثر **۳۰ چهره** در درخواست و **۱۰۰۰ عضو** در ورودی ساخت جلسه.

### محدوده و اعتبارسنجی

نسخه فعلی یک نمونه محلی دانشگاهی است. ورود مدیر، احراز هویت، ویرایش/حذف افراد، اصلاح دستی حضور، بازکردن مجدد جلسه و تشخیص زنده‌بودن چهره پیاده نشده‌اند. دقت تشخیص تضمین نشده و آستانه‌ها باید با داده واقعی ارزیابی شوند؛ ناشناس ماندن فرد لزوماً به معنی غیبت واقعی نیست.

۸ تست Python، ۴ تست React و ساخت خروجی فرانت در محیط توسعه موفق بوده‌اند. تست‌ها موتور AI و API وبکم را شبیه‌سازی می‌کنند؛ اجرای BAT روی ویندوز، وبکم واقعی و زنجیره کامل مدل‌های AI در محیط تحویل بررسی نشده‌اند.

---

## English

### Overview

Mositto is a local web application for enrolling students and teachers, creating attendance sessions, and marking attendance from photographs. It combines a Persian RTL React interface, a FastAPI backend, SQLite persistence, YOLO face detection, and DeepFace/Facenet512 face embeddings.

This is an independent web implementation of the original Tkinter attendance scenario. No desktop application files are required.

### Features

- Enroll a student or teacher with a name, globally unique code, and one-face image.
- Capture a photograph using the browser webcam or upload a JPEG, PNG, or WebP file.
- Preview before submission; no continuous video streaming.
- Create a session with an explicit roster of students and teachers.
- Recognize multiple faces and prevent duplicate attendance within a session.
- Review attendance, close sessions, and export UTF-8 CSV reports.
- Preserve records across restarts using SQLite.

### Quick start on Windows

Prerequisites: **Python 3.11 with Windows Python Launcher**, a camera-capable browser, and internet access for initial dependency/model downloads. A GPU is optional.

1. Extract the entire archive and open `mositto-web`.
2. Double-click **`START_WINDOWS.bat`**.
3. On first launch, the script creates `.venv` and installs Python dependencies.
4. The launcher selects an available loopback port, waits for the server, and opens the website.
5. Allow camera access when requested. Keep the terminal open; **Ctrl+C** stops the server.

For installation only, run `INSTALL_WINDOWS.bat`. `SETUP_WINDOWS.bat` is the internal setup script. **Node.js is not needed for normal use:** compiled React assets are included. Python is still required; this is not a standalone executable.

For manual installation, use the Windows or Linux commands in the Persian section above. `python launcher.py` opens the browser automatically. For a fixed address, run:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the application and `/docs` for Swagger. Use one worker. The launcher may select a different port on each run.

### User workflow

1. Open **افراد / People**. Enter a name, unique code, role, and a clear image containing exactly one face. Submit enrollment.
2. Open **جلسه جدید / New session**. Enter a title and select all expected participants, including teachers.
3. Open **حضور و غیاب / Attendance**. Select the session, capture or upload an image, then submit it for recognition.
4. Review per-face results and the roster report. Unseen members remain `pending` while the session is open.
5. Close the session after all images have been processed. Unseen members are then reported as `absent`; further recognition is rejected.
6. Download the CSV report if needed.

The browser stops its camera tracks when the camera component is removed or the camera is explicitly stopped. Webcam use is intended on the server machine through localhost/loopback. LAN/mobile access is not configured.

### API reference

| Method | Path | Input / purpose |
|---|---|---|
| GET | `/` | Compiled React application; redirects to `/docs` if its index is missing |
| GET | `/health` | Basic service status, model name, YOLO-loaded flag |
| POST | `/people` | Multipart: `code`, `name`, `role`, `photo`; enroll a person |
| GET | `/people` | List people; optional `role=student` or `role=teacher` |
| POST | `/sessions` | JSON: `title`, `person_ids`; create a roster snapshot |
| GET | `/sessions` | List sessions |
| POST | `/sessions/{session_id}/recognize` | Multipart: `photo`; recognize and mark attendance |
| GET | `/sessions/{session_id}/report` | Session details, member statuses, and counts |
| POST | `/sessions/{session_id}/close` | Close a session; repeated calls retain its first closing time |
| GET | `/sessions/{session_id}/export.csv` | CSV report with UTF-8 BOM and formula-prefix escaping |

Example session request; replace placeholders with actual person IDs returned by `/people`:

```json
{
  "title": "AI class — session 1",
  "person_ids": ["student-uuid", "teacher-uuid"]
}
```

Recognition statuses:

| Status | Meaning |
|---|---|
| `present` | New attendance record created |
| `already_present` | Attendance already exists; no duplicate inserted |
| `unknown` | No identity passes the distance threshold |
| `ambiguous` | The closest two candidates are too similar |
| `not_in_roster` | Recognized person is not a member of this session |

Report statuses are `present`, `pending`, and `absent`. A recognition `distance` is cosine distance, **not a confidence percentage**. Boxes refer to the EXIF-corrected image.

HTTP errors: `404` missing identity/session, `409` duplicate enrollment or closed session, `413` oversized image, `422` invalid input/no usable face, and `503` face-engine failure. Read server logs for AI failures.

### Architecture and project files

| Path | Responsibility |
|---|---|
| `app/main.py` | API routes, image validation, SQL persistence, reporting, static serving |
| `app/vision.py` | Lazy AI imports, YOLO crops, normalized Facenet512 embeddings |
| `frontend/src/main.jsx` | React screens and relative API requests |
| `frontend/src/Camera.jsx` | Webcam permission, capture, file selection, and cleanup |
| `frontend/src/style.css` | Responsive Persian RTL layout |
| `frontend/dist/` | Compiled frontend served by FastAPI |
| `models/model.pt` | Supplied YOLO face-detection weights |
| `launcher.py` | Select local port, start/wait for Uvicorn, open browser, stop child process |
| `*_WINDOWS.bat` | Windows setup and launch entry points |
| `tests/` | Python API and launcher tests |
| `frontend/src/Camera.test.jsx` | Mocked browser-camera tests |
| `PROJECT_BRIEF_AI.md` | Compact engineering context for an AI coding agent |

The browser and API use the same origin in normal operation. There is no separate Node.js server. SQLite tables are initialized when the backend module is imported; the project has no migration framework.

### Storage, models, and configuration

Default database: `data/attendance.sqlite3`. Person records store normalized embeddings, not original photographs. Attendance stores the first-seen time and match distance. Timestamps are timezone-aware UTC; the frontend formats visible times using browser locale settings.

Stop the server before copying the `data` directory for backup or transfer. Previous FastAPI data is compatible with the current schema. The original Tkinter image directories are not automatically imported.

| Environment variable | Default | Purpose |
|---|---|---|
| `DATA_DIR` | Project `data/` | Directory containing SQLite database |
| `MODEL_PATH` | Project `models/model.pt` | YOLO weight path |
| `FACE_THRESHOLD` | `0.30` | Maximum accepted cosine distance |
| `FACE_MARGIN` | `0.05` | Minimum distance gap between best and second-best candidates |

Environment variables must be set in the launching process; `.env` is **not loaded automatically**. Prefer absolute custom paths. Example before starting:

```powershell
$env:FACE_THRESHOLD="0.30"
.\.venv\Scripts\python.exe launcher.py
```

```bash
export FACE_THRESHOLD=0.30
python launcher.py
```

Thresholds are prototype defaults that need calibration on actual people, lighting, and unknown faces. Changing the embedding model requires re-enrollment or a deliberate embedding migration.

The bundled YOLO file does not include DeepFace recognition weights. Initial recognition may download additional weights; cache preparation is required for offline use. Dependency ranges are in `requirements.txt`; a fully validated Python lockfile is not included.

### Frontend development

Use Node.js 22 or another version supported by the pinned Vite version. From the project root:

```bash
cd frontend
npm ci
npm run test
npm run build
```

Restart the backend after rebuilding. For live development, start FastAPI on port 8000 and run `npm run dev` in `frontend`. Vite proxies `/people`, `/sessions`, and `/health` to that API. Open the Vite address for hot reload; `/docs` is available directly on the backend address.

### Tests and verification

From the project root, using the Python virtual environment:

```bash
python -m pip install -r requirements-test.txt
python -m pytest -q
```

Frontend tests/build:

```bash
cd frontend
npm ci
npm run test
npm run build
```

Previous verification: **8 Python tests passed**, **4 React tests passed**, and the Vite production build succeeded. Tests cover API behavior, persistence, duplicate prevention, roster exclusion, ambiguity, static serving, launcher behavior, and simulated camera interactions. They do not establish recognition accuracy or confirm a real Windows/webcam installation.

### Scope and next steps

This is a local academic prototype. It currently has no authentication/authorization, person editing/deletion, manual attendance correction, session reopening, or liveness detection. Photos displayed on screens or printed images may be accepted. Biometric embeddings remain sensitive data even when original images are not stored.

Keep the application bound to loopback. Public or institutional deployment needs access control, data-retention rules, real-world accuracy evaluation, and operational hardening. Potential enhancements are separate work: administrator login, manual review/corrections, multiple enrollment images, explicit migration management, and an end-to-end Windows test.

No project license is declared in this package. Check application and third-party dependency/model licensing before redistribution or commercial deployment.
