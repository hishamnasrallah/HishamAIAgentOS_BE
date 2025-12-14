# API Specification - AI Model Evaluation Platform

**Document Type:** API Documentation  
**Version:** 1.0.0  
**Created Date:** December 13, 2025  
**Status:** Draft  

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Model Registry API](#model-registry-api)
4. [Benchmark API](#benchmark-api)
5. [Evaluation API](#evaluation-api)
6. [Metrics API](#metrics-api)
7. [A/B Testing API](#ab-testing-api)
8. [Experimentation API](#experimentation-api)
9. [Selection API](#selection-api)
10. [Error Handling](#error-handling)

---

## 🌐 API Overview

### Base URL
```
/api/v1/evaluation/
```

### API Versioning
- Current version: `v1`
- Version specified in URL path
- Backward compatibility maintained within major versions

### Response Format
All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2025-12-13T10:00:00Z",
    "request_id": "req_abc123",
    "version": "1.0"
  },
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 100,
    "total_pages": 4
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "metadata": {
    "timestamp": "2025-12-13T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## 🔐 Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

Organization context is automatically determined from the authenticated user.

---

## 📦 Model Registry API

### List Models

**GET** `/models/`

**Query Parameters:**
- `platform` (optional): Filter by platform (openai, anthropic, google)
- `status` (optional): Filter by status (active, deprecated, experimental)
- `capabilities` (optional): Filter by capabilities (comma-separated)
- `search` (optional): Search by name or description
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 25, max: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "GPT-4",
      "display_name": "GPT-4",
      "description": "...",
      "platform": "openai",
      "platform_model_id": "gpt-4",
      "version": "1.0.0",
      "capabilities": ["text-generation", "code-generation"],
      "status": "active",
      "default_config": {
        "temperature": 0.7,
        "max_tokens": 2000
      },
      "statistics": {
        "total_evaluations": 150,
        "avg_accuracy": 0.92,
        "avg_latency_ms": 1250,
        "avg_cost_per_1k_tokens": 0.03
      },
      "created_at": "2025-12-01T00:00:00Z",
      "updated_at": "2025-12-13T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### Register Model

**POST** `/models/`

**Request Body:**
```json
{
  "name": "GPT-4",
  "display_name": "GPT-4",
  "description": "OpenAI's GPT-4 model",
  "platform": "openai",
  "platform_model_id": "gpt-4",
  "version": "1.0.0",
  "capabilities": ["text-generation", "code-generation"],
  "default_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "metadata": {},
  "tags": ["latest", "recommended"]
}
```

**Response:** 201 Created with model object

### Get Model

**GET** `/models/{id}/`

**Response:** Single model object

### Update Model

**PUT** `/models/{id}/`

**Request Body:** Partial model data

**Response:** Updated model object

### Delete Model

**DELETE** `/models/{id}/`

**Response:** 204 No Content

### Get Model Versions

**GET** `/models/{id}/versions/`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "version": "1.0.0",
      "is_latest": true,
      "created_at": "2025-12-01T00:00:00Z"
    }
  ]
}
```

---

## 📊 Benchmark API

### List Benchmarks

**GET** `/benchmarks/`

**Query Parameters:**
- `category` (optional): Filter by category
- `is_standard` (optional): Filter standard/custom (true/false)
- `search` (optional): Search by name
- `page`, `page_size`: Pagination

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Code Generation Quality",
      "description": "...",
      "category": "code-generation",
      "is_standard": true,
      "version": "1.0.0",
      "dataset": {
        "id": "uuid",
        "name": "Code Generation Test Set",
        "total_test_cases": 100
      },
      "evaluation_criteria": {
        "metrics": ["accuracy", "latency", "code_quality"],
        "scoring_method": "weighted_average"
      },
      "total_evaluations": 50,
      "created_at": "2025-12-01T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### Create Benchmark

**POST** `/benchmarks/`

**Request Body:**
```json
{
  "name": "Custom Benchmark",
  "description": "...",
  "category": "custom",
  "is_standard": false,
  "dataset_id": "uuid",
  "evaluation_criteria": {
    "metrics": ["accuracy", "latency"],
    "scoring_method": "average"
  },
  "tags": []
}
```

### Get Benchmark

**GET** `/benchmarks/{id}/`

### Update Benchmark

**PUT** `/benchmarks/{id}/`

### Datasets API

**GET** `/datasets/` - List datasets  
**POST** `/datasets/` - Create dataset  
**GET** `/datasets/{id}/` - Get dataset  
**PUT** `/datasets/{id}/` - Update dataset  
**DELETE** `/datasets/{id}/` - Delete dataset

---

## 🔬 Evaluation API

### Create Evaluation

**POST** `/evaluations/`

**Request Body:**
```json
{
  "model_id": "uuid",
  "benchmark_id": "uuid",
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "evaluation_config": {
    "parallel_execution": true,
    "max_concurrent": 10
  },
  "metadata": {}
}
```

**Response:** 202 Accepted
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "pending",
    "progress": 0.0,
    "created_at": "2025-12-13T10:00:00Z"
  }
}
```

### Get Evaluation

**GET** `/evaluations/{id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "model": { ... },
    "benchmark": { ... },
    "status": "completed",
    "progress": 1.0,
    "total_test_cases": 100,
    "completed_test_cases": 100,
    "failed_test_cases": 0,
    "aggregated_results": {
      "accuracy": 0.92,
      "avg_latency_ms": 1250,
      "total_cost": 5.50,
      "total_tokens": 150000
    },
    "started_at": "2025-12-13T10:00:00Z",
    "completed_at": "2025-12-13T10:05:00Z",
    "duration_seconds": 300
  }
}
```

### Get Evaluation Status

**GET** `/evaluations/{id}/status/`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "progress": 0.65,
    "completed_test_cases": 65,
    "total_test_cases": 100
  }
}
```

### Get Evaluation Results

**GET** `/evaluations/{id}/results/`

**Query Parameters:**
- `page`, `page_size`: Pagination for test case results

**Response:**
```json
{
  "success": true,
  "data": {
    "aggregated_results": { ... },
    "test_case_results": [
      {
        "test_case_index": 0,
        "input_data": { ... },
        "expected_output": { ... },
        "actual_output": { ... },
        "metrics": {
          "accuracy": 1.0,
          "latency_ms": 1200,
          "tokens_used": 1500,
          "cost": 0.05
        },
        "success": true,
        "executed_at": "2025-12-13T10:00:30Z"
      }
    ]
  },
  "pagination": { ... }
}
```

### Cancel Evaluation

**POST** `/evaluations/{id}/cancel/`

**Response:** 200 OK

### Batch Evaluation

**POST** `/evaluations/batch/`

**Request Body:**
```json
{
  "model_ids": ["uuid1", "uuid2", "uuid3"],
  "benchmark_id": "uuid",
  "evaluation_config": { ... }
}
```

**Response:** List of evaluation runs

---

## 📈 Metrics API

### Get Model Metrics

**GET** `/models/{id}/metrics/`

**Query Parameters:**
- `metric_type` (optional): Filter by metric type
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)
- `benchmark_id` (optional): Filter by benchmark
- `aggregation` (optional): hourly, daily, weekly, monthly

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "metric_type": "accuracy",
      "value": 0.92,
      "unit": "%",
      "timestamp": "2025-12-13T10:00:00Z",
      "benchmark_id": "uuid"
    }
  ]
}
```

### Get Aggregated Metrics

**GET** `/models/{id}/metrics/aggregated/`

**Query Parameters:**
- `period`: hourly, daily, weekly, monthly
- `start_date`, `end_date`: Date range

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "daily",
    "period_start": "2025-12-01T00:00:00Z",
    "period_end": "2025-12-13T00:00:00Z",
    "metrics": {
      "accuracy": {
        "min": 0.85,
        "max": 0.95,
        "avg": 0.92,
        "std_dev": 0.03
      },
      "latency_ms": { ... },
      "cost_per_1k_tokens": { ... }
    },
    "sample_count": 150
  }
}
```

### Compare Models

**POST** `/metrics/compare/`

**Request Body:**
```json
{
  "model_ids": ["uuid1", "uuid2"],
  "metric_types": ["accuracy", "latency", "cost"],
  "start_date": "2025-12-01T00:00:00Z",
  "end_date": "2025-12-13T00:00:00Z",
  "benchmark_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "model_id": "uuid1",
        "metrics": { ... }
      }
    ],
    "comparison": {
      "accuracy": {
        "winner": "uuid1",
        "difference": 0.05,
        "significance": "significant"
      }
    }
  }
}
```

---

## 🔬 A/B Testing API

### Create A/B Test

**POST** `/ab-tests/`

**Request Body:**
```json
{
  "name": "GPT-4 vs Claude-3 Comparison",
  "description": "...",
  "model_ids": ["uuid1", "uuid2"],
  "dataset_id": "uuid",
  "test_config": {
    "significance_level": 0.05,
    "min_sample_size": 100
  }
}
```

**Response:** 201 Created with A/B test object

### Execute A/B Test

**POST** `/ab-tests/{id}/execute/`

**Response:** 202 Accepted

### Get A/B Test

**GET** `/ab-tests/{id}/`

### Get A/B Test Results

**GET** `/ab-tests/{id}/results/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "completed",
    "models": [
      {
        "model_id": "uuid1",
        "results": {
          "accuracy": 0.92,
          "avg_latency_ms": 1250,
          "total_cost": 5.50
        }
      }
    ],
    "statistical_analysis": {
      "accuracy": {
        "model_1_mean": 0.92,
        "model_2_mean": 0.88,
        "difference": 0.04,
        "p_value": 0.001,
        "significant": true,
        "winner": "uuid1"
      }
    },
    "overall_winner": "uuid1",
    "completed_at": "2025-12-13T10:30:00Z"
  }
}
```

---

## 🧪 Experimentation API

### List Experiments

**GET** `/experiments/`

**Query Parameters:**
- `status`: Filter by status
- `search`: Search by name
- `page`, `page_size`: Pagination

### Create Experiment

**POST** `/experiments/`

**Request Body:**
```json
{
  "name": "Temperature Impact Study",
  "description": "...",
  "hypothesis": "Lower temperature improves accuracy",
  "objective": "Find optimal temperature",
  "experiment_config": {
    "models": ["uuid"],
    "benchmarks": ["uuid"],
    "parameters": {
      "temperature": [0.1, 0.5, 0.7, 1.0]
    }
  },
  "tags": ["optimization"]
}
```

### Get Experiment

**GET** `/experiments/{id}/`

### Run Experiment

**POST** `/experiments/{id}/run/`

**Request Body (optional):**
```json
{
  "run_config": { ... },
  "name": "Run #1"
}
```

**Response:** Experiment run object

### Get Experiment Runs

**GET** `/experiments/{id}/runs/`

**Response:** List of runs with comparison

### Compare Runs

**POST** `/experiments/{id}/runs/compare/`

**Request Body:**
```json
{
  "run_ids": ["uuid1", "uuid2"]
}
```

**Response:** Comparison results

---

## 🎯 Selection API

### Get Model Recommendation

**POST** `/selection/recommend/`

**Request Body:**
```json
{
  "capabilities": ["text-generation", "code-generation"],
  "constraints": {
    "max_cost_per_1k_tokens": 0.05,
    "max_latency_ms": 2000,
    "min_accuracy": 0.90
  },
  "use_case": "code-generation",
  "optimization_goal": "balanced" // cost, performance, quality, balanced
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommended_model": {
      "id": "uuid",
      "name": "GPT-4",
      "score": 0.95,
      "reasoning": "..."
    },
    "candidates": [
      {
        "model_id": "uuid",
        "score": 0.95,
        "metrics": { ... }
      }
    ],
    "explanation": "Selected based on high accuracy (0.92) and acceptable cost..."
  }
}
```

### Get Ranked Recommendations

**POST** `/selection/ranked/`

**Request Body:** Same as recommend

**Query Parameters:**
- `top_k`: Number of recommendations (default: 5)

**Response:** List of ranked recommendations

### Explain Selection

**POST** `/selection/explain/`

**Request Body:**
```json
{
  "model_id": "uuid",
  "capabilities": [...],
  "constraints": { ... }
}
```

**Response:** Detailed explanation of why this model was/would be selected

---

## ❌ Error Handling

### Error Codes

- `MODEL_NOT_FOUND` (404)
- `BENCHMARK_NOT_FOUND` (404)
- `EVALUATION_NOT_FOUND` (404)
- `EVALUATION_ALREADY_RUNNING` (400)
- `EVALUATION_CANNOT_BE_CANCELLED` (400)
- `INVALID_MODEL_CONFIG` (400)
- `INSUFFICIENT_PERMISSIONS` (403)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_ERROR` (500)

### Example Error Response

```json
{
  "success": false,
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model with ID 'uuid' not found",
    "details": {
      "model_id": "uuid"
    }
  },
  "metadata": {
    "timestamp": "2025-12-13T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

**Next Steps:** Review frontend design document for UI specifications.

