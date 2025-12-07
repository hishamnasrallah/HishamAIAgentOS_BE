# قالب Metadata كامل ومحسّن - HishamOS

## 🎯 المبادئ الأساسية

نظام Metadata شامل يركز على:
1. **الأشخاص** (Roles) - من يستفيد؟
2. **المراحل** (Phases) - في أي مرحلة؟
3. **الهدف** (Purpose) - لماذا؟
4. **المحتوى** (Content) - ماذا يحتوي؟
5. **الحالة** (Status) - ما حالته؟
6. **العلاقات** (Relations) - ما الوثائق ذات الصلة؟

---

## 📋 Template الكامل

```markdown
---
# ========================================
# BASIC INFORMATION / المعلومات الأساسية
# ========================================

title: "عنوان الوثيقة"
description: "وصف مختصر (2-3 أسطر) يوضح محتوى الوثيقة والهدف منها"

# التصنيف الأساسي
category: "Testing"                    # الفئة الرئيسية
subcategory: "Quick Start"             # الفئة الفرعية (اختياري)

# اللغة
language: "ar"                         # "ar" (عربي), "en" (إنجليزي), "both"
original_language: "en"                # اللغة الأصلية إذا تمت الترجمة

# ========================================
# PURPOSE & AUDIENCE / الهدف والجمهور
# ========================================

# 🎯 الهدف الأساسي من الوثيقة
purpose: |
  الهدف الأساسي من هذه الوثيقة هو مساعدة الفريق في البدء بسرعة في اختبار النظام.
  توفر خطوات واضحة ومبسطة للاختبار في وقت قصير (2-4 ساعات).

# 👥 الأشخاص الذين يستفيدون من هذه الوثيقة
target_audience:
  primary:                             # الجمهور الأساسي (يستخدمونها بشكل متكرر)
    - QA / Tester                      # المختبرون
    - Developer                        # المطورون
  secondary:                           # الجمهور الثانوي (يستخدمونها أحياناً)
    - Technical Lead                   # القادة التقنيون
    - Project Manager                  # مدراء المشاريع

# 🔄 المراحل/العمليات التي يمكن الاستفادة من هذه الوثيقة فيها
applicable_phases:
  primary:                             # المراحل الأساسية (تُستخدم فيها بشكل مباشر)
    - Testing                          # مرحلة الاختبار
    - QA                               # مرحلة ضمان الجودة
    - UAT                              # اختبار القبول للمستخدم
  secondary:                           # المراحل الثانوية (قد تُستخدم فيها)
    - Development                      # أثناء التطوير (لاختبار الكود)

# ========================================
# CONTENT METADATA / معلومات المحتوى
# ========================================

# 🏷️ Tags للبحث والفلترة
tags:
  # حسب الفئة
  - testing
  - quick-start
  - manual-testing
  
  # حسب الميزة
  - uat
  - test-execution
  - test-planning
  
  # حسب المرحلة
  - phase-1
  - phase-2
  
  # حسب النوع
  - guide
  - checklist
  - reference

# 🔑 كلمات مفتاحية للبحث (keywords مخصصة)
keywords:
  - "اختبار سريع"
  - "quick test"
  - "manual testing"
  - "test guide"

# 📦 الميزات/الوحدات المتعلقة
related_features:
  - "Command Execution"
  - "Workflow Execution"
  - "Dashboard Monitoring"

# 📚 المتطلبات السابقة (ما يجب معرفته/قراءته أولاً)
prerequisites:
  documents:
    - 01_CORE/USER_GUIDES/WALKTHROUGH.md
    - 01_CORE/USER_GUIDES/ADMIN_USER_MANAGEMENT.md
  knowledge:
    - "فهم أساسي لنظام HishamOS"
    - "معرفة أساسية بالاختبار اليدوي"
  tools:
    - "Browser (Chrome/Firefox)"
    - "Postman/Insomnia"
    - "Terminal"

# ========================================
# STATUS & QUALITY / الحالة والجودة
# ========================================

status: "active"                       # active, deprecated, draft, archived
priority: "high"                       # critical, high, medium, low
difficulty: "beginner"                 # beginner, intermediate, advanced, expert
completeness: "100%"                   # نسبة الاكتمال (0-100%)
quality_status: "reviewed"             # draft, reviewed, approved, needs-update

# ========================================
# TIME & EFFORT / الوقت والجهد
# ========================================

estimated_read_time: "15 minutes"      # الوقت المتوقع للقراءة
estimated_usage_time: "2-4 hours"     # الوقت المتوقع للاستخدام (إذا كان guide)
estimated_update_time: "30 minutes"   # الوقت المتوقع للتحديث

# ========================================
# VERSION CONTROL / التحكم بالإصدار
# ========================================

version: "1.0"                         # إصدار الوثيقة
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
review_frequency: "monthly"            # monthly, quarterly, annually, as-needed
next_review_date: "2025-01-06"        # تاريخ المراجعة القادمة

# ========================================
# OWNERSHIP / الملكية
# ========================================

author: "Development Team"             # المؤلف/الفريق
maintainer: "QA Team"                  # المسؤول عن الصيانة
reviewer: "Technical Lead"             # المراجع
approved_by: "CTO"                     # من وافق عليها

# ========================================
# RELATIONSHIPS / العلاقات
# ========================================

# 🔗 روابط ذات صلة مباشرة
related:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md
  - 03_TESTING/TEST_EXECUTION_WORKSHEET.md

# 📖 انظر أيضاً (وثائق ذات صلة غير مباشرة)
see_also:
  - 03_TESTING/manual_test_checklist/README.md
  - 07_TRACKING/TEST_TRACKING.md

# 🔄 يعتمد على (وثائق مطلوبة قبل هذه)
depends_on:
  - 01_CORE/USER_GUIDES/WALKTHROUGH.md

# 📤 يسبق (وثائق تستخدم هذه الوثيقة)
prerequisite_for:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md

# 🔀 أسماء بديلة للوثيقة (للبحث)
aliases:
  - "Testing Quick Start"
  - "Quick Test Guide"
  - "دليل الاختبار السريع"

# ========================================
# ADDITIONAL INFO / معلومات إضافية
# ========================================

# 📊 إحصائيات
word_count: 2500                       # عدد الكلمات (تقريبي)
page_count: 10                         # عدد الصفحات (تقريبي)
sections: 8                            # عدد الأقسام

# 📝 ملاحظات للمراجعين
review_notes: |
  تمت المراجعة في 2024-12-06.
  يجب تحديث الأمثلة بعد إصدار v2.0.

# 🚨 تحذيرات/ملاحظات مهمة
warnings:
  - "يجب تحديث بعد إصدار v2.0"
  - "بعض الأمثلة قد تحتاج تحديث"

# 📈 مقاييس الاستخدام (يمكن تحديثها تلقائياً)
usage_stats:
  views: 150                           # عدد المشاهدات
  last_accessed: "2024-12-06"         # آخر وصول
  popularity: "high"                   # high, medium, low

# ========================================
# CHANGE LOG / سجل التغييرات
# ========================================

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "النسخة الأولى"
    author: "Development Team"
  # يمكن إضافة المزيد من التغييرات

---
```

