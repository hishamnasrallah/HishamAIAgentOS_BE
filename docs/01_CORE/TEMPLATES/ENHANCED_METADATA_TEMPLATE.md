# قالب Metadata محسّن - يركز على الأدوار والأهداف

## 🎯 المبادئ الأساسية

1. **الأدوار (Roles)** - من يمكنه الاستفادة من هذه الوثيقة؟
2. **الهدف (Purpose)** - ما الهدف الأساسي من هذه الوثيقة؟
3. **المستوى (Level)** - للمبتدئين أم المتقدمين؟
4. **الوقت (Time)** - كم يستغرق قراءتها/استخدامها؟

---

## 📋 Template الكامل

```markdown
---
title: "عنوان الوثيقة"
description: "وصف مختصر (2-3 أسطر) يوضح محتوى الوثيقة والهدف منها"

# التصنيف الأساسي
category: "Testing"                    # الفئة الرئيسية
subcategory: "Quick Start"             # الفئة الفرعية (اختياري)

# 🎯 الهدف من الوثيقة (مهم جداً!)
purpose: |
  الهدف الأساسي من هذه الوثيقة هو مساعدة الفريق في البدء بسرعة في اختبار النظام.
  توفر خطوات واضحة ومبسطة للاختبار في وقت قصير (2-4 ساعات).

# 👥 الأشخاص الذين يستفيدون من هذه الوثيقة (مهم جداً!)
target_audience:
  primary:                             # الجمهور الأساسي (يستخدمونها بشكل متكرر)
    - QA / Tester                      # المختبرون
    - Developer                        # المطورون
  secondary:                           # الجمهور الثانوي (يستخدمونها أحياناً)
    - Technical Lead                   # القادة التقنيون
    - Project Manager                  # مدراء المشاريع

# 🔄 المراحل/العمليات التي يمكن الاستفادة من هذه الوثيقة فيها
applicable_phases:                     # في أي مرحلة من دورة حياة المشروع؟
  primary:                             # المراحل الأساسية (تُستخدم فيها بشكل مباشر)
    - Testing                          # مرحلة الاختبار
    - QA                               # مرحلة ضمان الجودة
    - Development                      # مرحلة التطوير (اختياري)
  secondary:                           # المراحل الثانوية (قد تُستخدم فيها)
    - Requirements Gathering           # مرحلة جمع المتطلبات (للفهم)
    - Planning                         # مرحلة التخطيط

# 📋 قائمة المراحل المتاحة:
# - Requirements Gathering    # جمع المتطلبات
# - Planning                  # التخطيط
# - Design                    # التصميم
# - Development               # التطوير
# - Code Review               # مراجعة الكود
# - Testing                   # الاختبار
# - QA                        # ضمان الجودة
# - UAT                       # اختبار القبول للمستخدم
# - Deployment                # النشر
# - Production                # الإنتاج
# - Maintenance               # الصيانة
# - Documentation             # التوثيق

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

# 📊 Metadata إضافية
status: "active"                       # active, deprecated, draft
priority: "high"                       # high, medium, low
difficulty: "beginner"                 # beginner, intermediate, advanced
estimated_read_time: "30 minutes"      # الوقت المتوقع للقراءة
estimated_usage_time: "2-4 hours"     # الوقت المتوقع للاستخدام (إذا كان guide)
last_reviewed: "2024-12-06"           # آخر مراجعة

# 📅 التواريخ
created: "2024-12-06"
updated: "2024-12-06"

# 🔗 روابط ذات صلة
related:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md
  - 03_TESTING/TEST_EXECUTION_WORKSHEET.md
see_also:
  - 03_TESTING/manual_test_checklist/README.md
  - 07_TRACKING/TEST_TRACKING.md

# 📌 معلومات إضافية
prerequisites:                         # متطلبات سابقة
  - "فهم أساسي لنظام HishamOS"
  - "إعداد البيئة للتطوير"
tools_needed:                          # الأدوات المطلوبة
  - "Browser (Chrome/Firefox)"
  - "Postman/Insomnia"
  - "Terminal"
---

# المحتوى الفعلي للوثيقة...
```

---

## 📝 أمثلة عملية

### مثال 1: دليل اختبار (QA/Tester Focus)

```markdown
---
title: "Quick Start Testing Guide"
description: "دليل سريع للبدء في اختبار نظام HishamOS في 5 دقائق. يحتوي على خطوات واضحة لاختبار المكونات الأساسية."

category: "Testing"
subcategory: "Quick Start"

purpose: |
  تسهيل عملية البدء في اختبار النظام للمختبرين الجدد.
  توفير مسار واضح ومباشر للاختبارات الأساسية.

target_audience:
  primary:
    - QA / Tester                    # ⭐ الجمهور الأساسي
    - Developer                      # يستخدمونها كثيراً
  secondary:
    - Technical Lead                 # قد يراجعونها
    - Project Manager                # للفهم العام

# 🔄 المراحل المستخدمة فيها
applicable_phases:
  primary:
    - Testing                         # ⭐ المرحلة الأساسية - مرحلة الاختبار
    - QA                              # ⭐ مرحلة ضمان الجودة
    - UAT                             # ⭐ اختبار القبول للمستخدم
  secondary:
    - Development                     # أثناء التطوير (لاختبار الكود)

tags:
  - testing
  - quick-start
  - manual-testing
  - uat
  - guide

status: "active"
priority: "high"
difficulty: "beginner"
estimated_read_time: "15 minutes"
estimated_usage_time: "2-4 hours"

related:
  - 03_TESTING/UAT_TESTING_CHECKLIST.md
---
```

