# دليل سريع لـ Metadata - Quick Reference

**للحصول على دليل كامل، راجع `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md`**

---

## ⚡ Template سريع (للنسخ والاستخدام)

```markdown
---
title: "[عنوان الوثيقة]"
description: "[وصف 2-3 أسطر]"

category: "[الفئة]"                  # Core, Design, Testing, Development, etc.
language: "ar"                        # ar, en, both

purpose: |
  [الهدف الأساسي - فقرة واحدة]

target_audience:
  primary:
    - [الدور الأساسي 1]               # Developer, QA/Tester, Project Manager, etc.
    - [الدور الأساسي 2]
  secondary:
    - [الدور الثانوي 1]

applicable_phases:
  primary:
    - [المرحلة الأساسية 1]            # Development, Testing, Deployment, etc.
    - [المرحلة الأساسية 2]
  secondary:
    - [المرحلة الثانوية 1]

tags:
  - [tag1]
  - [tag2]
  # ... 10+ tags

keywords:
  - "[كلمة مفتاحية 1]"

status: "active"                      # active, draft, deprecated
priority: "high"                      # critical, high, medium, low
difficulty: "beginner"                # beginner, intermediate, advanced

version: "1.0"
last_updated: "2024-12-06"
author: "[المؤلف/الفريق]"

related:
  - [path/to/related1.md]

prerequisites:
  documents:
    - [path/to/prereq1.md]
  knowledge:
    - "[متطلب معرفي 1]"
---
```

---

## 🎯 الحقول الإلزامية (Must Have)

| الحقل | مثال | الوصف |
|------|------|-------|
| `title` | "Quick Start Guide" | عنوان الوثيقة |
| `description` | "دليل للبدء السريع..." | وصف مختصر |
| `category` | "Testing" | الفئة الرئيسية |
| `purpose` | "تسهيل البدء..." | الهدف الأساسي |
| `target_audience.primary` | `["QA / Tester"]` | الجمهور الأساسي |
| `applicable_phases.primary` | `["Testing"]` | المراحل الأساسية |
| `tags` | `["testing", "quick-start"]` | Tags (10+ مستحسن) |
| `status` | "active" | الحالة |
| `version` | "1.0" | الإصدار |
| `last_updated` | "2024-12-06" | آخر تحديث |

---

## 👥 الأدوار المتاحة (Roles)

```
- Developer
- QA / Tester
- Business Analyst
- Project Manager
- DevOps
- Technical Lead
- CTO / Technical Lead
- Scrum Master
- UI/UX Designer
- Technical Writer
- Administrator
- End User
- Stakeholder
```

---

## 🔄 المراحل المتاحة (Phases)

```
- Requirements Gathering
- Planning
- Design
- Development
- Code Review
- Testing
- QA
- UAT
- Deployment
- Production
- Maintenance
- Documentation
- All Phases
```

---

## 🏷️ أمثلة على Tags

### حسب الفئة:
- `testing`, `development`, `deployment`, `design`, `planning`

### حسب الميزة:
- `api`, `ui`, `database`, `authentication`, `workflows`, `commands`

### حسب النوع:
- `guide`, `checklist`, `reference`, `status`, `implementation`

### حسب المرحلة:
- `phase-1`, `phase-2`, `phase-6`, `phase-13-14`

---

## ✅ Checklist سريع

### عند إنشاء وثيقة جديدة:
- [ ] ✅ استخدم Template أعلاه
- [ ] ✅ املأ جميع الحقول الإلزامية
- [ ] ✅ حدد `target_audience` بدقة
- [ ] ✅ حدد `applicable_phases` بدقة
- [ ] ✅ أضف 10+ tags
- [ ] ✅ أضف `related` و `prerequisites`

### عند تحديث وثيقة:
- [ ] ✅ زد `version` (1.0 → 1.1)
- [ ] ✅ حدّث `last_updated`
- [ ] ✅ أضف في `changelog`
- [ ] ✅ حدّث `related` إذا تغيرت

---

## 📚 المراجع الكاملة

- `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` - الدليل الكامل
- `COMPLETE_METADATA_TEMPLATE.md` - Template كامل
- `ENHANCED_METADATA_TEMPLATE.md` - شرح تفصيلي
- `PHASES_EXAMPLES.md` - أمثلة على المراحل
- `METADATA_EXAMPLE_QUICK_START.md` - مثال عملي

---

**ملاحظة:** هذا دليل سريع. للتفاصيل الكاملة، راجع `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md`

