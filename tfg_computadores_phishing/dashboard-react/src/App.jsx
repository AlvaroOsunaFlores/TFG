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
  getBenchmarks,
  getHealth,
  getMessages,
  getMessageStats,
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

function prettyNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  return Number(value).toFixed(digits);
}

function prettyBytes(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  const units = ["B", "KB", "MB", "GB"];
  let current = Number(value);
  let index = 0;
  while (current >= 1024 && index < units.length - 1) {
    current /= 1024;
    index += 1;
  }
  return `${current.toFixed(2)} ${units[index]}`;
}

export default function App() {
  const [activeTab, setActiveTab] = useState(getInitialTab);
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [selectedRun, setSelectedRun] = useState("");
  const [summary, setSummary] = useState(null);
  const [messageStats, setMessageStats] = useState(null);
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
        const [healthResponse, runsResponse, trainingResponse, benchmarkResponse] = await Promise.all([
          getHealth(),
          getRuns(),
          getTrainingMetadata(),
          getBenchmarks(),
        ]);
        if (cancelled) return;

        const runList = runsResponse.runs || [];
        setHealth(healthResponse);
        setRuns(runList);
        setBenchmarks(benchmarkResponse.benchmarks || []);
        setTrainingMetadata(trainingResponse.metadata);
        setSelectedRun(runList[0]?.run_id || "");
      } catch (e) {
        if (!cancelled) setError(String(e));
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
        const [summaryResponse, thresholdResponse, confusionResponse, statsResponse] = await Promise.all([
          getRunSummary(selectedRun),
          getRunThresholds(selectedRun),
          getRunConfusion(selectedRun),
          getMessageStats({ runId: selectedRun, limit: 500 }),
        ]);
        if (cancelled) return;
        setSummary(summaryResponse);
        setThresholds(thresholdResponse.points || []);
        setConfusion(confusionResponse);
        setMessageStats(statsResponse);
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

  const latestBenchmark = benchmarks[0] || null;

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
    return {
      labels: ["Pred 0", "Pred 1"],
      datasets: [
        {
          label: "Real 0",
          data: confusion.matrix[0],
          backgroundColor: ["#99f6e4", "#2dd4bf"],
        },
        {
          label: "Real 1",
          data: confusion.matrix[1],
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
        <p className="hero-kicker">TFG Computadores | Telegram + RabbitMQ + Prometheus</p>
        <h1>Pipeline Operativo de Deteccion de Phishing</h1>
        <p>
          Vista integrada de ejecuciones offline, latencias por etapa, observabilidad del worker y benchmark
          controlado del pipeline.
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
          <span>Benchmarks: {benchmarks.length}</span>
        </div>
      </section>

      <nav className="tabs">
        {TABS.map((tab) => (
          <button key={tab} className={tab === activeTab ? "tab active" : "tab"} onClick={() => setActiveTab(tab)}>
            {tab}
          </button>
        ))}
      </nav>

      {activeTab === "Resumen" && summary && (
        <section className="panel">
          <h2>KPIs Globales</h2>
          <div className="metrics-grid">
            <MetricCard label="Accuracy offline" value={prettyPercent(summary.metrics?.accuracy)} />
            <MetricCard label="Precision (class 1)" value={prettyPercent(summary.metrics?.precision_pos)} />
            <MetricCard label="Recall (class 1)" value={prettyPercent(summary.metrics?.recall_pos)} />
            <MetricCard label="F1 (class 1)" value={prettyPercent(summary.metrics?.f1_pos)} />
            <MetricCard label="Threshold" value={summary.threshold ?? "N/A"} />
            <MetricCard label="Samples offline" value={summary.num_samples ?? "N/A"} />
            <MetricCard label="E2E avg (ms)" value={prettyNumber(messageStats?.end_to_end_latency_avg_ms)} />
            <MetricCard label="E2E p95 (ms)" value={prettyNumber(messageStats?.end_to_end_latency_p95_ms)} />
            <MetricCard label="Throughput msg/s" value={prettyNumber(messageStats?.throughput_messages_per_second)} />
            <MetricCard label="CPU medio" value={prettyNumber(messageStats?.cpu_avg_percent)} />
            <MetricCard label="RAM media" value={prettyBytes(messageStats?.rss_avg_bytes)} />
            <MetricCard label="Cola media" value={prettyNumber(messageStats?.queue_depth_avg)} />
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
          <h2>Rendimiento Operativo</h2>
          <div className="chart-card">
            <h3>Curva por umbral</h3>
            <Line data={thresholdChartData} />
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Metrica</th>
                <th>Media</th>
                <th>P95</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Preprocess latency (ms)</td>
                <td>{prettyNumber(messageStats?.preprocess_latency_avg_ms)}</td>
                <td>{prettyNumber(messageStats?.preprocess_latency_p95_ms)}</td>
              </tr>
              <tr>
                <td>Inference latency (ms)</td>
                <td>{prettyNumber(messageStats?.inference_latency_avg_ms)}</td>
                <td>{prettyNumber(messageStats?.inference_latency_p95_ms)}</td>
              </tr>
              <tr>
                <td>DB write latency (ms)</td>
                <td>{prettyNumber(messageStats?.db_write_latency_avg_ms)}</td>
                <td>{prettyNumber(messageStats?.db_write_latency_p95_ms)}</td>
              </tr>
              <tr>
                <td>Queue wait latency (ms)</td>
                <td>{prettyNumber(messageStats?.queue_wait_latency_avg_ms)}</td>
                <td>{prettyNumber(messageStats?.queue_wait_latency_p95_ms)}</td>
              </tr>
            </tbody>
          </table>
          {latestBenchmark && (
            <>
              <h3>Ultimo benchmark controlado</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>Escenario</th>
                    <th>Target msg/s</th>
                    <th>Throughput</th>
                    <th>Latencia avg</th>
                    <th>Latencia p95</th>
                    <th>CPU medio</th>
                    <th>RAM media</th>
                    <th>Error rate</th>
                  </tr>
                </thead>
                <tbody>
                  {latestBenchmark.scenarios.map((scenario) => (
                    <tr key={scenario.scenario}>
                      <td>{scenario.scenario}</td>
                      <td>{scenario.target_rate_mps}</td>
                      <td>{prettyNumber(scenario.throughput_mps)}</td>
                      <td>{prettyNumber(scenario.latency_avg_ms)}</td>
                      <td>{prettyNumber(scenario.latency_p95_ms)}</td>
                      <td>{prettyNumber(scenario.cpu_avg_percent)}</td>
                      <td>{prettyBytes(scenario.ram_avg_bytes)}</td>
                      <td>{prettyPercent(scenario.error_rate)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
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
                <th>Score</th>
                <th>Preprocess</th>
                <th>Inference</th>
                <th>DB</th>
                <th>E2E</th>
                <th>CPU</th>
                <th>Queue</th>
              </tr>
            </thead>
            <tbody>
              {messages.items.map((msg) => (
                <tr key={`${msg.run_id}-${msg.message_id}-${msg.msg_sha256}`}>
                  <td>{msg.created_at_utc || "-"}</td>
                  <td>{msg.pred ?? "-"}</td>
                  <td>{msg.score_1?.toFixed?.(4) ?? "-"}</td>
                  <td>{msg.preprocess_latency_ms ?? "-"}</td>
                  <td>{msg.inference_latency_ms ?? "-"}</td>
                  <td>{msg.db_write_latency_ms ?? "-"}</td>
                  <td>{msg.end_to_end_latency_ms ?? "-"}</td>
                  <td>{msg.cpu_percent ?? "-"}</td>
                  <td>{msg.queue_depth ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {activeTab === "Trazabilidad" && (
        <section className="panel">
          <h2>Detalle Tecnico</h2>
          <div className="trace-grid">
            <article>
              <h3>Resumen de run</h3>
              <pre>{JSON.stringify(summary, null, 2)}</pre>
            </article>
            <article>
              <h3>Stats operativas</h3>
              <pre>{JSON.stringify(messageStats, null, 2)}</pre>
            </article>
            <article>
              <h3>Ultimo benchmark</h3>
              <pre>{JSON.stringify(latestBenchmark, null, 2)}</pre>
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