### مثال 2: دليل تطوير (Developer Focus)

```markdown
---
title: "Master Development Guide"
description: "دليل شامل للتطوير في HishamOS. يتضمن إعداد البيئة، أفضل الممارسات، ومعمارية النظام."

category: "Development"
subcategory: "Guide"

purpose: |
  توفير دليل مرجعي شامل للمطورين الجدد في المشروع.
  شرح المعمارية، أفضل الممارسات، وأدوات التطوير.

target_audience:
  primary:
    - Developer                      # ⭐ الجمهور الأساسي
    - Technical Lead                 # ⭐ مهم لهم جداً
  secondary:
    - DevOps                         # للفهم التقني
    - CTO / Technical Lead           # للمراجعة

# 🔄 المراحل المستخدمة فيها
applicable_phases:
  primary:
    - Development                     # ⭐ المرحلة الأساسية - التطوير
    - Code Review                     # ⭐ مراجعة الكود
  secondary:
    - Planning                        # أثناء التخطيط (للفهم التقني)
    - Design                          # أثناء التصميم (للفهم المعماري)
    - Maintenance                     # أثناء الصيانة

tags:
  - development
  - guide
  - architecture
  - best-practices
  - setup

status: "active"
priority: "critical"
difficulty: "intermediate"
estimated_read_time: "60 minutes"
estimated_usage_time: "Ongoing reference"

related:
  - 02_DESIGN/ARCHITECTURE/
  - 05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md
---
```

### مثال 3: تقرير حالة (Project Manager/CTO Focus)

```markdown
---
title: "Project Status Report - December 2024"
description: "تقرير شامل عن حالة المشروع الحالية، الإنجازات، والتحديات."

category: "Core"
subcategory: "Status"

purpose: |
  توفير نظرة شاملة عن حالة المشروع لاتخاذ القرارات.
  تتبع التقدم والإنجازات.

target_audience:
  primary:
    - Project Manager                # ⭐ الجمهور الأساسي
    - CTO / Technical Lead           # ⭐ مهم جداً
  secondary:
    - Business Analyst               # للفهم العام
    - Stakeholders                   # للإطلاع

# 🔄 المراحل المستخدمة فيها
applicable_phases:
  primary:
    - Planning                        # ⭐ للتخطيط المستقبلي
    - All Phases                      # ⭐ في جميع المراحل (مرجع مستمر)
  secondary:
    - Requirements Gathering          # أثناء جمع المتطلبات
    - Development                     # لمراقبة التقدم
    - Testing                         # لمعرفة ما تم إنجازه

tags:
  - project-status
  - status-report
  - dec-2024
  - progress
  - milestones

status: "active"
priority: "medium"
difficulty: "beginner"
estimated_read_time: "20 minutes"
estimated_usage_time: "Reference"

related:
  - 09_PHASES/PHASE_6/PHASE_6_PROGRESS.md
  - 07_TRACKING/PROJECT_ROADMAP.md
---
```

### مثال 4: وثيقة متعددة الأدوار (Multi-Role)

```markdown
---
title: "Command Library Documentation"
description: "توثيق شامل لجميع الأوامر المتاحة في HishamOS (250+ أمر)."

category: "Commands"
subcategory: "Library"

purpose: |
  توفير مرجع شامل لجميع الأوامر المتاحة في النظام.
  يساعد المطورين في كتابة الأوامر، المختبرين في الاختبار، والمستخدمين في الاستخدام.

target_audience:
  primary:
    - Developer                      # ⭐ لكتابة الأوامر
    - QA / Tester                    # ⭐ لاختبار الأوامر
  secondary:
    - Business Analyst               # للفهم
    - Technical Writer               # للتوثيق
    - End User                       # للاستخدام

# 🔄 المراحل المستخدمة فيها (متعددة!)
applicable_phases:
  primary:
    - Development                     # ⭐ أثناء التطوير (كتابة الأوامر)
    - Testing                         # ⭐ أثناء الاختبار (اختبار الأوامر)
    - Code Review                     # ⭐ أثناء مراجعة الكود (التحقق)
  secondary:
    - Requirements Gathering          # أثناء جمع المتطلبات (لفهم الإمكانيات)
    - Design                          # أثناء التصميم (لتصميم الأوامر الجديدة)
    - Maintenance                     # أثناء الصيانة (المرجع المستمر)
    - Documentation                   # أثناء التوثيق (كتابة التوثيق)

tags:
  - commands
  - library
  - reference
  - api
  - documentation

status: "active"
priority: "high"
difficulty: "intermediate"
estimated_read_time: "45 minutes"
estimated_usage_time: "Ongoing reference"

related:
  - 08_COMMANDS/COMMAND_TESTING_GUIDE.md
  - 03_TESTING/COMMAND_TESTING_CHECKLIST.md
---
```

