import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Music2, Clock } from "lucide-react";

interface QueueTopic {
  id: string;
  text: string;
  votes: number;
}

interface QueueInfo {
  current_topic: string;
  queue: QueueTopic[];
  queue_length: number;
  used_count: number;
}

export const QueueView = () => {
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchQueue = async () => {
      try {
        const response = await fetch(`${API_URL}/api/podcast/queue`);
        if (response.ok) {
          const data = await response.json();
          setQueueInfo(data);
        }
      } catch (error) {
        console.error("Error fetching queue:", error);
      }
    };

    // Initial fetch
    fetchQueue();

    // Poll every 5 seconds
    const interval = setInterval(fetchQueue, 5000);

    return () => clearInterval(interval);
  }, [API_URL]);

  if (!queueInfo) return null;

  return (
    <Card className="p-4 bg-card border-border">
      <div className="space-y-4">
        {/* Now Playing */}
        {queueInfo.current_topic && (
          <div className="flex items-start gap-3 p-3 bg-gradient-to-r from-orange-500/10 to-purple-500/10 rounded-lg border border-orange-500/20">
            <Music2 className="w-5 h-5 text-orange-500 mt-0.5 animate-pulse" />
            <div className="flex-1">
              <p className="text-xs font-medium text-muted-foreground mb-1">
                Now Playing
              </p>
              <p className="text-sm font-semibold">{queueInfo.current_topic}</p>
            </div>
          </div>
        )}

        {/* Queue */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Up Next
            </h3>
            <Badge variant="secondary" className="text-xs">
              {queueInfo.queue_length} in queue
            </Badge>
          </div>

          {queueInfo.queue.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground text-sm">
              Queue is empty. Vote on topics to add them!
            </div>
          ) : (
            <div className="space-y-2">
              {queueInfo.queue.map((topic, index) => (
                <div
                  key={topic.id}
                  className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex-shrink-0">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{topic.text}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">
                        ~{(index + 1) * 2} min
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Stats */}
        {queueInfo.used_count > 0 && (
          <div className="pt-3 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              {queueInfo.used_count} topics discussed so far
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};
