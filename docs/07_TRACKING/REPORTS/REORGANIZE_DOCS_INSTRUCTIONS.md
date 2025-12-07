# تعليمات تشغيل سكربت إعادة تنظيم الوثائق

## الطريقة 1: تشغيل من PyCharm (الأسهل)

1. افتح ملف `reorganize_docs.py` في PyCharm
2. اضغط بزر الماوس الأيمن على الملف
3. اختر "Run 'reorganize_docs'"
4. أو اضغط `Shift + F10`

## الطريقة 2: تشغيل من Terminal في PyCharm

1. افتح Terminal في PyCharm (Alt + F12)
2. تأكد أنك في المجلد الجذر للمشروع
3. قم بتفعيل venv أولاً:
   ```bash
   # إذا كان venv في backend
   backend\venv\Scripts\activate
   
   # ثم شغّل السكربت
   python reorganize_docs.py
   ```

## الطريقة 3: استخدام Python مباشرة

إذا كان Python مثبت في النظام:

```bash
# استبدل المسار بمسار Python الخاص بك
"C:\Users\hisha\AppData\Local\Programs\Python\Python313\python.exe" reorganize_docs.py
```

## ما الذي يفعله السكربت؟

1. ✅ يقرأ جميع ملفات .md من `backend/docs/`
2. ✅ ينقلها إلى `docs/` مع الهيكل الجديد
3. ✅ يضيف metadata تلقائياً لكل ملف
4. ✅ يحافظ على المحتوى الأصلي
5. ✅ يطبع تقرير بالإحصائيات

## ملاحظات

- السكربت **آمن** - لا يحذف الملفات الأصلية
- يمكن تشغيله عدة مرات
- إذا كان الملف يحتوي على metadata مسبقاً، سيحافظ عليه

---

**إذا لم تعمل أي طريقة، يمكن نقل الملفات يدوياً.**

