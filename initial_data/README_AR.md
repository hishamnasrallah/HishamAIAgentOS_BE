---
title: البيانات الأولية - Database Fixtures
description: أدوات استخراج واستيراد البيانات من/إلى قاعدة البيانات

category: Development
subcategory: Database
language: ar
original_language: ar

purpose: |
  هذا المجلد يحتوي على أدوات لاستخراج واستيراد البيانات الأولية من/إلى
  قاعدة بيانات HishamOS. مفيد لإعداد بيئات جديدة، النسخ الاحتياطية، والهجرة.

target_audience:
  primary:
    - Developer
    - DevOps
  secondary:
    - Technical Lead

applicable_phases:
  primary:
    - Development
    - Deployment
  secondary:
    - Testing

tags:
  - database
  - fixtures
  - initial-data
  - backup
  - export
  - import

status: active
priority: high
difficulty: intermediate
completeness: 100%

estimated_read_time: 10 minutes

version: 1.0
last_updated: 2024-12-06
last_reviewed: 2024-12-06
review_frequency: quarterly
next_review_date: 2025-03-06

author: Development Team
maintainer: Development Team
reviewer: Technical Lead
---

# البيانات الأولية - Database Fixtures

هذا المجلد يحتوي على أدوات لاستخراج واستيراد البيانات من/إلى قاعدة بيانات HishamOS.

---

## 📁 هيكل المجلد

```
initial_data/
├── README.md                    # هذا الملف (English)
├── README_AR.md                 # هذا الملف (Arabic)
├── __init__.py                  # تهيئة الحزمة
├── fixtures/                    # ملفات البيانات المصدرة (JSON)
│   ├── agents.json
│   ├── commands.json
│   ├── projects.json
│   └── ...
└── scripts/                     # السكريبتات المساعدة
    └── export_all_data.py
```

---

## 🚀 البدء السريع

### استخراج جميع البيانات من قاعدة البيانات

```bash
# من مجلد backend
python manage.py export_initial_data

# مع مجلد مخصص للنتائج
python manage.py export_initial_data --output initial_data/fixtures/

# استخراج تطبيقات محددة فقط
python manage.py export_initial_data --apps agents commands
```

### استيراد البيانات من الملفات

```bash
# استيراد جميع الملفات
python manage.py loaddata initial_data/fixtures/*.json

# استيراد ملف محدد
python manage.py loaddata initial_data/fixtures/agents.json
```

---

## 📋 ما يتم استخراجه

الأمر يقوم باستخراج البيانات من التطبيقات التالية:

### النماذج الأساسية
- **Authentication**: المستخدمين، مفاتيح API
- **Agents**: تعريفات الوكلاء، تنفيذات الوكلاء
- **Commands**: فئات الأوامر، قوالب الأوامر
- **Projects**: المشاريع، السباقات، الملاحم، قصص المستخدم، المهام
- **Workflows**: سير العمل، تنفيذات سير العمل، خطوات سير العمل
- **Integrations**: منصات AI، استخدام المنصات
- **Core**: إعدادات النظام، أعلام الميزات
- **Monitoring**: مقاييس النظام، فحوصات الصحة، سجلات التدقيق
- **Chat**: المحادثات، الرسائل
- **Results**: النتائج، ملاحظات النتائج

### النماذج المستثناة (افتراضي)
- **سجلات التدقيق** (استخدم `--include-audit` لتضمينها)
- **مقاييس النظام** (استخدم `--include-metrics` لتضمينها)
- **سجلات التنفيذ** (استخدم `--include-histories` لتضمينها)

---

## 🔧 أمر الإدارة

### أمر الاستخراج

```bash
python manage.py export_initial_data [options]
```

#### الخيارات

- `--output DIR` - مجلد الإخراج للملفات (افتراضي: `initial_data/fixtures/`)
- `--apps APP1 APP2` - استخراج تطبيقات محددة فقط
- `--format FORMAT` - تنسيق الإخراج: `json` (افتراضي), `xml`
- `--indent N` - مستوى المسافة البادئة لـ JSON (افتراضي: 2)
- `--exclude-empty` - تخطي الملفات الفارغة (افتراضي: True)
- `--include-audit` - تضمين سجلات التدقيق
- `--include-metrics` - تضمين مقاييس النظام
- `--include-histories` - تضمين سجلات التنفيذ
- `--exclude-users` - استثناء بيانات المستخدمين (مفيد للقوالب)

#### أمثلة

