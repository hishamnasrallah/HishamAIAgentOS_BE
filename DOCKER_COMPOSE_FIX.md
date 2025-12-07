# إصلاح ملفات Docker Compose للعمل من داخل backend/

**تاريخ الإصلاح:** 06 ديسمبر 2025  
**الهدف:** جعل ملفات `docker-compose.yml` تعمل بشكل صحيح عند التشغيل من داخل مجلد `backend/`

---

## 🔧 التغييرات التي تمت

### المبدأ الأساسي
تم تعديل جميع المسارات النسبية في ملفات Docker Compose لتكون صحيحة عند التشغيل من داخل `backend/`:

**من:** `backend/docker-compose.yml` (يتم تشغيله من الجذر)  
**إلى:** `backend/docker-compose.yml` (يتم تشغيله من داخل `backend/`)

---

## 📝 التغييرات التفصيلية

### 1. ملف `docker-compose.yml`

#### أ. Backend Service
```yaml
# قبل:
context: ./backend
volumes:
  - ./backend:/app
env_file:
  - .env

# بعد:
context: .
volumes:
  - .:/app
env_file:
  - ../.env
```

**السبب:**
- `context: .` لأننا بالفعل داخل `backend/`
- `volumes: .:/app` لأن `backend/` هو المجلد الحالي
- `env_file: ../.env` لأن `.env` يجب أن يكون في الجذر

#### ب. Celery Services (Worker & Beat)
```yaml
# قبل:
context: ./backend
volumes:
  - ./backend:/app
env_file:
  - .env

# بعد:
context: .
volumes:
  - .:/app
env_file:
  - ../.env
```

#### ج. Frontend Service
```yaml
# قبل:
context: ./frontend
dockerfile: ../infrastructure/docker/Dockerfile.frontend
volumes:
  - ./frontend:/app
env_file:
  - .env

# بعد:
context: ../frontend
dockerfile: ../../infrastructure/docker/Dockerfile.frontend
volumes:
  - ../frontend:/app
env_file:
  - ../.env
```

**السبب:**
- `context: ../frontend` لأن `frontend/` على مستوى أعلى من `backend/`
- `dockerfile: ../../infrastructure` لأن `infrastructure/` على نفس مستوى `backend/`، فنحتاج مستويين أعلى

#### د. PostgreSQL Service
```yaml
# قبل:
volumes:
  - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql

# بعد:
volumes:
  - ../scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
```

**ملاحظة:** إذا كان `scripts/` موجود في الجذر. إذا لم يكن موجوداً، يجب إنشاؤه أو حذف هذا السطر.

---

### 2. ملف `docker-compose.prod.yml`

تم تطبيق نفس التغييرات على ملف الإنتاج:

#### Backend, Celery Worker, Celery Beat
```yaml
# قبل:
context: ./backend

# بعد:
context: .
```

#### Frontend
```yaml
# قبل:
context: ./frontend
dockerfile: ../infrastructure/docker/Dockerfile.frontend.prod
volumes:
  - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro

# بعد:
context: ../frontend
dockerfile: ../../infrastructure/docker/Dockerfile.frontend.prod
volumes:
  - ../infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

---

## 🚀 كيفية الاستخدام

### للتطوير (Development)
```bash
cd backend/
docker-compose up
```

أو مع rebuild:
```bash
cd backend/
docker-compose up --build
```

### للإنتاج (Production)
```bash
cd backend/
docker-compose -f docker-compose.prod.yml up -d
```

---

## ⚠️ متطلبات إضافية

### 1. ملف `.env`
يجب أن يكون ملف `.env` في الجذر (نفس مستوى `backend/`):
```
hishamAiAgentOS/
├── .env          ← يجب أن يكون هنا
├── backend/
│   └── docker-compose.yml
├── frontend/
└── infrastructure/
```

### 2. ملف `scripts/init-db.sql` (اختياري)
إذا كنت تستخدم ملف `init-db.sql` لتهيئة قاعدة البيانات، يجب أن يكون في:
```
hishamAiAgentOS/
└── scripts/
    └── init-db.sql
```

إذا لم يكن موجوداً، يمكنك:
- إنشاؤه في الجذر
- أو حذف السطر `- ../scripts/init-db.sql:...` من docker-compose.yml

---

## ✅ التحقق من الإصلاح

### اختبار المسارات:
```bash
cd backend/

# التحقق من أن المسارات صحيحة
cat docker-compose.yml | grep -E "context:|dockerfile:|volumes:"
```

يجب أن ترى:
- `context: .` للـ backend
- `context: ../frontend` للـ frontend
- `dockerfile: ../infrastructure/...` أو `../../infrastructure/...`

---

## 📋 البنية المتوقعة

```
hishamAiAgentOS/
├── .env                    # ملف البيئة (يجب أن يكون هنا)
├── scripts/                # (اختياري)
│   └── init-db.sql
├── backend/
│   ├── docker-compose.yml      # ✅ معدل للعمل من هنا
│   ├── docker-compose.prod.yml # ✅ معدل للعمل من هنا
│   └── ...
├── frontend/
│   └── ...
└── infrastructure/
    └── docker/
        ├── Dockerfile.backend
        ├── Dockerfile.backend.prod
        ├── Dockerfile.frontend
        └── Dockerfile.frontend.prod
```

---

## 🔍 ملاحظات مهمة

1. **البيئة (.env):** يجب أن يكون `.env` في الجذر، وإلا ستحدث أخطاء عند تحميل المتغيرات.

2. **Volumes:** جميع المسارات في `volumes:` الآن نسبية لموقع الملفات في `backend/`.

3. **Dockerfile Paths:** مسارات Dockerfiles تم تعديلها لتكون صحيحة عند البناء من `backend/`.

4. **Network:** الشبكة الداخلية بين الخدمات ستعمل بشكل طبيعي لأن Docker Compose يديرها تلقائياً.

---

## 🆘 استكشاف الأخطاء

### خطأ: "Cannot find .env file"
**الحل:** تأكد من وجود `.env` في الجذر:
```bash
# من الجذر
ls .env

# إذا لم يكن موجوداً، أنشئه
cp .env.example .env
```

### خطأ: "Cannot find frontend directory"
**الحل:** تأكد من وجود `frontend/` في الجذر:
```bash
# من الجذر
ls -d frontend/
```

### خطأ: "Cannot find infrastructure directory"
**الحل:** تأكد من وجود `infrastructure/` في الجذر:
```bash
# من الجذر
ls -d infrastructure/
```

---

**آخر تحديث:** 06 ديسمبر 2025

