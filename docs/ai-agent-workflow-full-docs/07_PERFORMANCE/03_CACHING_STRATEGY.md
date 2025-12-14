# Caching Strategy - Performance Optimization

**Document Type:** Caching Strategy  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_OPTIMIZATION_STRATEGIES.md  
**File Size:** 481 lines

---

## 📋 Purpose

This document describes the caching strategy for the AI agent workflow enhancement.

---

## 💾 Caching Layers

### Layer 1: API Response Caching

**Cache:**
- Generated project listings
- File listings
- Export job statuses

**TTL:**
- List responses: 60 seconds
- Detail responses: 300 seconds
- Status responses: 5 seconds

---

### Layer 2: File Metadata Caching

**Cache:**
- File paths and metadata
- File tree structures

**TTL:**
- File metadata: 300 seconds
- File tree: 600 seconds

---

### Layer 3: Workflow Definition Caching

**Cache:**
- Parsed workflow definitions
- Step type registries

**TTL:**
- Workflow definitions: 600 seconds
- Invalidate on workflow update

---

## 🔗 Related Documentation

- **Optimization:** `02_OPTIMIZATION_STRATEGIES.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed  
**Last Updated:** 2025-12-13

