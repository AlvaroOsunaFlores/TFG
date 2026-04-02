from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    timestamp_utc: str
    mongo_ok: bool
    reports_ok: bool
    details: dict[str, str] = Field(default_factory=dict)


class RunSummary(BaseModel):
    run_id: str
    timestamp: str | None = None
    hf_model: str | None = None
    model_source: str | None = None
    threshold: float | None = None
    num_samples: int | None = None
    label_distribution: dict[str, int] = Field(default_factory=dict)
    metrics: dict[str, float | None] = Field(default_factory=dict)


class RunsResponse(BaseModel):
    runs: list[RunSummary]


class ThresholdPoint(BaseModel):
    threshold: float
    precision_pos: float
    recall_pos: float
    f1_pos: float
    accuracy: float


class ThresholdResponse(BaseModel):
    run_id: str
    points: list[ThresholdPoint]


class ConfusionMatrixResponse(BaseModel):
    run_id: str
    labels: list[int]
    matrix: list[list[int]]
    normalized: list[list[float]]


class MessageRecord(BaseModel):
    created_at_utc: str | None = None
    persisted_at_utc: str | None = None
    source_received_at_utc: str | None = None
    queued_at_utc: str | None = None
    run_id: str | None = None
    source: str | None = None
    channel: str | None = None
    chat_hash: str | None = None
    user_hash: str | None = None
    message_id: int | None = None
    msg_sha256: str | None = None
    pred: int | None = None
    score_1: float | None = None
    latency_ms: float | None = None
    preprocess_latency_ms: float | None = None
    inference_latency_ms: float | None = None
    db_write_latency_ms: float | None = None
    queue_wait_latency_ms: float | None = None
    end_to_end_latency_ms: float | None = None
    queue_depth: int | None = None
    cpu_percent: float | None = None
    rss_bytes: int | None = None
    vms_bytes: int | None = None
    gpu_memory_bytes: int | None = None
    ok: bool | None = None
    error: str | None = None


class MessagesResponse(BaseModel):
    source: str
    total: int
    limit: int
    offset: int
    items: list[MessageRecord]
    warning: str | None = None


class MessageStatsResponse(BaseModel):
    source: str
    total: int
    benign_count: int
    threat_count: int
    error_count: int
    error_rate: float
    latency_avg_ms: float | None = None
    latency_p95_ms: float | None = None
    preprocess_latency_avg_ms: float | None = None
    preprocess_latency_p95_ms: float | None = None
    inference_latency_avg_ms: float | None = None
    inference_latency_p95_ms: float | None = None
    db_write_latency_avg_ms: float | None = None
    db_write_latency_p95_ms: float | None = None
    end_to_end_latency_avg_ms: float | None = None
    end_to_end_latency_p95_ms: float | None = None
    queue_wait_latency_avg_ms: float | None = None
    queue_wait_latency_p95_ms: float | None = None
    queue_depth_avg: float | None = None
    queue_depth_p95: float | None = None
    score_avg: float | None = None
    score_p50: float | None = None
    score_p95: float | None = None
    cpu_avg_percent: float | None = None
    rss_avg_bytes: float | None = None
    vms_avg_bytes: float | None = None
    gpu_memory_avg_bytes: float | None = None
    throughput_messages_per_second: float | None = None
    warning: str | None = None


class BenchmarkScenario(BaseModel):
    scenario: str
    target_rate_mps: int
    planned_messages: int
    processed_messages: int
    throughput_mps: float | None = None
    latency_avg_ms: float | None = None
    latency_p95_ms: float | None = None
    cpu_avg_percent: float | None = None
    ram_avg_bytes: float | None = None
    vms_avg_bytes: float | None = None
    error_rate: float | None = None


class BenchmarkRun(BaseModel):
    benchmark_id: str
    created_at_utc: str | None = None
    duration_seconds_per_scenario: int | None = None
    write_mongo: bool = False
    artifacts_dir: str | None = None
    scenarios: list[BenchmarkScenario] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)


class BenchmarksResponse(BaseModel):
    benchmarks: list[BenchmarkRun]


class TrainingMetadataResponse(BaseModel):
    metadata: dict[str, Any]
