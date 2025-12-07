# أمثلة على استخدام المراحل في Metadata

## 📋 أمثلة واقعية

### 1. وثيقة جمع المتطلبات (Requirements Gathering)

```markdown
---
title: "BA Artifacts - Requirements Gathering"
description: "مستندات تحليل الأعمال وجمع المتطلبات للمشروع."

applicable_phases:
  primary:
    - Requirements Gathering         # ⭐ المرحلة الأساسية
    - Planning                       # ⭐ أثناء التخطيط
  secondary:
    - Design                         # كمدخلات للتصميم

target_audience:
  primary:
    - Business Analyst
    - Project Manager
  secondary:
    - Developer                      # للفهم
    - Technical Lead
---
```

---

### 2. وثيقة التصميم (Design Phase)

```markdown
---
title: "Complete Design Part 1 - Architecture"
description: "التصميم المعماري الكامل للنظام - الجزء الأول."

applicable_phases:
  primary:
    - Design                         # ⭐ المرحلة الأساسية
    - Planning                       # ⭐ أثناء التخطيط
  secondary:
    - Requirements Gathering         # للتوافق مع المتطلبات
    - Development                    # كمرجع أثناء التطوير

target_audience:
  primary:
    - CTO / Technical Lead
    - Technical Architect
  secondary:
    - Developer
    - Project Manager
---
```

---

### 3. وثيقة التطوير (Development Phase)

```markdown
---
title: "Master Development Guide"
description: "دليل شامل للتطوير في HishamOS."

applicable_phases:
  primary:
    - Development                    # ⭐ المرحلة الأساسية
    - Code Review                    # ⭐ أثناء مراجعة الكود
  secondary:
    - Planning                       # أثناء التخطيط التقني
    - Maintenance                    # أثناء الصيانة

target_audience:
  primary:
    - Developer
    - Technical Lead
---
```

---

### 4. وثيقة الاختبار (Testing Phase)

```markdown
---
title: "Quick Start Testing Guide"
description: "دليل سريع للبدء في الاختبار."

applicable_phases:
  primary:
    - Testing                        # ⭐ المرحلة الأساسية
    - QA                             # ⭐ ضمان الجودة
    - UAT                            # ⭐ اختبار القبول
  secondary:
    - Development                    # أثناء التطوير (TDD)

target_audience:
  primary:
    - QA / Tester
    - Developer
---
```

---

### 5. وثيقة النشر (Deployment Phase)

```markdown
---
title: "Production Deployment Guide"
description: "دليل شامل لنشر النظام في الإنتاج."

applicable_phases:
  primary:
    - Deployment                     # ⭐ المرحلة الأساسية
    - Production                     # ⭐ في الإنتاج
  secondary:
    - Planning                       # أثناء التخطيط للنشر
    - Maintenance                    # أثناء الصيانة

target_audience:
  primary:
    - DevOps
    - Technical Lead
  secondary:
    - Developer
    - Project Manager
---
```

---

### 6. وثيقة مرجعية (All Phases)

```markdown
---
title: "Command Library Documentation"
description: "مرجع شامل لجميع الأوامر (250+)."

applicable_phases:
  primary:
    - All Phases                     # ⭐ في جميع المراحل
  # يمكن أيضاً تحديد مراحل محددة:
  # primary:
  #   - Development
  #   - Testing
  #   - Code Review
  #   - Maintenance

target_audience:
  primary:
    - Developer
    - QA / Tester
---
```

---

### 7. وثيقة UAT (User Acceptance Testing)

```markdown
---
title: "UAT Testing Checklist"
description: "قائمة شاملة لاختبار القبول للمستخدم."

applicable_phases:
  primary:
    - UAT                            # ⭐ المرحلة الأساسية
    - Testing                        # ⭐ بعد الاختبارات التقنية
    - QA                             # ⭐ ضمان الجودة
  secondary:
    - Requirements Gathering         # للتحقق من المتطلبات
    - Production                     # قبل الإنتاج

target_audience:
  primary:
    - QA / Tester
    - Business Analyst
    - End User                       # المستخدمون النهائيون
  secondary:
    - Project Manager
---
```

---

### 8. وثيقة مراجعة الكود (Code Review)

