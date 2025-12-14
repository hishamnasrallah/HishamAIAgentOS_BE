# Data Models - AI Model Evaluation Platform

**Document Type:** Database Schema Documentation  
**Version:** 1.0.0  
**Created Date:** December 13, 2025  
**Status:** Draft  

---

## 📋 Table of Contents

1. [Model Registry Models](#model-registry-models)
2. [Benchmark Models](#benchmark-models)
3. [Evaluation Models](#evaluation-models)
4. [Metrics Models](#metrics-models)
5. [A/B Testing Models](#ab-testing-models)
6. [Experimentation Models](#experimentation-models)
7. [Selection Models](#selection-models)
8. [Database Indexes](#database-indexes)
9. [Data Relationships](#data-relationships)

---

## 🗄️ Model Registry Models

### Model

**Purpose:** Store AI model metadata and versions

```python
class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Basic Information
    name = models.CharField(max_length=200)  # e.g., "GPT-4"
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Platform Information
    platform = models.CharField(max_length=50)  # openai, anthropic, google
    platform_model_id = models.CharField(max_length=200)  # e.g., "gpt-4", "claude-3-opus"
    
    # Versioning
    version = models.CharField(max_length=50, default="1.0.0")
    is_latest = models.BooleanField(default=True)
    parent_model = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Capabilities
    capabilities = models.ManyToManyField('ModelCapability', related_name='models')
    
    # Configuration
    default_config = models.JSONField(default=dict)  # temperature, max_tokens, etc.
    supported_configs = models.JSONField(default=list)  # Available configuration options
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('deprecated', 'Deprecated'),
            ('experimental', 'Experimental'),
            ('archived', 'Archived')
        ],
        default='active'
    )
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Custom metadata
    tags = models.JSONField(default=list)  # User-defined tags
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deprecated_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics (cached)
    total_evaluations = models.IntegerField(default=0)
    avg_accuracy = models.FloatField(null=True, blank=True)
    avg_latency_ms = models.FloatField(null=True, blank=True)
    avg_cost_per_1k_tokens = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'evaluation_models'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['platform', 'platform_model_id']),
            models.Index(fields=['status', '-created_at']),
        ]
        unique_together = [['organization', 'platform', 'platform_model_id', 'version']]
```

### ModelCapability

**Purpose:** Define model capabilities (tags)

```python
class ModelCapability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)  # e.g., "text-generation"
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)  # e.g., "generation", "analysis", "translation"
    
    class Meta:
        db_table = 'model_capabilities'
        verbose_name_plural = 'Model Capabilities'
```

---

## 📊 Benchmark Models

### BenchmarkSuite

**Purpose:** Define benchmark suites (standard or custom)

```python
class BenchmarkSuite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, default="1.0.0")
    
    # Type
    is_standard = models.BooleanField(default=False)  # Standard benchmark vs custom
    category = models.CharField(
        max_length=50,
        choices=[
            ('text-generation', 'Text Generation'),
            ('code-generation', 'Code Generation'),
            ('qa', 'Question Answering'),
            ('summarization', 'Summarization'),
            ('classification', 'Classification'),
            ('translation', 'Translation'),
            ('custom', 'Custom')
        ]
    )
    
    # Dataset Reference
    dataset = models.ForeignKey('EvaluationDataset', on_delete=models.PROTECT)
    
    # Evaluation Criteria
    evaluation_criteria = models.JSONField(default=dict)  # Metrics to calculate
    scoring_methodology = models.TextField(blank=True)  # How to score
    
    # Metadata
    metadata = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    
    # Statistics
    total_evaluations = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'benchmark_suites'
        indexes = [
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['is_standard', 'category']),
        ]
```

### EvaluationDataset

**Purpose:** Store test datasets for evaluation

```python
class EvaluationDataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Data Storage
    # Option 1: Store in database (for small datasets)
    test_cases = models.JSONField(default=list)  # List of test case dicts
    
    # Option 2: Reference external file (for large datasets)
    file_path = models.CharField(max_length=500, blank=True)  # Path to JSON/CSV file
    file_format = models.CharField(
        max_length=20,
        choices=[('json', 'JSON'), ('csv', 'CSV'), ('jsonl', 'JSONL')],
        blank=True
    )
    
    # Schema
    input_schema = models.JSONField(default=dict)  # Schema for inputs
    output_schema = models.JSONField(default=dict, blank=True)  # Schema for expected outputs
    
    # Statistics
    total_test_cases = models.IntegerField(default=0)
    has_ground_truth = models.BooleanField(default=False)  # Has expected outputs
    
    # Metadata
    metadata = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'evaluation_datasets'
        indexes = [
            models.Index(fields=['organization', '-created_at']),
        ]
```

---

## 🔬 Evaluation Models

### EvaluationRun

**Purpose:** Track evaluation executions

```python
class EvaluationRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # References
    model = models.ForeignKey('Model', on_delete=models.PROTECT)
    benchmark = models.ForeignKey('BenchmarkSuite', on_delete=models.PROTECT)
    dataset = models.ForeignKey('EvaluationDataset', on_delete=models.PROTECT)
    
    # Configuration
    model_config = models.JSONField(default=dict)  # Override model default config
    evaluation_config = models.JSONField(default=dict)  # Evaluation-specific settings
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    
    # Progress
    progress = models.FloatField(default=0.0)  # 0.0 to 1.0
    total_test_cases = models.IntegerField(default=0)
    completed_test_cases = models.IntegerField(default=0)
    failed_test_cases = models.IntegerField(default=0)
    
    # Results (aggregated)
    aggregated_results = models.JSONField(default=dict)  # Overall metrics
    
    # Execution Info
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Cost Tracking
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    
    # Error Information
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluation_runs'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['model', '-created_at']),
            models.Index(fields=['benchmark', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
```

### EvaluationResult

**Purpose:** Store results for individual test cases

```python
class EvaluationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    evaluation_run = models.ForeignKey('EvaluationRun', on_delete=models.CASCADE, related_name='results')
    
    # Test Case Information
    test_case_index = models.IntegerField()  # Index in dataset
    test_case_id = models.CharField(max_length=200, blank=True)  # ID if dataset provides
    
    # Input/Output
    input_data = models.JSONField()  # Input sent to model
    expected_output = models.JSONField(null=True, blank=True)  # Expected output (if available)
    actual_output = models.JSONField()  # Model's response
    
    # Metrics
    metrics = models.JSONField(default=dict)  # All calculated metrics
    
    # Performance
    latency_ms = models.FloatField(null=True, blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'evaluation_results'
        indexes = [
            models.Index(fields=['evaluation_run', 'test_case_index']),
            models.Index(fields=['evaluation_run', 'success']),
        ]
        unique_together = [['evaluation_run', 'test_case_index']]
```

---

## 📈 Metrics Models

### ModelMetric

**Purpose:** Store time-series performance metrics

```python
class ModelMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    model = models.ForeignKey('Model', on_delete=models.CASCADE)
    
    # Metric Information
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('accuracy', 'Accuracy'),
            ('latency_p50', 'Latency P50'),
            ('latency_p95', 'Latency P95'),
            ('latency_p99', 'Latency P99'),
            ('cost_per_1k_tokens', 'Cost per 1K Tokens'),
            ('error_rate', 'Error Rate'),
            ('success_rate', 'Success Rate'),
            ('bleu_score', 'BLEU Score'),
            ('rouge_score', 'ROUGE Score'),
            ('custom', 'Custom Metric')
        ]
    )
    
    # Value
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)  # %, ms, USD, etc.
    
    # Context
    benchmark_id = models.UUIDField(null=True, blank=True)  # If metric is benchmark-specific
    evaluation_run_id = models.UUIDField(null=True, blank=True)  # Source evaluation
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'model_metrics'
        indexes = [
            models.Index(fields=['model', 'metric_type', '-timestamp']),
            models.Index(fields=['organization', 'metric_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        ordering = ['-timestamp']
```

### MetricAggregation

**Purpose:** Store pre-aggregated metrics for performance

```python
class MetricAggregation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    model = models.ForeignKey('Model', on_delete=models.CASCADE)
    
    # Aggregation Period
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('hour', 'Hourly'),
            ('day', 'Daily'),
            ('week', 'Weekly'),
            ('month', 'Monthly')
        ]
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Aggregated Metrics
    metrics = models.JSONField(default=dict)  # All metrics aggregated
    
    # Statistics
    sample_count = models.IntegerField(default=0)  # Number of data points
    
    class Meta:
        db_table = 'metric_aggregations'
        indexes = [
            models.Index(fields=['model', 'period_type', '-period_start']),
            models.Index(fields=['organization', 'period_type', '-period_start']),
        ]
        unique_together = [['model', 'period_type', 'period_start']]
```

---

## 🔬 A/B Testing Models

### ABTest

**Purpose:** Define A/B tests comparing models

```python
class ABTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Models to Compare
    models = models.ManyToManyField('Model', related_name='ab_tests')
    
    # Test Dataset
    dataset = models.ForeignKey('EvaluationDataset', on_delete=models.PROTECT)
    
    # Configuration
    test_config = models.JSONField(default=dict)  # Test-specific settings
    significance_level = models.FloatField(default=0.05)  # Statistical significance threshold
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ],
        default='draft'
    )
    
    # Results
    results = models.JSONField(default=dict, blank=True)  # Statistical comparison results
    winner_model_id = models.UUIDField(null=True, blank=True)  # Winner (if significant)
    
    # Execution Info
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ab_tests'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
```

---

## 🧪 Experimentation Models

### Experiment

**Purpose:** Define experiments for testing hypotheses

```python
class Experiment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    hypothesis = models.TextField(blank=True)  # What are we testing?
    objective = models.TextField(blank=True)  # What do we want to achieve?
    
    # Configuration
    experiment_config = models.JSONField(default=dict)  # Models, benchmarks, parameters
    template_id = models.UUIDField(null=True, blank=True)  # If created from template
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    
    # Statistics
    total_runs = models.IntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'experiments'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
```

### ExperimentRun

**Purpose:** Track individual experiment executions

```python
class ExperimentRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    experiment = models.ForeignKey('Experiment', on_delete=models.CASCADE, related_name='runs')
    
    # Run Information
    run_number = models.IntegerField()  # Sequential run number
    name = models.CharField(max_length=200, blank=True)  # Optional run name
    description = models.TextField(blank=True)
    
    # Configuration (may differ from experiment default)
    run_config = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    
    # Results
    results = models.JSONField(default=dict, blank=True)  # Aggregated results
    
    # Execution Info
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Linked Evaluations
    evaluation_runs = models.ManyToManyField('EvaluationRun', blank=True)  # Evaluations in this run
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'experiment_runs'
        indexes = [
            models.Index(fields=['experiment', '-run_number']),
            models.Index(fields=['status', '-created_at']),
        ]
        unique_together = [['experiment', 'run_number']]
```

---

## 🎯 Selection Models

### ModelSelectionLog

**Purpose:** Log model selection decisions for analysis

```python
class ModelSelectionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Selection Context
    requested_capabilities = models.JSONField(default=list)
    constraints = models.JSONField(default=dict)  # Cost, latency, quality constraints
    use_case = models.CharField(max_length=200, blank=True)
    
    # Selection Result
    selected_model = models.ForeignKey('Model', on_delete=models.SET_NULL, null=True)
    selected_model_id = models.UUIDField()  # Store ID even if model deleted
    candidate_models = models.JSONField(default=list)  # All considered models with scores
    
    # Selection Details
    selection_algorithm = models.CharField(max_length=50)  # Which algorithm was used
    selection_score = models.FloatField(null=True, blank=True)
    selection_explanation = models.TextField(blank=True)
    
    # Outcome (if available)
    execution_successful = models.BooleanField(null=True, blank=True)
    actual_performance = models.JSONField(default=dict, blank=True)  # Actual metrics
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'model_selection_logs'
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['selected_model', '-created_at']),
            models.Index(fields=['use_case', '-created_at']),
        ]
```

---

## 📊 Database Indexes

### Critical Indexes

1. **Performance Indexes:**
   - `model_metrics`: `(model, metric_type, timestamp)` for time-series queries
   - `evaluation_runs`: `(model, created_at)` for model history
   - `evaluation_results`: `(evaluation_run, test_case_index)` for result retrieval

2. **Organization Isolation:**
   - All tables: `(organization, ...)` for multi-tenancy

3. **Status Queries:**
   - `evaluation_runs`: `(status, created_at)` for dashboard queries
   - `ab_tests`: `(status, created_at)`

4. **Search Indexes:**
   - `models`: `(name, platform)` for search
   - `benchmark_suites`: `(category, is_standard)`

---

## 🔗 Data Relationships

### Entity Relationship Diagram (Simplified)

```
Organization
    ├── Model (M)
    │       ├── EvaluationRun (M)
    │       ├── ModelMetric (M)
    │       └── ModelSelectionLog (M)
    │
    ├── BenchmarkSuite (M)
    │       └── EvaluationRun (M)
    │
    ├── EvaluationDataset (M)
    │       ├── EvaluationRun (M)
    │       └── BenchmarkSuite (M)
    │
    ├── ABTest (M)
    │       └── Model (M:M)
    │
    └── Experiment (M)
            └── ExperimentRun (M)
                    └── EvaluationRun (M:M)

EvaluationRun
    └── EvaluationResult (M)
```

### Key Relationships

- **One Organization → Many Models**
- **One Model → Many EvaluationRuns**
- **One BenchmarkSuite → Many EvaluationRuns**
- **One EvaluationRun → Many EvaluationResults**
- **One Model → Many ModelMetrics (time-series)**
- **ABTest ↔ Models (Many-to-Many)**
- **Experiment → Many ExperimentRuns**
- **ExperimentRun ↔ EvaluationRuns (Many-to-Many)**

---

**Next Steps:** Review implementation phases document for development sequence.

