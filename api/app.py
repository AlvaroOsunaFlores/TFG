from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import services
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


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    settings = custom_settings or load_settings()

    def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if x_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="missing or invalid api key")

    protected = [Depends(verify_api_key)]

    app = FastAPI(
        title="TFG Cybersecurity API",
        version="1.1.0",
        description="API para trazabilidad, metricas y resultados del TFG Telegram + IA + Mongo.",
    )
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health", response_model=HealthResponse, dependencies=protected)
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

    @app.get("/api/v1/runs", response_model=RunsResponse, dependencies=protected)
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

    @app.get("/api/v1/runs/{run_id}/summary", response_model=RunSummary, dependencies=protected)
    def run_summary(run_id: str) -> RunSummary:
        payload = _resolve_run_or_404(run_id)
        return RunSummary(**services.run_summary_from_payload(payload))

    @app.get("/api/v1/runs/{run_id}/thresholds", response_model=ThresholdResponse, dependencies=protected)
    def run_thresholds(run_id: str) -> ThresholdResponse:
        payload = _resolve_run_or_404(run_id)
        points = services.load_threshold_points(Path(str(payload["_artifacts_dir"])))
        return ThresholdResponse(run_id=run_id, points=points)

    @app.get("/api/v1/runs/{run_id}/confusion-matrix", response_model=ConfusionMatrixResponse, dependencies=protected)
    def run_confusion_matrix(run_id: str) -> ConfusionMatrixResponse:
        payload = _resolve_run_or_404(run_id)
        matrix_payload = services.load_confusion_payload(Path(str(payload["_artifacts_dir"])))
        return ConfusionMatrixResponse(run_id=run_id, **matrix_payload)

    @app.get("/api/v1/messages", response_model=MessagesResponse, dependencies=protected)
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

    @app.get("/api/v1/messages/stats", response_model=MessageStatsResponse, dependencies=protected)
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

    @app.get("/api/v1/training/metadata", response_model=TrainingMetadataResponse, dependencies=protected)
    def training_metadata() -> TrainingMetadataResponse:
        metadata = services.load_training_metadata(settings.training_metadata_path)
        return TrainingMetadataResponse(metadata=metadata)

    return app

app = create_app()
