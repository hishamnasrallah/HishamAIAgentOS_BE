# Initial Data

نظام بسيط لتصدير وتحميل بيانات قاعدة البيانات.

## تصدير البيانات (جاهزة للاستخدام)

```bash
python manage.py export_initial_data
```

هذا الأمر:
- يصدر جميع الجداول من جميع التطبيقات
- يستثني جميع المستخدمين ما عدا `admin@hishamos.com`
- **ينظف تلقائياً جميع مراجع المستخدمين** ويجعلها تشير إلى admin
- يجعل الـ fixtures **جاهزة مباشرة للاستخدام** في deployment

**الملفات المُصدّرة:**
- `initial_data/fixtures/authentication.json` - admin user فقط
- `initial_data/fixtures/agents.json`
- `initial_data/fixtures/commands.json`
- `initial_data/fixtures/projects.json`
- `initial_data/fixtures/workflows.json`
- `initial_data/fixtures/integrations.json`
- `initial_data/fixtures/chat.json`
- وغيرها...

## تحميل البيانات

```bash
python manage.py load_initial_data
```

هذا الأمر:
- يحمل جميع الـ fixtures من `initial_data/fixtures/`
- يتخطى `authentication.json` تلقائياً إذا كان المستخدم موجوداً
- يعرض ملخص بما تم تحميله

## استخدام مباشر في Deployment

**في السيرفر (بعد `migrate` و `setup_admin_user`):**

```bash
python manage.py load_initial_data
```

أو:

```bash
python manage.py loaddata initial_data/fixtures/*.json
```

**ملاحظة:** الـ fixtures جاهزة للاستخدام مباشرة - لا تحتاج تنظيف أو معالجة إضافية.

## ملاحظات

- جميع مراجع المستخدمين تم تنظيفها تلقائياً لتشير إلى admin
- الـ fixtures جاهزة للاستخدام مباشرة في deployment
- لا تحتاج أي معالجة إضافية
