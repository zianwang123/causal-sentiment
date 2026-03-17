"use client";

import { useEffect, useRef, useState } from "react";
import { API_URL as API } from "@/lib/config";

interface CausalHistoryPoint {
  date: string;
  raw_value: number;
  scored_value: number;
}

interface CausalHistoryResponse {
  node_id: string;
  scoring: string;
  days: number;
  history: CausalHistoryPoint[];
}

type Range = 30 | 90 | 365;

export default function CausalScoreChart({
  nodeId,
  scoring,
}: {
  nodeId: string;
  scoring: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<
    typeof import("lightweight-charts").createChart
  > | null>(null);
  const [range, setRange] = useState<Range>(90);
  const [data, setData] = useState<CausalHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch history data
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    fetch(`${API}/api/causal/node/${nodeId}?scoring=${scoring}&days=${range}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((d: CausalHistoryResponse) => {
        setData(d.history ?? []);
        setLoading(false);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setLoading(false);
      });
    return () => controller.abort();
  }, [nodeId, scoring, range]);

  // Render chart
  useEffect(() => {
    if (!containerRef.current || typeof window === "undefined") return;

    let cancelled = false;

    import("lightweight-charts").then(({ createChart, ColorType, LineStyle }) => {
      if (cancelled || !containerRef.current) return;

      // Clean up previous chart
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }

      const chart = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height: 160,
        layout: {
          background: { type: ColorType.Solid, color: "#1a1a2e" },
          textColor: "#9ca3af",
          fontSize: 10,
        },
        grid: {
          vertLines: { color: "#1f2937" },
          horzLines: { color: "#1f2937" },
        },
        timeScale: {
          borderColor: "#374151",
          timeVisible: true,
        },
        rightPriceScale: {
          borderColor: "#374151",
        },
        crosshair: {
          horzLine: { style: LineStyle.Dotted },
          vertLine: { style: LineStyle.Dotted },
        },
      });

      chartRef.current = chart;

      const series = chart.addLineSeries({
        color: "#a855f7",
        lineWidth: 2,
        priceFormat: { type: "price", precision: 3, minMove: 0.001 },
      });

      // Zero line
      series.createPriceLine({
        price: 0,
        color: "#4b5563",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: false,
      });

      if (data.length > 0) {
        // Deduplicate and sort by date (lightweight-charts requires strictly increasing times)
        const byTime = new Map<number, number>();
        for (const d of data) {
          // date strings like "2025-01-15" — parse as UTC midnight
          const t = Math.floor(new Date(d.date + "T00:00:00Z").getTime() / 1000);
          // Last value wins for duplicate dates
          byTime.set(t, d.scored_value);
        }
        const chartData = Array.from(byTime.entries())
          .sort((a, b) => a[0] - b[0])
          .map(([t, v]) => ({
            time: t as import("lightweight-charts").UTCTimestamp,
            value: v,
          }));
        if (chartData.length > 0) {
          series.setData(chartData);
          chart.timeScale().fitContent();
        }
      }
    });

    return () => {
      cancelled = true;
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data]);

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <h4 className="text-xs font-semibold text-gray-400 uppercase">
          Score History
        </h4>
        <div className="flex gap-1">
          {([30, 90, 365] as Range[]).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`text-xs px-2 py-0.5 rounded ${
                range === r
                  ? "bg-purple-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-white"
              }`}
            >
              {r}d
            </button>
          ))}
        </div>
      </div>
      {loading ? (
        <div className="h-[160px] bg-gray-800/50 rounded flex items-center justify-center text-xs text-gray-500">
          Loading...
        </div>
      ) : data.length === 0 ? (
        <div className="h-[160px] bg-gray-800/50 rounded flex items-center justify-center text-xs text-gray-500">
          No score history available
        </div>
      ) : (
        <div
          ref={containerRef}
          className="rounded overflow-hidden"
          style={{ minHeight: 160 }}
        />
      )}
    </div>
  );
}
