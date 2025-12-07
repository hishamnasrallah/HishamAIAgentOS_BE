# Context: إعادة تنظيم الوثائق - HishamOS

**تاريخ الإنشاء:** 06 ديسمبر 2025  
**الحالة:** جاري التنفيذ  
**المطور:** AI Agent (Auto)

---

## 📋 ملخص المشروع

### الهدف
إعادة تنظيم جميع الوثائق (175+ ملف) في `backend/docs/` إلى هيكل منظم ومُصنف مع إضافة metadata شامل لكل مستند.

### المشاكل الحالية
1. ❌ الوثائق غير منظمة - صعب الوصول من Windows Explorer
2. ❌ لا يوجد metadata منظم - صعب البحث والفلترة
3. ❌ المراجع قديمة وغير محدثة
4. ❌ لا يوجد نظام تصنيف واضح

---

## 📁 الهيكل الحالي

### الموقع: `backend/docs/`

```
backend/docs/
├── commands/                    (2 ملفات)
├── deployment/                  (2 ملفات)
├── design/                      (1 ملف)
├── how_to_develop/              (4 ملفات)
├── implementation_plan/         (2 ملفات)
├── project_planning/            (7 ملفات)
├── testing/                     (13+ ملفات)
│   └── manual_test_checklist/   (19 ملفات)
├── tracking/                    (84 ملفات)
└── [ملفات في الجذر]            (~40 ملف)

المجموع: 175+ ملف
```

---

## 📁 الهيكل الجديد المقترح

### الموقع: `docs/` (سيتم إنشاؤه)

