"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useGraphStore } from "@/hooks/useGraphData";

const RANGE_HOURS = 7 * 24; // 7 days
const STEP_HOURS = 1;
const TOTAL_STEPS = RANGE_HOURS / STEP_HOURS;

function formatTimestamp(date: Date): string {
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function TimeSlider() {
  const [open, setOpen] = useState(false);
  const [sliderValue, setSliderValue] = useState(TOTAL_STEPS); // Start at "now"
  const [playing, setPlaying] = useState(false);
  const fetchSnapshot = useGraphStore((s) => s.fetchSnapshot);
  const clearSnapshot = useGraphStore((s) => s.clearSnapshot);
  const snapshotTimestamp = useGraphStore((s) => s.snapshotTimestamp);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const sliderValueRef = useRef(TOTAL_STEPS);

  const now = useRef(new Date());

  const getTimestamp = useCallback(
    (step: number): Date => {
      const offset = (TOTAL_STEPS - step) * STEP_HOURS * 3600 * 1000;
      return new Date(now.current.getTime() - offset);
    },
    []
  );

  const handleSliderChange = useCallback(
    (value: number) => {
      setSliderValue(value);
      sliderValueRef.current = value;
      // Debounce API calls while dragging
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (value >= TOTAL_STEPS) {
          clearSnapshot();
        } else {
          const ts = getTimestamp(value);
          fetchSnapshot(ts.toISOString());
        }
      }, 150);
    },
    [fetchSnapshot, clearSnapshot, getTimestamp]
  );

  // Auto-play: advance slider and fetch snapshots on a timer
  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        const prev = sliderValueRef.current;
        const next = prev + 1;
        if (next > TOTAL_STEPS) {
          setPlaying(false);
          setSliderValue(TOTAL_STEPS);
          clearSnapshot();
          return;
        }
        setSliderValue(next);
        sliderValueRef.current = next;
        const ts = getTimestamp(next);
        fetchSnapshot(ts.toISOString());
      }, 500);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing, fetchSnapshot, clearSnapshot, getTimestamp]);

  const handleClose = () => {
    setOpen(false);
    setPlaying(false);
    setSliderValue(TOTAL_STEPS);
    sliderValueRef.current = TOTAL_STEPS;
    clearSnapshot();
  };

  const currentTimestamp = getTimestamp(sliderValue);
  const isLive = sliderValue >= TOTAL_STEPS;

  return (
    <div className="relative">
      <button
        onClick={() => {
          if (open) {
            handleClose();
          } else {
            now.current = new Date();
            setOpen(true);
          }
        }}
        className="bg-gray-800/90 backdrop-blur border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white transition-colors"
      >
        Time Travel
      </button>

      {open && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-[6] w-[600px] max-w-[90vw] bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg px-4 py-3 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPlaying(!playing)}
                className="text-xs bg-gray-700 hover:bg-gray-600 text-white px-2 py-1 rounded"
              >
                {playing ? "⏸" : "▶"}
              </button>
              <span className="text-xs text-gray-300 font-mono">
                {isLive ? (
                  <span className="text-green-400">● LIVE</span>
                ) : (
                  formatTimestamp(currentTimestamp)
                )}
              </span>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-white text-sm"
            >
              &times;
            </button>
          </div>

          <input
            type="range"
            min={0}
            max={TOTAL_STEPS}
            step={1}
            value={sliderValue}
            onChange={(e) => handleSliderChange(Number(e.target.value))}
            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />

          <div className="flex justify-between mt-1 text-[10px] text-gray-500">
            <span>{formatTimestamp(getTimestamp(0))}</span>
            <span>Now</span>
          </div>
        </div>
      )}
    </div>
  );
}