---

## 🎯 الاقتراحات الإضافية للتحسين

### 1. **Version Control** ✅
- تتبع الإصدارات والتغييرات
- سجل تغييرات واضح

### 2. **Ownership & Responsibility** ✅
- معرفة من المسؤول عن الصيانة
- من المراجع والموافق

### 3. **Quality Metrics** ✅
- حالة الجودة
- نسبة الاكتمال
- حالة المراجعة

### 4. **Dependencies** ✅
- ما يجب قراءته قبل هذه الوثيقة
- ما الذي يعتمد على هذه الوثيقة

### 5. **Search Enhancement** ✅
- Keywords مخصصة
- Aliases (أسماء بديلة)
- Related features

### 6. **Time Tracking** ✅
- وقت القراءة
- وقت الاستخدام
- وقت التحديث

### 7. **Review Schedule** ✅
- تواتر المراجعة
- تاريخ المراجعة القادمة

### 8. **Usage Statistics** ✅
- عدد المشاهدات
- آخر وصول
- الشعبية

---

## 📊 مثال عملي كامل

```markdown
---
title: "Quick Start Testing Guide"
description: "دليل سريع للبدء في اختبار نظام HishamOS. يحتوي على خطوات واضحة ومبسطة لاختبار المكونات الأساسية في وقت قصير."

category: "Testing"
subcategory: "Quick Start"
language: "both"                       # عربي وإنجليزي
original_language: "en"

purpose: |
  تسهيل عملية البدء في اختبار النظام للمختبرين الجدد والمطورين.
  توفير مسار واضح ومباشر للاختبارات الأساسية.

target_audience:
  primary:
    - QA / Tester
    - Developer
  secondary:
    - Technical Lead
    - Project Manager

applicable_phases:
  primary:
    - Testing
    - QA
    - UAT
  secondary:
    - Development

tags:
  - testing
  - quick-start
  - manual-testing
  - uat
  - guide

keywords:
  - "quick test"
  - "اختبار سريع"
  - "manual testing"
  - "test guide"

related_features:
  - "Command Execution"
  - "Workflow Execution"

prerequisites:
  documents:
    - 01_CORE/USER_GUIDES/WALKTHROUGH.md
  knowledge:
    - "فهم أساسي لنظام HishamOS"
  tools:
    - "Browser"
    - "Postman"

status: "active"
priority: "high"
difficulty: "beginner"
completeness: "100%"
quality_status: "reviewed"

estimated_read_time: "15 minutes"
estimated_usage_time: "2-4 hours"
estimated_update_time: "30 minutes"

version: "1.2"
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
review_frequency: "monthly"
next_review_date: "2025-01-06"

author: "QA Team"
maintainer: "QA Team"
reviewer: "Technical Lead"
approved_by: "CTO"

related:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md
see_also:
  - 03_TESTING/manual_test_checklist/README.md
depends_on:
  - 01_CORE/USER_GUIDES/WALKTHROUGH.md
prerequisite_for:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md

aliases:
  - "Testing Quick Start"
  - "Quick Test Guide"

word_count: 2500
page_count: 10
sections: 8

review_notes: |
  تمت المراجعة في 2024-12-06.
  يجب تحديث الأمثلة بعد إصدار v2.0.

warnings:
  - "يجب تحديث بعد إصدار v2.0"

usage_stats:
  views: 150
  last_accessed: "2024-12-06"
  popularity: "high"

changelog:
  - version: "1.2"
    date: "2024-12-06"
    changes: "إضافة قسم اختبار WebSocket"
    author: "QA Team"
  - version: "1.1"
    date: "2024-11-20"
    changes: "تحديث الأمثلة"
    author: "QA Team"
  - version: "1.0"
    date: "2024-10-15"
    changes: "النسخة الأولى"
    author: "QA Team"
---
```

---

**هذا النظام الشامل سيحسن إدارة وتنظيم الوثائق بشكل كبير!**