```
docs/
├── README.md                           # الفهرس الرئيسي
├── 00_GUIDE_INDEX.md                   # دليل شامل مع metadata
│
├── 01_CORE/                            # الوثائق الأساسية
│   ├── README.md
│   ├── INDEXES/
│   │   ├── README.md
│   │   ├── فهرس_المحتوى.md
│   │   └── hishamos_INDEX.md
│   ├── STATUS/
│   │   ├── PROJECT_STATUS_DEC_2024.md
│   │   ├── RELEASE_NOTES_DEC_2024.md
│   │   └── TASK_TRACKER.md
│   ├── USER_GUIDES/
│   │   ├── PROJECT_MANAGEMENT_USER_GUIDE.md
│   │   ├── WALKTHROUGH.md
│   │   └── ADMIN_USER_MANAGEMENT.md
│   ├── ADMIN/
│   │   └── DOCS_VIEWER_README.md
│   └── SUMMARIES/
│       ├── FINAL_SUMMARY_AR.md
│       ├── RESTRUCTURING_SUMMARY.md
│       └── analysis_hishamos.md
│
├── 02_DESIGN/                          # التصميم والمواصفات
│   ├── README.md
│   ├── ARCHITECTURE/
│   │   ├── hishamos_complete_design_part1.md
│   │   ├── hishamos_complete_design_part2.md
│   │   ├── hishamos_complete_design_part3.md
│   │   ├── hishamos_complete_design_part4.md
│   │   ├── hishamos_complete_design_part5.md
│   │   └── hishamos_complete_sdlc_roles_workflows.md
│   ├── UI/
│   │   ├── ui_redesign_plan.md
│   │   ├── hishamos_admin_management_screens.md
│   │   └── hishamos_ai_project_management.md
│   ├── GAPS/
│   │   ├── hishamos_critical_gaps_solutions.md
│   │   ├── hishamos_critical_gaps_solutions_part2.md
│   │   └── hishamos_critical_gaps_solutions_part3.md
│   ├── ROADMAP/
│   │   └── hishamos_missing_features_roadmap.md
│   └── PROMPTS/
│       ├── hishamos_complete_prompts_library.md
│       └── reference_prompts.md
│
├── 03_TESTING/                         # التوثيق الخاص بالاختبار
│   ├── README.md
│   ├── QUICK_START_TESTING_GUIDE.md
│   ├── UAT_TESTING_CHECKLIST.md
│   ├── UAT_USER_ACCEPTANCE_TESTING.md
│   ├── COMMAND_TESTING_CHECKLIST.md
│   ├── USER_JOURNEY_GUIDE.md
│   ├── TEST_EXECUTION_WORKSHEET.md
│   ├── MANUAL_TEST_CHECKLISTS/
│   │   ├── README.md
│   │   ├── ADMIN_UI_MANUAL_TESTING_CHECKLIST.md
│   │   ├── ADMIN_UI_BUG_FIXES.md
│   │   ├── SYSTEM_SETTINGS_UI_MANUAL_TESTING_CHECKLIST.md
│   │   └── [19 ملفات أخرى من manual_test_checklist/]
│   └── IMPLEMENTATION/
│       ├── SYSTEM_SETTINGS_UI_IMPLEMENTATION.md
│       └── USAGE_ANALYTICS_UI_IMPLEMENTATION.md
│
├── 04_DEPLOYMENT/                      # التوثيق الخاص بالنشر
│   ├── README.md
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   └── DEPLOYMENT_INFRASTRUCTURE_SUMMARY.md
│
├── 05_DEVELOPMENT/                     # أدلة التطوير
│   ├── README.md
│   ├── MASTER_DEVELOPMENT_GUIDE.md
│   ├── DOCUMENTATION_MAINTENANCE.md
│   └── VERIFICATION_CHECKLIST.md
│
├── 06_PLANNING/                        # التخطيط والمشاريع
│   ├── README.md
│   ├── BA_ARTIFACTS.md
│   ├── USER_STORIES.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── PROJECT_PLANS/
│   │   ├── PROJECT_PLAN.md
│   │   └── MASTER_DEVELOPMENT_PLAN.md
│   └── IMPLEMENTATION/
│       ├── IMPLEMENTATION_PLAN.md
│       ├── IMPLEMENTATION_SPECS.md
│       └── FULL_TECHNICAL_REFERENCE.md
│
├── 07_TRACKING/                        # التتبع والمراقبة
│   ├── README.md
│   ├── STATUS/
│   │   ├── PHASE_STATUS_SUMMARY.md
│   │   ├── PROJECT_ROADMAP.md
│   │   └── IMMEDIATE_NEXT_STEPS.md
│   ├── IMPLEMENTATION/
│   │   ├── PHASE_11_12_IMPLEMENTATION_PLAN.md
│   │   ├── PHASE_13_14_IMPLEMENTATION_PLAN.md
│   │   ├── PHASE_15_16_IMPLEMENTATION_PLAN.md
│   │   └── PHASE_17_18_IMPLEMENTATION_PLAN.md
│   ├── BUGS_FIXES/
│   │   ├── WEBSOCKET_FIXES_DEC_2024.md
│   │   ├── PERMISSIONS_FIX_DEC_2024.md
│   │   └── [ملفات fixes أخرى]
│   ├── PHASES/
│   │   ├── phase_0_detailed.md
│   │   ├── phase_1_detailed.md
│   │   └── [ملفات phases الأخرى]
│   └── [ملفات tracking أخرى]
│
├── 08_COMMANDS/                        # الأوامر والمكتبات
│   ├── README.md
│   ├── COMMAND_LIBRARY_DOCUMENTATION.md
│   └── COMMAND_TESTING_GUIDE.md
│
└── 09_PHASES/                          # المراحل والإكمال
    ├── README.md
    ├── PHASE_3/
    │   ├── PHASE_3_COMPLETION.md
    │   ├── PHASE_3_MODEL_CHANGES_REVIEW.md
    │   └── PHASE_3_TESTING_GUIDE.md
    ├── PHASE_4/
    │   └── PHASE_4_COMPLETION.md
    ├── PHASE_5/
    │   ├── PHASE_5_AGENT_TEMPLATES.md
    │   └── PHASE_5_COMPLETION.md
    ├── PHASE_6/
    │   ├── PHASE_6_COMPLETE.md
    │   ├── PHASE_6_IMPLEMENTATION_PLAN.md
    │   ├── PHASE_6_INFRASTRUCTURE_COMPLETE.md
    │   └── PHASE_6_PROGRESS.md
    └── PHASE_9/
        ├── PHASE_9B_GUIDE.md
        └── PHASE_9C_SUMMARY.md
```

