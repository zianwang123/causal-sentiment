"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { API_URL as API } from "@/lib/config";

interface BacktestResult {
  node_id: string;
  correlation: number | null;
  hit_rate: number | null;
  ic: number | null;
  n_observations: number;
  avg_return_bullish: number | null;
  avg_return_bearish: number | null;
  scatter_points: number[][];
}

export default function BacktestChart({ nodeId }: { nodeId: string }) {
  const [data, setData] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const fetchBacktest = useCallback(() => {
    setLoading(true);
    fetch(`${API}/api/graph/backtest/${nodeId}`)
      .then((r) => r.json())
      .then((d: BacktestResult) => setData(d))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [nodeId]);

  useEffect(() => {
    fetchBacktest();
  }, [fetchBacktest]);

  // Draw scatter plot on canvas
  useEffect(() => {
    if (!data || !canvasRef.current || data.scatter_points.length === 0) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;
    const pad = 30;

    ctx.clearRect(0, 0, w, h);

    const points = data.scatter_points;
    const xs = points.map((p) => p[0]);
    const ys = points.map((p) => p[1]);
    const xMin = Math.min(...xs, -0.5);
    const xMax = Math.max(...xs, 0.5);
    const yMin = Math.min(...ys, -2);
    const yMax = Math.max(...ys, 2);
    const xRange = xMax - xMin || 1;
    const yRange = yMax - yMin || 1;

    const toX = (v: number) => pad + ((v - xMin) / xRange) * (w - 2 * pad);
    const toY = (v: number) => h - pad - ((v - yMin) / yRange) * (h - 2 * pad);

    // Grid lines
    ctx.strokeStyle = "#374151";
    ctx.lineWidth = 0.5;
    // Zero lines
    if (xMin < 0 && xMax > 0) {
      ctx.beginPath();
      ctx.moveTo(toX(0), pad);
      ctx.lineTo(toX(0), h - pad);
      ctx.stroke();
    }
    if (yMin < 0 && yMax > 0) {
      ctx.beginPath();
      ctx.moveTo(pad, toY(0));
      ctx.lineTo(w - pad, toY(0));
      ctx.stroke();
    }

    // Axis labels
    ctx.fillStyle = "#6b7280";
    ctx.font = "9px monospace";
    ctx.textAlign = "center";
    ctx.fillText("Sentiment", w / 2, h - 4);
    ctx.save();
    ctx.translate(8, h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("Return %", 0, 0);
    ctx.restore();

    // Points
    for (const [sx, ry] of points) {
      const px = toX(sx);
      const py = toY(ry);
      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      // Color by quadrant
      if (sx > 0 && ry > 0) ctx.fillStyle = "#22c55e"; // green: correct bullish
      else if (sx < 0 && ry < 0) ctx.fillStyle = "#22c55e"; // green: correct bearish
      else ctx.fillStyle = "#ef4444"; // red: wrong direction
      ctx.globalAlpha = 0.7;
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    // Trend line (simple linear regression)
    if (points.length >= 5) {
      const n = points.length;
      const sumX = xs.reduce((a, b) => a + b, 0);
      const sumY = ys.reduce((a, b) => a + b, 0);
      const sumXY = points.reduce((a, p) => a + p[0] * p[1], 0);
      const sumX2 = xs.reduce((a, x) => a + x * x, 0);
      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
      const intercept = (sumY - slope * sumX) / n;

      ctx.strokeStyle = "#60a5fa";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(toX(xMin), toY(slope * xMin + intercept));
      ctx.lineTo(toX(xMax), toY(slope * xMax + intercept));
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [data]);

  if (loading) {
    return (
      <div className="text-xs text-gray-500 py-2">Loading backtest...</div>
    );
  }

  if (!data || data.n_observations < 3) {
    return (
      <div className="text-xs text-gray-500 py-2">
        Insufficient data for backtest ({data?.n_observations ?? 0} obs)
      </div>
    );
  }

  const hitRateColor =
    data.hit_rate !== null
      ? data.hit_rate >= 0.6
        ? "text-green-400"
        : data.hit_rate >= 0.5
          ? "text-yellow-400"
          : "text-red-400"
      : "text-gray-400";

  return (
    <div className="mb-4">
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
        Predictive Power
      </h4>

      <div className="grid grid-cols-3 gap-1.5 mb-2">
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-[10px] text-gray-500">Hit Rate</div>
          <div className={`text-sm font-mono ${hitRateColor}`}>
            {data.hit_rate !== null ? `${(data.hit_rate * 100).toFixed(0)}%` : "N/A"}
          </div>
        </div>
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-[10px] text-gray-500">Corr</div>
          <div className="text-sm font-mono text-gray-200">
            {data.correlation !== null ? data.correlation.toFixed(3) : "N/A"}
          </div>
        </div>
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-[10px] text-gray-500">Obs</div>
          <div className="text-sm font-mono text-gray-200">
            {data.n_observations}
          </div>
        </div>
      </div>

      {data.avg_return_bullish !== null || data.avg_return_bearish !== null ? (
        <div className="flex gap-2 mb-2 text-[10px]">
          {data.avg_return_bullish !== null && (
            <span className="text-green-400">
              Bullish avg: {data.avg_return_bullish > 0 ? "+" : ""}
              {data.avg_return_bullish.toFixed(2)}%
            </span>
          )}
          {data.avg_return_bearish !== null && (
            <span className="text-red-400">
              Bearish avg: {data.avg_return_bearish > 0 ? "+" : ""}
              {data.avg_return_bearish.toFixed(2)}%
            </span>
          )}
        </div>
      ) : null}

      {data.scatter_points.length > 0 && (
        <canvas
          ref={canvasRef}
          width={280}
          height={160}
          className="w-full rounded bg-gray-800/50"
        />
      )}
    </div>
  );
}
