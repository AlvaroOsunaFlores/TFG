import { useEffect, useMemo, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";

import {
  getHealth,
  getMessages,
  getRunConfusion,
  getRuns,
  getRunSummary,
  getRunThresholds,
  getTrainingMetadata,
} from "./api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);

const TABS = ["Resumen", "Rendimiento", "Confusion", "Mensajes", "Trazabilidad"];

function getInitialTab() {
  try {
    const value = new URLSearchParams(window.location.search).get("tab");
    if (value && TABS.includes(value)) {
      return value;
    }
  } catch (_err) {
    return "Resumen";
  }
  return "Resumen";
}

function MetricCard({ label, value }) {
  return (
    <article className="metric-card">
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value}</p>
    </article>
  );
}

function prettyPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  return `${(Number(value) * 100).toFixed(2)}%`;
}

export default function App() {
  const [activeTab, setActiveTab] = useState(getInitialTab);
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState("");
  const [summary, setSummary] = useState(null);
  const [thresholds, setThresholds] = useState([]);
  const [confusion, setConfusion] = useState(null);
  const [messages, setMessages] = useState({ items: [], warning: null, source: "loading" });
  const [trainingMetadata, setTrainingMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [messageFilters, setMessageFilters] = useState({ pred: "", scoreMin: "" });

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      try {
        setLoading(true);
        const [healthResponse, runsResponse, trainingResponse] = await Promise.all([
          getHealth(),
          getRuns(),
          getTrainingMetadata(),
        ]);
        if (cancelled) return;

        const runList = runsResponse.runs || [];
        setHealth(healthResponse);
        setRuns(runList);
        setTrainingMetadata(trainingResponse.metadata);
        setSelectedRun(runList[0]?.run_id || "");
      } catch (e) {
        if (!cancelled) {
          setError(String(e));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadRunData() {
      if (!selectedRun) return;
      try {
        const [summaryResponse, thresholdResponse, confusionResponse] = await Promise.all([
          getRunSummary(selectedRun),
          getRunThresholds(selectedRun),
          getRunConfusion(selectedRun),
        ]);
        if (cancelled) return;
        setSummary(summaryResponse);
        setThresholds(thresholdResponse.points || []);
        setConfusion(confusionResponse);
      } catch (e) {
        if (!cancelled) setError(String(e));
      }
    }
    loadRunData();
    return () => {
      cancelled = true;
    };
  }, [selectedRun]);

  useEffect(() => {
    let cancelled = false;
    async function loadMessages() {
      if (!selectedRun) return;
      try {
        const response = await getMessages({
          runId: selectedRun,
          limit: 100,
          pred: messageFilters.pred,
          scoreMin: messageFilters.scoreMin,
        });
        if (!cancelled) setMessages(response);
      } catch (e) {
        if (!cancelled) setError(String(e));
      }
    }
    loadMessages();
    return () => {
      cancelled = true;
    };
  }, [selectedRun, messageFilters.pred, messageFilters.scoreMin]);

  const thresholdChartData = useMemo(
    () => ({
      labels: thresholds.map((row) => row.threshold),
      datasets: [
        {
          label: "Recall",
          data: thresholds.map((row) => row.recall_pos),
          borderColor: "#ef4444",
          backgroundColor: "rgba(239,68,68,0.16)",
          tension: 0.2,
        },
        {
          label: "Precision",
          data: thresholds.map((row) => row.precision_pos),
          borderColor: "#0f766e",
          backgroundColor: "rgba(15,118,110,0.16)",
          tension: 0.2,
        },
        {
          label: "F1",
          data: thresholds.map((row) => row.f1_pos),
          borderColor: "#0369a1",
          backgroundColor: "rgba(3,105,161,0.16)",
          tension: 0.2,
        },
      ],
    }),
    [thresholds]
  );

  const confusionChartData = useMemo(() => {
    if (!confusion) return null;
    const matrix = confusion.matrix;
    return {
      labels: ["Pred 0", "Pred 1"],
      datasets: [
        {
          label: "Real 0",
          data: matrix[0],
          backgroundColor: ["#99f6e4", "#2dd4bf"],
        },
        {
          label: "Real 1",
          data: matrix[1],
          backgroundColor: ["#fecaca", "#ef4444"],
        },
      ],
    };
  }, [confusion]);

  const predDistributionData = useMemo(() => {
    if (!messages?.items?.length) return null;
    const positives = messages.items.filter((row) => row.pred === 1).length;
    const negatives = messages.items.filter((row) => row.pred === 0).length;
    return {
      labels: ["Benigno", "Amenaza"],
      datasets: [
        {
          data: [negatives, positives],
          backgroundColor: ["#0ea5e9", "#ef4444"],
        },
      ],
    };
  }, [messages]);

  if (loading) {
    return <main className="page">Cargando dashboard...</main>;
  }

  if (error) {
    return (
      <main className="page">
        <h1>Error</h1>
        <p>{error}</p>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="hero">
        <p className="hero-kicker">TFG Ciberseguridad | Telegram + IA + MongoDB</p>
        <h1>Dashboard Operativo de Deteccion</h1>
        <p>
          Visualizacion de ejecuciones, ajuste de umbral orientado a recall, trazabilidad de mensajes y
          resultados de validacion.
        </p>
      </section>

      <section className="toolbar">
        <label>
          Run ID
          <select value={selectedRun} onChange={(e) => setSelectedRun(e.target.value)}>
            {runs.map((run) => (
              <option key={run.run_id} value={run.run_id}>
                {run.run_id}
              </option>
            ))}
          </select>
        </label>
        <div className="health">
          <span className={`status ${health?.status || "unknown"}`}>{health?.status || "unknown"}</span>
          <span>Reports: {String(health?.reports_ok)}</span>
          <span>Mongo: {String(health?.mongo_ok)}</span>
        </div>
      </section>

      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab}
            className={tab === activeTab ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {activeTab === "Resumen" && summary && (
        <section className="panel">
          <h2>KPIs Globales</h2>
          <div className="metrics-grid">
            <MetricCard label="Accuracy" value={prettyPercent(summary.metrics?.accuracy)} />
            <MetricCard label="Precision (class 1)" value={prettyPercent(summary.metrics?.precision_pos)} />
            <MetricCard label="Recall (class 1)" value={prettyPercent(summary.metrics?.recall_pos)} />
            <MetricCard label="F1 (class 1)" value={prettyPercent(summary.metrics?.f1_pos)} />
            <MetricCard label="ROC AUC" value={summary.metrics?.roc_auc?.toFixed?.(4) || "N/A"} />
            <MetricCard label="Average Precision" value={summary.metrics?.average_precision?.toFixed?.(4) || "N/A"} />
            <MetricCard label="Threshold" value={summary.threshold} />
            <MetricCard label="Samples" value={summary.num_samples} />
          </div>
          {predDistributionData && (
            <div className="chart-card">
              <h3>Distribucion de predicciones (muestra de mensajes)</h3>
              <Doughnut data={predDistributionData} />
            </div>
          )}
        </section>
      )}

      {activeTab === "Rendimiento" && (
        <section className="panel">
          <h2>Curva por Umbral</h2>
          <div className="chart-card">
            <Line data={thresholdChartData} />
          </div>
        </section>
      )}

      {activeTab === "Confusion" && (
        <section className="panel">
          <h2>Matriz de Confusion</h2>
          {confusionChartData && (
            <div className="chart-card">
              <Bar data={confusionChartData} />
            </div>
          )}
          {confusion && (
            <table className="table">
              <thead>
                <tr>
                  <th>Real/Pred</th>
                  <th>Pred 0</th>
                  <th>Pred 1</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Real 0</td>
                  <td>{confusion.matrix[0][0]}</td>
                  <td>{confusion.matrix[0][1]}</td>
                </tr>
                <tr>
                  <td>Real 1</td>
                  <td>{confusion.matrix[1][0]}</td>
                  <td>{confusion.matrix[1][1]}</td>
                </tr>
              </tbody>
            </table>
          )}
        </section>
      )}

      {activeTab === "Mensajes" && (
        <section className="panel">
          <h2>Mensajes y Trazabilidad</h2>
          <div className="filters">
            <label>
              Pred
              <select
                value={messageFilters.pred}
                onChange={(e) => setMessageFilters((prev) => ({ ...prev, pred: e.target.value }))}
              >
                <option value="">Todos</option>
                <option value="0">Benigno</option>
                <option value="1">Amenaza</option>
              </select>
            </label>
            <label>
              Score minimo
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={messageFilters.scoreMin}
                onChange={(e) => setMessageFilters((prev) => ({ ...prev, scoreMin: e.target.value }))}
              />
            </label>
          </div>
          {messages.warning && <p className="warning">Aviso de fuente: {messages.warning}</p>}
          <table className="table">
            <thead>
              <tr>
                <th>Fecha UTC</th>
                <th>Pred</th>
                <th>Score_1</th>
                <th>Latencia (ms)</th>
                <th>Hash</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {messages.items.map((msg) => (
                <tr key={`${msg.run_id}-${msg.message_id}-${msg.msg_sha256}`}>
                  <td>{msg.created_at_utc || "-"}</td>
                  <td>{msg.pred}</td>
                  <td>{msg.score_1?.toFixed?.(4) ?? "-"}</td>
                  <td>{msg.latency_ms ?? "-"}</td>
                  <td className="mono">{msg.msg_sha256 || "-"}</td>
                  <td>{String(msg.ok)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {activeTab === "Trazabilidad" && (
        <section className="panel">
          <h2>Detalle de Ejecucion y Entrenamiento</h2>
          <div className="trace-grid">
            <article>
              <h3>Resumen de run</h3>
              <pre>{JSON.stringify(summary, null, 2)}</pre>
            </article>
            <article>
              <h3>Metadata de entrenamiento</h3>
              <pre>{JSON.stringify(trainingMetadata, null, 2)}</pre>
            </article>
          </div>
        </section>
      )}
    </main>
  );
}
