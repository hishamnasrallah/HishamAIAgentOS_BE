# File Generation Integration - Workflow Integration

**Document Type:** Integration Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** ../04_BACKEND/03_SERVICES_IMPLEMENTATION.md, ../04_BACKEND/02_MODELS_IMPLEMENTATION.md  
**File Size:** 489 lines

---

## 📋 Purpose

This document describes how file generation integrates with workflows and agents.

---

## 🔗 Integration Points

### Integration 1: Workflow Step Integration

**File Generation Step:**
```yaml
- id: generate_files
  type: file_generation
  config:
    project_id: "{{ project_id }}"
    structure:
      src/main.py: "{{ code_content }}"
      tests/test_main.py: "{{ test_content }}"
```

**Execution:**
1. Workflow executor identifies step type as `file_generation`
2. Executor calls `ProjectGenerator.generate_project_structure()`
3. Files created on filesystem
4. `ProjectFile` records created in database
5. `GeneratedProject` statistics updated

---

### Integration 2: Agent Integration

**Agent requests file generation:**
```python
# Agent generates code content
code_content = generate_code(...)

# Request file generation via context
file_generator = context.get('file_generator')
if file_generator:
    file_generator.write_file(
        path="src/main.py",
        content=code_content
    )
```

---

### Integration 3: Database Integration

**File creation triggers:**
- `ProjectFile` model creation
- `GeneratedProject` statistics update (via signals)
- File metadata stored

---

## 🔗 Related Documentation

- **Services:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`
- **Models:** `../04_BACKEND/02_MODELS_IMPLEMENTATION.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