```markdown
---
title: "Code Review Guidelines"
description: "إرشادات مراجعة الكود وأفضل الممارسات."

applicable_phases:
  primary:
    - Code Review                    # ⭐ المرحلة الأساسية
    - Development                    # ⭐ أثناء التطوير
  secondary:
    - Planning                       # لتعريف المعايير
    - QA                             # كجزء من ضمان الجودة

target_audience:
  primary:
    - Developer
    - Technical Lead
  secondary:
    - QA / Tester
---
```

---

### 9. وثيقة الصيانة (Maintenance)

```markdown
---
title: "Maintenance Guide"
description: "دليل صيانة النظام وتحديثاته."

applicable_phases:
  primary:
    - Maintenance                    # ⭐ المرحلة الأساسية
    - Production                     # ⭐ في الإنتاج
  secondary:
    - Development                    # أثناء إصلاح الأخطاء

target_audience:
  primary:
    - DevOps
    - Developer
  secondary:
    - Technical Lead
---
```

---

### 10. وثيقة التوثيق (Documentation Phase)

```markdown
---
title: "Documentation Maintenance Guide"
description: "دليل صيانة وتحديث الوثائق."

applicable_phases:
  primary:
    - Documentation                  # ⭐ المرحلة الأساسية
    - All Phases                     # ⭐ مستمرة في جميع المراحل
  secondary:
    - Development                    # أثناء التطوير (documentation as code)
    - Maintenance                    # أثناء الصيانة

target_audience:
  primary:
    - Technical Writer
    - Developer
  secondary:
    - All Roles                      # للجميع
---
```

---

## 🔍 الفلترة حسب المرحلة

### مثال 1: جميع الوثائق لمرحلة التطوير

```python
development_docs = [
    doc for doc in all_docs 
    if 'Development' in doc.metadata['applicable_phases']['primary']
    or 'Development' in doc.metadata['applicable_phases']['secondary']
    or 'All Phases' in doc.metadata['applicable_phases']['primary']
]
```

**النتيجة:**
- ✅ Master Development Guide
- ✅ Command Library Documentation
- ✅ API Documentation
- ✅ Code Review Guidelines

### مثال 2: جميع الوثائق لمرحلة الاختبار

```python
testing_docs = [
    doc for doc in all_docs 
    if any(phase in ['Testing', 'QA', 'UAT'] 
           for phase in doc.metadata['applicable_phases']['primary'])
]
```

**النتيجة:**
- ✅ Quick Start Testing Guide
- ✅ UAT Testing Checklist
- ✅ Command Testing Checklist
- ✅ All manual test checklists

### مثال 3: جميع الوثائق لمرحلة النشر

```python
deployment_docs = [
    doc for doc in all_docs 
    if 'Deployment' in doc.metadata['applicable_phases']['primary']
    or 'Production' in doc.metadata['applicable_phases']['primary']
]
```

**النتيجة:**
- ✅ Production Deployment Guide
- ✅ Deployment Infrastructure Summary
- ✅ Docker Deployment Testing

---

## 🎯 الفلترة المركبة (Role + Phase)

### مثال: وثائق للمطورين في مرحلة التطوير

```python
dev_development_docs = [
    doc for doc in all_docs 
    if 'Developer' in doc.metadata['target_audience']['primary']
    and ('Development' in doc.metadata['applicable_phases']['primary']
         or 'All Phases' in doc.metadata['applicable_phases']['primary'])
]
```

### مثال: وثائق للمختبرين في مرحلة UAT

```python
qa_uat_docs = [
    doc for doc in all_docs 
    if 'QA / Tester' in doc.metadata['target_audience']['primary']
    and 'UAT' in doc.metadata['applicable_phases']['primary']
]
```

---

## ✅ الفوائد

1. **تنظيم أفضل** - اعرف أي وثيقة في أي مرحلة
2. **فلترة دقيقة** - ابحث حسب المرحلة + الدور
3. **إدارة أفضل** - تتبع الوثائق حسب المرحلة
4. **تخطيط أذكى** - اعرف ما تحتاجه في كل مرحلة

---

**هذا النظام يجعل الوثائق مرتبطة بوضوح بدورة حياة المشروع!**