---

## 📝 نظام Metadata الكامل

### Template الأساسي:

```yaml
---
title: "عنوان الوثيقة"
description: "وصف مختصر (2-3 أسطر)"
category: "Testing"                    # الفئة الرئيسية
subcategory: "Quick Start"             # الفئة الفرعية

language: "ar"                         # ar, en, both
original_language: "en"

purpose: |
  الهدف الأساسي من هذه الوثيقة...

target_audience:
  primary:
    - QA / Tester
    - Developer
  secondary:
    - Technical Lead

applicable_phases:
  primary:
    - Testing
    - QA
  secondary:
    - Development

tags:
  - testing
  - quick-start
  - manual-testing
  # ... المزيد

keywords:
  - "اختبار سريع"
  - "quick test"

prerequisites:
  documents:
    - 01_CORE/USER_GUIDES/WALKTHROUGH.md
  knowledge:
    - "فهم أساسي لنظام HishamOS"

status: "active"                       # active, deprecated, draft
priority: "high"                       # critical, high, medium, low
difficulty: "beginner"                 # beginner, intermediate, advanced
completeness: "100%"
quality_status: "reviewed"             # draft, reviewed, approved

estimated_read_time: "15 minutes"
estimated_usage_time: "2-4 hours"
estimated_update_time: "30 minutes"

version: "1.0"
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
review_frequency: "monthly"
next_review_date: "2025-01-06"

author: "Development Team"
maintainer: "QA Team"
reviewer: "Technical Lead"

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

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "النسخة الأولى"
    author: "Development Team"
---
```

---

## 🔧 Backend Code

### الملفات المهمة:

1. **`backend/apps/docs/views.py`**
   - `get_docs_path()` - يبحث في `backend/docs/` أولاً، ثم `docs/` في الجذر
   - `list_files()` - يعرض الملفات في tree أو topics
   - `get_file()` - يجلب محتوى ملف معين
   - `search()` - يبحث في الوثائق
   - `_classify_by_roles()` - يصنف الملفات حسب الأدوار
   - `_classify_by_topics()` - يصنف الملفات حسب المواضيع

2. **`backend/apps/docs/urls.py`**
   - `/api/v1/docs/list_files/` - عرض الملفات
   - `/api/v1/docs/get_file/` - جلب ملف
   - `/api/v1/docs/search/` - البحث

### التحديثات المطلوبة:

1. ✅ تحديث `get_docs_path()` للبحث في المكان الجديد بعد النقل
2. ⏳ تحديث `_classify_by_topics()` لتطابق الهيكل الجديد
3. ⏳ تحديث البحث لدعم Metadata (tags, roles, phases)

---

## 📊 خريطة التصنيف

### حسب الفئات:

- **01_CORE** - الوثائق الأساسية (30+ ملف)
- **02_DESIGN** - التصميم والمواصفات (15+ ملف)
- **03_TESTING** - الاختبار (35+ ملف)
- **04_DEPLOYMENT** - النشر (2 ملف)
- **05_DEVELOPMENT** - التطوير (4 ملفات)
- **06_PLANNING** - التخطيط (10+ ملفات)
- **07_TRACKING** - التتبع (84 ملف)
- **08_COMMANDS** - الأوامر (2 ملفات)
- **09_PHASES** - المراحل (10+ ملفات)

### حسب الأدوار (Roles):

- **Business Analyst** - BA artifacts, user stories
- **QA / Tester** - Testing guides, checklists
- **Developer** - Development guides, implementation
- **Technical Writer** - Documentation guides
- **Project Manager** - Planning, status, tracking
- **DevOps** - Deployment, infrastructure
- **CTO / Technical Lead** - Architecture, design

### حسب المراحل (Phases):

