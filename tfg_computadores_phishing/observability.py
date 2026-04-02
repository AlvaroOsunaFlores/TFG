from __future__ import annotations

from dataclasses import asdict, dataclass
from time import monotonic

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
import psutil
import torch


STAGE_BUCKETS = (1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)

MESSAGES_PUBLISHED_TOTAL = Counter(
    "tfg_messages_published_total",
    "Mensajes enviados a la cola RabbitMQ.",
    ["source"],
)
MESSAGES_PROCESSED_TOTAL = Counter(
    "tfg_messages_processed_total",
    "Mensajes procesados por el worker.",
    ["result"],
)
MESSAGE_PREDICTIONS_TOTAL = Counter(
    "tfg_message_predictions_total",
    "Distribucion de predicciones del pipeline.",
    ["pred"],
)
PIPELINE_STAGE_LATENCY_MS = Histogram(
    "tfg_pipeline_stage_latency_ms",
    "Latencia por etapa del pipeline en milisegundos.",
    ["stage"],
    buckets=STAGE_BUCKETS,
)
QUEUE_DEPTH_MESSAGES = Gauge(
    "tfg_queue_depth_messages",
    "Profundidad aproximada de la cola RabbitMQ.",
)
PROCESS_CPU_PERCENT = Gauge(
    "tfg_process_cpu_percent",
    "Uso de CPU del proceso actual.",
)
PROCESS_RSS_BYTES = Gauge(
    "tfg_process_rss_bytes",
    "Memoria RSS del proceso actual.",
)
PROCESS_VMS_BYTES = Gauge(
    "tfg_process_vms_bytes",
    "Memoria VMS del proceso actual.",
)
PROCESS_GPU_BYTES = Gauge(
    "tfg_process_gpu_bytes",
    "Memoria GPU reservada por el proceso actual.",
)
BENCHMARK_THROUGHPUT_MPS = Gauge(
    "tfg_benchmark_throughput_mps",
    "Throughput medido en el benchmark controlado.",
    ["scenario"],
)
BENCHMARK_LATENCY_P95_MS = Gauge(
    "tfg_benchmark_latency_p95_ms",
    "Latencia p95 del benchmark controlado.",
    ["scenario"],
)
BENCHMARK_ERROR_RATE = Gauge(
    "tfg_benchmark_error_rate",
    "Tasa de errores del benchmark controlado.",
    ["scenario"],
)
API_REQUESTS_TOTAL = Counter(
    "tfg_api_requests_total",
    "Peticiones recibidas por la API.",
    ["path", "method", "status"],
)
API_REQUEST_LATENCY_MS = Histogram(
    "tfg_api_request_latency_ms",
    "Latencia de peticiones de la API.",
    ["path", "method"],
    buckets=STAGE_BUCKETS,
)


@dataclass(frozen=True)
class ResourceSnapshot:
    cpu_percent: float
    rss_bytes: int
    vms_bytes: int
    gpu_memory_bytes: int | None

    def to_document_fields(self) -> dict[str, float | int | None]:
        return {
            "cpu_percent": round(self.cpu_percent, 3),
            "rss_bytes": self.rss_bytes,
            "vms_bytes": self.vms_bytes,
            "gpu_memory_bytes": self.gpu_memory_bytes,
        }


class ProcessResourceMonitor:
    def __init__(self, snapshot_interval_seconds: float = 5.0) -> None:
        self.snapshot_interval_seconds = snapshot_interval_seconds
        self._process = psutil.Process()
        self._process.cpu_percent(interval=None)
        self._last_snapshot_at = 0.0
        self._last_snapshot: ResourceSnapshot | None = None

    def snapshot(self, *, force: bool = False) -> ResourceSnapshot:
        now = monotonic()
        if not force and self._last_snapshot is not None and now - self._last_snapshot_at < self.snapshot_interval_seconds:
            return self._last_snapshot

        mem = self._process.memory_info()
        gpu_memory_bytes = int(torch.cuda.memory_allocated()) if torch.cuda.is_available() else None
        snapshot = ResourceSnapshot(
            cpu_percent=float(self._process.cpu_percent(interval=None)),
            rss_bytes=int(mem.rss),
            vms_bytes=int(mem.vms),
            gpu_memory_bytes=gpu_memory_bytes,
        )

        PROCESS_CPU_PERCENT.set(snapshot.cpu_percent)
        PROCESS_RSS_BYTES.set(snapshot.rss_bytes)
        PROCESS_VMS_BYTES.set(snapshot.vms_bytes)
        PROCESS_GPU_BYTES.set(float(snapshot.gpu_memory_bytes or 0))

        self._last_snapshot_at = now
        self._last_snapshot = snapshot
        return snapshot


def record_publish(*, source: str, queue_depth: int | None) -> None:
    MESSAGES_PUBLISHED_TOTAL.labels(source=source).inc()
    if queue_depth is not None:
        QUEUE_DEPTH_MESSAGES.set(queue_depth)


def record_queue_depth(queue_depth: int | None) -> None:
    if queue_depth is not None:
        QUEUE_DEPTH_MESSAGES.set(queue_depth)


def record_worker_result(document: dict[str, object]) -> None:
    MESSAGES_PROCESSED_TOTAL.labels(result="ok" if document.get("ok") else "error").inc()
    pred = document.get("pred")
    if pred in {0, 1}:
        MESSAGE_PREDICTIONS_TOTAL.labels(pred=str(pred)).inc()

    for field_name, stage in [
        ("preprocess_latency_ms", "preprocess"),
        ("inference_latency_ms", "inference"),
        ("db_write_latency_ms", "db_write"),
        ("end_to_end_latency_ms", "end_to_end"),
        ("queue_wait_latency_ms", "queue_wait"),
    ]:
        value = document.get(field_name)
        if isinstance(value, (int, float)):
            PIPELINE_STAGE_LATENCY_MS.labels(stage=stage).observe(float(value))

    queue_depth = document.get("queue_depth")
    if isinstance(queue_depth, (int, float)):
        QUEUE_DEPTH_MESSAGES.set(float(queue_depth))

    for field_name, gauge in [
        ("cpu_percent", PROCESS_CPU_PERCENT),
        ("rss_bytes", PROCESS_RSS_BYTES),
        ("vms_bytes", PROCESS_VMS_BYTES),
        ("gpu_memory_bytes", PROCESS_GPU_BYTES),
    ]:
        value = document.get(field_name)
        if isinstance(value, (int, float)):
            gauge.set(float(value))


def record_benchmark_summary(scenario: str, payload: dict[str, object]) -> None:
    throughput = payload.get("throughput_mps")
    latency_p95 = payload.get("latency_p95_ms")
    error_rate = payload.get("error_rate")
    if isinstance(throughput, (int, float)):
        BENCHMARK_THROUGHPUT_MPS.labels(scenario=scenario).set(float(throughput))
    if isinstance(latency_p95, (int, float)):
        BENCHMARK_LATENCY_P95_MS.labels(scenario=scenario).set(float(latency_p95))
    if isinstance(error_rate, (int, float)):
        BENCHMARK_ERROR_RATE.labels(scenario=scenario).set(float(error_rate))


def observe_api_request(path: str, method: str, status: int, duration_ms: float) -> None:
    API_REQUESTS_TOTAL.labels(path=path, method=method, status=str(status)).inc()
    API_REQUEST_LATENCY_MS.labels(path=path, method=method).observe(duration_ms)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def snapshot_fields_dict(snapshot: ResourceSnapshot) -> dict[str, float | int | None]:
    return asdict(snapshot)
