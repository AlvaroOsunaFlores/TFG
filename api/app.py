from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .contracts import (
    ConfusionMatrixResponse,
    HealthResponse,
    MessageStatsResponse,
    MessagesResponse,
    RunsResponse,
    RunSummary,
    ThresholdResponse,
    TrainingMetadataResponse,
)
from .settings import Settings, load_settings
from . import services


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    settings = custom_settings or load_settings()

    app = FastAPI(
        title="TFG Cybersecurity API",
        version="1.0.0",
        description="API para trazabilidad, metricas y resultados del TFG Telegram + IA + Mongo.",
    )
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        reports_ok, reports_error = services.check_reports_available(settings.reports_dir)
        mongo_ok, mongo_error = services.check_mongo_connection(settings)

        details: dict[str, str] = {}
        if reports_error:
            details["reports"] = reports_error
        if mongo_error:
            details["mongo"] = mongo_error

        status = "ok" if reports_ok and mongo_ok else "degraded"
        return HealthResponse(
            status=status,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            mongo_ok=mongo_ok,
            reports_ok=reports_ok,
            details=details,
        )

    @app.get("/api/v1/runs", response_model=RunsResponse)
    def list_runs() -> RunsResponse:
        payloads = services.load_metrics_payloads(settings.reports_dir)
        runs = [RunSummary(**services.run_summary_from_payload(payload)) for payload in payloads]
        return RunsResponse(runs=runs)

    def _resolve_run_or_404(run_id: str) -> dict:
        payloads = services.load_metrics_payloads(settings.reports_dir)
        payload = services.get_run_payload_by_id(payloads, run_id)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"run_id '{run_id}' not found")
        return payload

    @app.get("/api/v1/runs/{run_id}/summary", response_model=RunSummary)
    def run_summary(run_id: str) -> RunSummary:
        payload = _resolve_run_or_404(run_id)
        return RunSummary(**services.run_summary_from_payload(payload))

    @app.get("/api/v1/runs/{run_id}/thresholds", response_model=ThresholdResponse)
    def run_thresholds(run_id: str) -> ThresholdResponse:
        _resolve_run_or_404(run_id)
        points = services.load_threshold_points(settings.reports_dir)
        return ThresholdResponse(run_id=run_id, points=points)

    @app.get("/api/v1/runs/{run_id}/confusion-matrix", response_model=ConfusionMatrixResponse)
    def run_confusion_matrix(run_id: str) -> ConfusionMatrixResponse:
        _resolve_run_or_404(run_id)
        payload = services.load_confusion_payload(settings.reports_dir)
        return ConfusionMatrixResponse(run_id=run_id, **payload)

    @app.get("/api/v1/messages", response_model=MessagesResponse)
    def messages(
        run_id: str | None = Query(default=None),
        pred: int | None = Query(default=None, ge=0, le=1),
        score_min: float | None = Query(default=None, ge=0.0, le=1.0),
        date_from: datetime | None = Query(default=None),
        date_to: datetime | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
    ) -> MessagesResponse:
        payload = services.fetch_messages(
            settings,
            run_id=run_id,
            pred=pred,
            score_min=score_min,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return MessagesResponse(**payload)

    @app.get("/api/v1/messages/stats", response_model=MessageStatsResponse)
    def message_stats(
        run_id: str | None = Query(default=None),
        date_from: datetime | None = Query(default=None),
        date_to: datetime | None = Query(default=None),
        limit: int = Query(default=500, ge=1, le=5000),
    ) -> MessageStatsResponse:
        payload = services.fetch_message_stats(
            settings,
            run_id=run_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )
        return MessageStatsResponse(**payload)

    @app.get("/api/v1/training/metadata", response_model=TrainingMetadataResponse)
    def training_metadata() -> TrainingMetadataResponse:
        metadata = services.load_training_metadata(settings.training_metadata_path)
        return TrainingMetadataResponse(metadata=metadata)

    return app


app = create_app()
