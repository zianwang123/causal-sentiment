"use client";

import { useCallback, useEffect, useState } from "react";

import { API_URL as API } from "@/lib/config";

interface Automation {
  id: string;
  label: string;
  description: string;
  enabled: boolean;
  schedule: string | null;
}

export default function AutomationToggles() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [toggling, setToggling] = useState<string | null>(null);

  const fetchAutomations = useCallback(() => {
    fetch(`${API}/api/agent/automations`)
      .then((r) => r.json())
      .then((data: { automations: Automation[] }) =>
        setAutomations(data.automations)
      )
      .catch((e) => console.error("Failed to fetch automations:", e));
  }, []);

  useEffect(() => {
    fetchAutomations();
    const interval = setInterval(fetchAutomations, 30_000);
    return () => clearInterval(interval);
  }, [fetchAutomations]);

  const toggle = async (id: string, enabled: boolean) => {
    setToggling(id);
    try {
      const res = await fetch(`${API}/api/agent/automations/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ automation_id: id, enabled }),
      });
      const data = await res.json();
      setAutomations(data.automations);
    } catch (e) {
      console.error("Toggle failed:", e);
    } finally {
      setToggling(null);
    }
  };

  if (automations.length === 0) return null;

  return (
    <div className="space-y-1.5">
      {automations.map((a) => (
        <div
          key={a.id}
          className="flex items-center justify-between gap-2"
          title={`${a.description}${a.schedule ? ` (${a.schedule})` : ""}`}
        >
          <div className="flex items-center gap-1.5 min-w-0">
            <div
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                a.enabled ? "bg-green-400" : "bg-gray-600"
              }`}
            />
            <span className="text-[11px] text-gray-300 truncate">{a.label}</span>
          </div>
          <button
            onClick={() => toggle(a.id, !a.enabled)}
            disabled={toggling === a.id}
            className={`shrink-0 ${toggling === a.id ? "opacity-50" : ""}`}
            style={{
              position: "relative",
              width: 28,
              height: 14,
              borderRadius: 7,
              backgroundColor: a.enabled ? "#16a34a" : "#4b5563",
              transition: "background-color 0.2s",
              border: "none",
              padding: 0,
              cursor: "pointer",
            }}
          >
            <span
              style={{
                position: "absolute",
                top: 2,
                left: a.enabled ? 14 : 2,
                width: 10,
                height: 10,
                borderRadius: "50%",
                backgroundColor: "white",
                transition: "left 0.2s",
              }}
            />
          </button>
        </div>
      ))}
    </div>
  );
}
