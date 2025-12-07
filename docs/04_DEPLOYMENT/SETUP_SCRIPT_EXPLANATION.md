---
title: Setup Script Explanation
description: شرح مفصل لوظيفة سكربت setup_multi_repos.ps1 - Detailed explanation of setup_multi_repos.ps1 script

category: Deployment
subcategory: Setup
language: ar
original_language: ar

purpose: |
  شرح شامل لوظيفة سكربت إعداد المستودعات المتعددة وكيفية استخدامه

target_audience:
  primary:
    - Developer
    - DevOps
  secondary:
    - Project Manager

applicable_phases:
  primary:
    - Development
    - Deployment
  secondary: []

tags:
  - script
  - automation
  - setup
  - git
  - repository
  - powershell

status: active
priority: medium
difficulty: beginner
completeness: 100%

version: 1.0
last_updated: 2024-12-06
review_frequency: quarterly

author: DevOps Team
---

# شرح سكربت setup_multi_repos.ps1

## 🎯 الوظيفة الأساسية

السكربت يقوم بـ **تقسيم المشروع الواحد (Monorepo) إلى 3 مستودعات Git منفصلة**:
1. **Backend** (`backend/`)
2. **Frontend** (`frontend/`)
3. **Infrastructure** (`infrastructure/`)

---

## 📋 ماذا يفعل السكربت بالضبط؟

### 1. نقل الوثائق إلى Backend (اختياري)
```powershell
.\setup_multi_repos.ps1 -MoveDocsToBackend
```
- ينقل مجلد `docs/` من الجذر إلى `backend/docs/`
- يحذف `backend/docs/` القديم إذا كان موجوداً
- الوثائق ستصبح جزء من مستودع Backend

### 2. تهيئة Git في كل مجلد
- ينشئ `.git` في كل مجلد (backend, frontend, infrastructure)
- يضيف جميع الملفات
- ينشئ commit أولي

### 3. إضافة Remote Repositories (اختياري)
```powershell
.\setup_multi_repos.ps1 -PushToRemote -BackendRepo "https://github.com/..." ...
```
- يضيف روابط GitHub لكل مستودع
- يمكن دفع الكود مباشرة

---

## 🚀 طرق الاستخدام

### الطريقة 1: التحضير فقط (بدون نقل docs)
```powershell
.\setup_multi_repos.ps1
```
**النتيجة:**
- ✅ تهيئة Git في 3 مجلدات
- ✅ إنشاء commits
- ❌ لا ينقل docs
- ❌ لا يضيف remote
- ❌ لا يدفع إلى GitHub

**متى تستخدمها:** عندما تريد التحضير فقط وتقوم بالنقل والدفع يدوياً

---

### الطريقة 2: نقل docs إلى backend
```powershell
.\setup_multi_repos.ps1 -MoveDocsToBackend
```
**النتيجة:**
- ✅ نقل `docs/` إلى `backend/docs/`
- ✅ حذف `backend/docs/` القديم
- ✅ تهيئة Git في 3 مجلدات
- ✅ إنشاء commits
- ❌ لا يضيف remote
- ❌ لا يدفع إلى GitHub

**متى تستخدمها:** عندما تريد نقل docs قبل إعداد Git

---

### الطريقة 3: إعداد كامل مع دفع (Full Setup)
```powershell
.\setup_multi_repos.ps1 `
  -MoveDocsToBackend `
  -PushToRemote `
  -BackendRepo "https://github.com/your-org/hishamos-backend.git" `
  -FrontendRepo "https://github.com/your-org/hishamos-frontend.git" `
  -InfraRepo "https://github.com/your-org/hishamos-infrastructure.git"
```

**النتيجة:**
- ✅ نقل docs
- ✅ تهيئة Git
- ✅ إضافة remote repositories
- ✅ دفع الكود إلى GitHub

**متى تستخدمها:** عندما تكون جاهزاً لدفع كل شيء مباشرة

---

## 📝 خطوات ما بعد السكربت

إذا لم تستخدم `-PushToRemote`، ستحتاج:

### 1. إنشاء المستودعات على GitHub
- `hishamos-backend`
- `hishamos-frontend`
- `hishamos-infrastructure`

### 2. إضافة Remote URLs
```powershell
cd backend
git remote add origin https://github.com/your-org/hishamos-backend.git
git push -u origin main

cd ../frontend
git remote add origin https://github.com/your-org/hishamos-frontend.git
git push -u origin main

cd ../infrastructure
git remote add origin https://github.com/your-org/hishamos-infrastructure.git
git push -u origin main
```

---

## ⚠️ تحذيرات مهمة

1. **انسخ المشروع أولاً** - السكربت سيغير البنية
2. **تأكد من عدم وجود `.git`** في المجلدات قبل التشغيل
3. **النسخ الاحتياطية** - تأكد من وجود backup

---

## 🔍 ماذا يحدث بالتفصيل؟

### Step 1: نقل الوثائق (إذا استخدمت `-MoveDocsToBackend`)
```
قبل:  hishamAiAgentOS/
        ├── docs/           ← الوثائق هنا
        └── backend/

بعد:  hishamAiAgentOS/
        └── backend/
            └── docs/       ← الوثائق هنا الآن
```

### Step 2: تهيئة Git
```powershell
cd backend
git init
git add .
git commit -m "Initial Backend repository setup"

cd ../frontend
git init
git add .
git commit -m "Initial Frontend repository setup"

cd ../infrastructure
git init
git add .
git commit -m "Initial Infrastructure repository setup"
```

### Step 3: إضافة Remote (إذا استخدمت `-PushToRemote`)
```powershell
git remote add origin <URL>
git push -u origin main
```

---

## ✅ Checklist قبل التشغيل

- [ ] نسخة احتياطية من المشروع
- [ ] إنشاء المستودعات على GitHub (إذا كنت ستستخدم `-PushToRemote`)
- [ ] التأكد من عدم وجود `.git` في المجلدات الفرعية
- [ ] التأكد من أن جميع التغييرات محفوظة

---

## 📊 مثال على المخرجات

```
=== HishamOS Multi-Repository Setup ===

Project root: C:\Users\hisha\PycharmProjects\hishamAiAgentOS

Step 1: Moving docs to backend...
  ✓ Docs moved to backend/docs

Step 2: Initializing repositories...

Setting up Backend...
  ✓ Git initialized
  ✓ Initial commit created

Setting up Frontend...
  ✓ Git initialized
  ✓ Initial commit created

Setting up Infrastructure...
  ✓ Git initialized
  ✓ Initial commit created

=== Setup Summary ===
  ✓ backend - Ready
  ✓ frontend - Ready
  ✓ infrastructure - Ready

=== Setup Complete ===
```

---

## 🎯 النتيجة النهائية

بعد تشغيل السكربت:

```
hishamAiAgentOS/
├── backend/          ← Git repo (مع docs/ بداخله)
├── frontend/         ← Git repo
└── infrastructure/   ← Git repo
```

كل مجلد أصبح مستودع Git مستقل يمكن دفعه إلى GitHub بشكل منفصل!

---

**آخر تحديث:** 06 ديسمبر 2024

