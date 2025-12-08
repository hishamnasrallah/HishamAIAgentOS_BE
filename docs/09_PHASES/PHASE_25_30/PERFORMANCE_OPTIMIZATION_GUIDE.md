# Performance Optimization Guide

**Date:** December 8, 2024  
**Status:** Active

---

## 🎯 Performance Targets

### API Response Times
- **p95 Response Time:** < 200ms
- **p99 Response Time:** < 500ms
- **Average Response Time:** < 100ms

### Database Queries
- **List Endpoints:** < 10 queries per request
- **Detail Endpoints:** < 5 queries per request
- **No N+1 Query Problems**

### Concurrent Users
- **Target:** 1000+ concurrent users
- **Success Rate:** > 99%

---

## 🔧 Optimization Techniques

### 1. Database Query Optimization

#### Use `select_related()` for ForeignKey/OneToOne
```python
# Bad: N+1 queries
agents = Agent.objects.all()
for agent in agents:
    print(agent.created_by.email)  # New query for each agent

# Good: Single query
agents = Agent.objects.select_related('created_by').all()
for agent in agents:
    print(agent.created_by.email)  # No additional queries
```

#### Use `prefetch_related()` for Reverse Relations
```python
# Bad: N+1 queries
projects = Project.objects.all()
for project in projects:
    print(project.stories.count())  # New query for each project

# Good: Single query
projects = Project.objects.prefetch_related('stories').all()
for project in projects:
    print(project.stories.count())  # No additional queries
```

#### Use `only()` and `defer()` to Limit Fields
```python
# Only fetch needed fields
agents = Agent.objects.only('id', 'name', 'agent_id').all()
```

### 2. Caching

#### Function Result Caching
```python
from core.performance import cache_result

@cache_result(timeout=600)
def expensive_computation():
    # Expensive operation
    return result
```

#### View Caching
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    # View code
```

### 3. Database Indexing

Ensure indexes exist on:
- Foreign keys
- Frequently queried fields
- Date/time fields used in filtering
- Search fields

### 4. Pagination

Always use pagination for list endpoints:
```python
from rest_framework.pagination import PageNumberPagination

class MyPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 5. Async Operations

Use Celery for long-running tasks:
```python
from celery import shared_task

@shared_task
def process_large_dataset(data):
    # Long-running operation
    pass
```

---

## 📊 Monitoring Performance

### Query Monitoring
```python
from core.performance import query_count_monitor

@query_count_monitor
def my_view(request):
    # View code
```

### Performance Monitoring
```python
from core.performance import performance_monitor

@performance_monitor
def my_view(request):
    # View code
```

### Django Debug Toolbar
Enable in development to see:
- Query count and time
- Cache hits/misses
- Template rendering time

---

## 🧪 Performance Testing

### Run Performance Tests
```bash
pytest tests/performance/ -v
```

### Load Testing
```bash
pytest tests/load/ -v
```

### Manual Load Testing with Locust
```bash
pip install locust
locust -f tests/load/locustfile.py
```

---

## 📈 Optimization Checklist

- [ ] All list endpoints use pagination
- [ ] All ForeignKey relationships use `select_related()`
- [ ] All reverse relations use `prefetch_related()`
- [ ] Expensive operations are cached
- [ ] Database indexes are optimized
- [ ] Long-running tasks use Celery
- [ ] API response times < 200ms (p95)
- [ ] Query count < 10 per request
- [ ] No N+1 query problems
- [ ] Load tested with 1000+ concurrent users

---

**Last Updated:** December 8, 2024