---

## 🔍 نظام الفلترة حسب الأدوار

### Fliter by Role - أمثلة:

#### للمطورين (Developers):
```yaml
target_audience:
  primary:
    - Developer
  OR
  secondary:
    - Developer
```

#### للمختبرين (QA/Testers):
```yaml
target_audience:
  primary:
    - QA / Tester
  OR
  secondary:
    - QA / Tester
```

#### لمديري المشاريع (Project Managers):
```yaml
target_audience:
  primary:
    - Project Manager
  OR
  secondary:
    - Project Manager
```

---

## 📊 قائمة الأدوار الكاملة

### الأدوار الأساسية:

```yaml
roles_list:
  - "Developer"                      # المطورون
  - "QA / Tester"                    # المختبرون
  - "Business Analyst"               # المحللون الأعمال
  - "Project Manager"                # مديرو المشاريع
  - "DevOps"                         # DevOps Engineers
  - "Technical Lead"                 # القادة التقنيون
  - "CTO / Technical Lead"           # CTO والقادة التقنيون
  - "Scrum Master"                   # Scrum Masters
  - "UI/UX Designer"                 # مصممو واجهات المستخدم
  - "Technical Writer"               # الكتّاب التقنيون
  - "Administrator"                  # المسؤولون
  - "End User"                       # المستخدمون النهائيون
  - "Stakeholder"                    # أصحاب المصلحة
```

---

## 🔄 قائمة المراحل/العمليات الكاملة

### المراحل الأساسية:

```yaml
phases_list:
  # مرحلة ما قبل التطوير
  - "Requirements Gathering"         # جمع المتطلبات
  - "Planning"                       # التخطيط
  - "Design"                         # التصميم
  
  # مرحلة التطوير
  - "Development"                    # التطوير
  - "Code Review"                    # مراجعة الكود
  
  # مرحلة الاختبار
  - "Testing"                        # الاختبار
  - "QA"                             # ضمان الجودة
  - "UAT"                            # اختبار القبول للمستخدم
  
  # مرحلة النشر
  - "Deployment"                     # النشر
  - "Production"                     # الإنتاج
  
  # مرحلة الصيانة
  - "Maintenance"                    # الصيانة
  - "Documentation"                  # التوثيق
  
  # خاص
  - "All Phases"                     # في جميع المراحل (مرجع مستمر)
```

### أمثلة على استخدام المراحل:

```yaml
# وثيقة لجمع المتطلبات
applicable_phases:
  primary:
    - Requirements Gathering
    - Planning

# وثيقة للتطوير
applicable_phases:
  primary:
    - Development
    - Code Review

# وثيقة للاختبار
applicable_phases:
  primary:
    - Testing
    - QA
    - UAT

# وثيقة للنشر
applicable_phases:
  primary:
    - Deployment
    - Production

# وثيقة مرجعية (في جميع المراحل)
applicable_phases:
  primary:
    - All Phases
```

---

## 🎯 نظام Priority حسب الدور

### High Priority Roles:
- **Developer** → Development guides, API docs, Architecture
- **QA / Tester** → Testing guides, Checklists, Test plans
- **Project Manager** → Status reports, Roadmaps, Plans
- **Technical Lead** → Architecture, Design, Technical decisions

### Medium Priority Roles:
- **Business Analyst** → Requirements, User stories, Analysis
- **DevOps** → Deployment guides, Infrastructure
- **Administrator** → Admin guides, User management

### Low Priority (Reference):
- **End User** → User guides, Walkthroughs
- **Stakeholder** → Status reports, Overviews

---

## ✅ Checklist لإضافة Metadata

- [ ] **Title** - عنوان واضح
- [ ] **Description** - وصف مختصر (2-3 أسطر)
- [ ] **Purpose** - الهدف الأساسي (مهم جداً!)
- [ ] **Target Audience (Primary)** - الجمهور الأساسي (يستخدمونها كثيراً)
- [ ] **Target Audience (Secondary)** - الجمهور الثانوي (يستخدمونها أحياناً)
- [ ] **Tags** - tags شاملة للبحث
- [ ] **Difficulty** - مستوى الصعوبة
- [ ] **Estimated Read Time** - الوقت المتوقع للقراءة
- [ ] **Related** - روابط للمستندات ذات الصلة
- [ ] **Prerequisites** - المتطلبات السابقة (إن وجدت)

---

**هذا النظام سيسمح بالفلترة الدقيقة حسب الدور والهدف!**

