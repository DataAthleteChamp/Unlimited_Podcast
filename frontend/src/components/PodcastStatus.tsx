import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Clock, Hash } from "lucide-react";

interface PodcastStatusData {
  running: boolean;
  current_topic: string | null;
  turn_count: number;
  uptime_seconds: number;
}

export const PodcastStatus = () => {
  const [status, setStatus] = useState<PodcastStatusData | null>(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/podcast/status`);
        if (response.ok) {
          const data = await response.json();
          setStatus(data);
        }
      } catch (error) {
        console.error("Error fetching podcast status:", error);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 5 seconds
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, [API_URL]);

  if (!status) return null;

  const formatUptime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  return (
    <Card className="p-4 bg-card border-border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Podcast Status</h3>
        <Badge variant={status.running ? "default" : "secondary"}>
          {status.running ? "Live" : "Stopped"}
        </Badge>
      </div>

      <div className="space-y-2 text-sm">
        {status.current_topic && (
          <div className="flex items-start gap-2">
            <Activity className="w-4 h-4 mt-0.5 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Current Topic</p>
              <p className="font-medium">{status.current_topic}</p>
            </div>
          </div>
        )}

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Hash className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Turns</p>
              <p className="font-medium">{status.turn_count}</p>
            </div>
          </div>

          {status.running && (
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Uptime</p>
                <p className="font-medium">{formatUptime(status.uptime_seconds)}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
