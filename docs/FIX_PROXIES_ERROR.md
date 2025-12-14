# Fix: "AsyncClient.__init__() got an unexpected keyword argument 'proxies'"

## Problem

You're seeing this error when trying to use OpenRouter or OpenAI adapters:

```
ERROR: Failed to initialize openrouter adapter: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```

## Cause

This is a version incompatibility between the `openai` library and `httpx`. The OpenAI library internally uses `httpx.AsyncClient`, and newer versions try to pass a `proxies` parameter that older `httpx` versions don't support.

## Solution

### Step 1: Update httpx

```bash
cd backend
pip install --upgrade httpx>=0.25.0
```

Or reinstall all dependencies:

```bash
pip install -r requirements/base.txt --upgrade
```

### Step 2: Restart Django

After updating httpx, restart your Django server:

```bash
python manage.py runserver
```

### Step 3: Test Again

Run the test script:

```bash
python scripts/test-openrouter-adapter.py
```

You should now see:

```
✓ Registry initialized
  Adapters available: ['openrouter', 'mock']
✓ OpenRouter adapter found
```

## Verification

After fixing, you should see adapter initialization in Django logs:

```
INFO: Initialized adapter for openrouter
INFO: Registry initialized with 2 adapters
```

## Alternative Fix (If Above Doesn't Work)

If updating httpx doesn't work, try downgrading the OpenAI library:

```bash
pip install openai==1.3.0
```

Or use a specific httpx version that's compatible:

```bash
pip install httpx==0.24.1
```

## Still Having Issues?

1. Check installed versions:
```bash
pip show openai httpx
```

2. Check for conflicting packages:
```bash
pip list | grep -i http
```

3. Try a clean reinstall:
```bash
pip uninstall openai httpx
pip install openai==1.10.0 httpx>=0.25.0
```