```bash
# استخراج جميع البيانات
python manage.py export_initial_data

# استخراج الوكلاء والأوامر فقط
python manage.py export_initial_data --apps agents commands

# استخراج مع سجلات التدقيق
python manage.py export_initial_data --include-audit

# استخراج بدون بيانات المستخدمين (للقالب)
python manage.py export_initial_data --exclude-users
```

---

## 📦 استيراد الملفات

### استخدام Django's loaddata

```bash
# تحميل جميع الملفات
python manage.py loaddata initial_data/fixtures/*.json

# تحميل ملفات محددة بالترتيب
python manage.py loaddata \
    initial_data/fixtures/core.json \
    initial_data/fixtures/integrations.json \
    initial_data/fixtures/agents.json \
    initial_data/fixtures/commands.json
```

### الترتيب مهم!

عند الاستيراد، قم بتحميل الملفات بهذا الترتيب:

1. **Core** (`core.json`) - إعدادات النظام، أعلام الميزات
2. **Integrations** (`integrations.json`) - منصات AI
3. **Agents** (`agents.json`) - تعريفات الوكلاء
4. **Commands** (`commands.json`) - قوالب الأوامر (يعتمد على الوكلاء)
5. **Projects** (`projects.json`) - المشاريع والبيانات ذات الصلة
6. **Workflows** (`workflows.json`) - سير العمل
7. **أخرى** - المراقبة، الدردشة، النتائج (اختياري)

---

## 🔒 اعتبارات الأمان

### البيانات الحساسة

**⚠️ مهم:** الملفات قد تحتوي على بيانات حساسة:

- **مفاتيح API** - مشفرة في قاعدة البيانات، لكن يتم تصديرها في الملفات
- **كلمات مرور المستخدمين** - مشفرة، لكن لا تزال حساسة
- **بيانات المستخدمين** - معلومات شخصية

### أفضل الممارسات

1. **لا ترفع ملفات تحتوي على بيانات حقيقية** إلى التحكم بالإصدار
2. **استخدم `.gitignore`** لاستثناء ملفات الملفات:
   ```
   initial_data/fixtures/*.json
   !initial_data/fixtures/.gitkeep
   ```
3. **أنشئ ملفات قالب** بدون بيانات حساسة:
   ```bash
   python manage.py export_initial_data --exclude-users --output initial_data/fixtures/templates/
   ```
4. **قم بتشفير الملفات** إذا كانت تحتوي على بيانات حساسة

---

## 📝 مثال على سير العمل

### 1. استخراج قاعدة البيانات الحالية

```bash
# استخراج جميع البيانات من قاعدة البيانات الحالية
python manage.py export_initial_data --output initial_data/fixtures/backup_2024-12-06/
```

### 2. إنشاء ملفات قالب

```bash
# استخراج بدون بيانات حساسة للقوالب
python manage.py export_initial_data \
    --exclude-users \
    --output initial_data/fixtures/templates/
```

### 3. إعداد بيئة جديدة

```bash
# 1. تشغيل migrations
python manage.py migrate

# 2. تحميل ملفات القالب
python manage.py loaddata initial_data/fixtures/templates/*.json

# 3. إنشاء مستخدم admin
python manage.py setup_admin_user

# 4. إنشاء الوكلاء الافتراضيين (إذا لم تكن في الملفات)
python scripts/create_default_agents.py
```

---

## 🛠️ حل المشاكل

### المشكلة: قيود المفتاح الخارجي

**الخطأ:** `IntegrityError: FOREIGN KEY constraint failed`

**الحل:** قم بتحميل الملفات بالترتيب الصحيح (راجع قسم "الترتيب مهم!" أعلاه).

### المشكلة: أخطاء المفتاح المكرر

**الخطأ:** `IntegrityError: UNIQUE constraint failed`

**الحل:** 
- امسح البيانات الموجودة قبل التحميل:
  ```bash
  python manage.py flush --noinput
  python manage.py migrate
  python manage.py loaddata initial_data/fixtures/*.json
  ```

### المشكلة: مفاتيح API المشفرة

**ملاحظة:** مفاتيح API مشفرة في قاعدة البيانات. إذا كنت تستورد ملفات تحتوي على مفاتيح مشفرة:
- تأكد من أن متغير البيئة `ENCRYPTION_KEY` يتطابق
- أو أدخل مفاتيح API يدوياً بعد الاستيراد

---

## 📚 الوثائق ذات الصلة

- **دليل التثبيت**: `../INSTALLATION_GUIDE.md`
- **Django Fixtures**: https://docs.djangoproject.com/en/stable/topics/serialization/
- **Management Commands**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/

---

**آخر تحديث:** 6 ديسمبر 2024  
**الإصدار:** 1.0  
**يتم صيانتها بواسطة:** Development Team