- **Development** - أثناء التطوير
- **Testing** - مرحلة الاختبار
- **QA** - ضمان الجودة
- **Business Gathering** - جمع المتطلبات
- **Deployment** - النشر
- **Planning** - التخطيط

---

## 📚 الملفات المرجعية

### الخطط والتوثيق:

1. `DOCS_REORGANIZATION_PLAN.md` - الخطة الشاملة
2. `DOCS_CLASSIFICATION_MAP.md` - خريطة التصنيف
3. `COMPLETE_METADATA_TEMPLATE.md` - Template Metadata
4. `DOCUMENTATION_WRITING_GUIDELINES.md` - دليل الكتابة
5. `EXAMPLE_DOCS_REORGANIZATION.md` - أمثلة عملية
6. `PHASES_EXAMPLES.md` - أمثلة المراحل

---

## ✅ خطة التنفيذ

### المرحلة 1: الإعداد ✅
- [x] دراسة جميع الوثائق
- [x] إنشاء خريطة تصنيف
- [x] إنشاء نظام Metadata
- [x] إنشاء دليل الكتابة
- [x] حفظ Context

### المرحلة 2: إنشاء الهيكل الجديد ⏳
- [ ] إنشاء مجلد `docs/` في الجذر
- [ ] إنشاء جميع المجلدات الرئيسية (01_CORE - 09_PHASES)
- [ ] إنشاء المجلدات الفرعية
- [ ] إنشاء README.md لكل مجلد

### المرحلة 3: نقل الملفات وإضافة Metadata ⏳
- [ ] نقل ملفات 01_CORE وإضافة Metadata
- [ ] نقل ملفات 02_DESIGN وإضافة Metadata
- [ ] نقل ملفات 03_TESTING وإضافة Metadata
- [ ] نقل ملفات 04_DEPLOYMENT وإضافة Metadata
- [ ] نقل ملفات 05_DEVELOPMENT وإضافة Metadata
- [ ] نقل ملفات 06_PLANNING وإضافة Metadata
- [ ] نقل ملفات 07_TRACKING وإضافة Metadata
- [ ] نقل ملفات 08_COMMANDS وإضافة Metadata
- [ ] نقل ملفات 09_PHASES وإضافة Metadata

### المرحلة 4: التحديثات ⏳
- [ ] تحديث جميع المراجع الداخلية
- [ ] تحديث جميع المراجع الخارجية
- [ ] تحديث Backend code
- [ ] تحديث Frontend code (إذا لزم)
- [ ] تحديث قواعد التطوير

### المرحلة 5: الاختبار والتحقق ⏳
- [ ] اختبار البحث
- [ ] اختبار الفلترة
- [ ] اختبار عرض الملفات
- [ ] التحقق من جميع الروابط
- [ ] التحقق من Metadata

---

## 🎯 القواعد والأولويات

### قواعد النقل:
1. ✅ الحفاظ على المحتوى الأصلي
2. ✅ إضافة Metadata كامل لكل ملف
3. ✅ تحديث الروابط الداخلية
4. ✅ استخدام أسماء واضحة

### أولويات:
1. **Critical:** 01_CORE, 03_TESTING, 05_DEVELOPMENT
2. **High:** 02_DESIGN, 06_PLANNING, 09_PHASES
3. **Medium:** 04_DEPLOYMENT, 08_COMMANDS
4. **Low:** 07_TRACKING (كبير جداً، يمكن تقسيمه)

---

## 📝 ملاحظات مهمة

1. **الموقع الجديد:** `docs/` في جذر المشروع (بجانب `backend/` و `frontend/`)
2. **الموقع القديم:** `backend/docs/` (سيتم حذفه بعد التأكد)
3. **Backend Code:** يحتاج تحديث `get_docs_path()` للبحث في `docs/` في الجذر
4. **Metadata:** إلزامي لجميع الملفات
5. **الروابط:** يجب تحديث جميع الروابط للمسارات الجديدة

---

**آخر تحديث:** 06 ديسمبر 2025  
**الحالة:** جاري التنفيذ - المرحلة 2

