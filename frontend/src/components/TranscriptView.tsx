import { useEffect, useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface TranscriptEntry {
  speaker: string;
  text: string;
  timestamp: number;
  turn_number: number;
}

export const TranscriptView = () => {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchTranscript = async () => {
      try {
        const response = await fetch(`${API_URL}/api/podcast/transcript`);
        if (response.ok) {
          const data = await response.json();
          setTranscript(data);
        }
      } catch (error) {
        console.error("Error fetching transcript:", error);
      }
    };

    // Initial fetch
    fetchTranscript();

    // Poll every 10 seconds
    const interval = setInterval(fetchTranscript, 10000);

    return () => clearInterval(interval);
  }, [API_URL]);

  useEffect(() => {
    // Auto-scroll to bottom when new entries arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcript]);

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <Card className="h-full flex flex-col bg-card">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">Transcript</h2>
        <p className="text-sm text-muted-foreground">
          {transcript.length > 0
            ? `${transcript.length} entries`
            : "No dialogue yet"}
        </p>
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {transcript.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>Start the podcast to see the conversation between Alex and Mira</p>
            </div>
          ) : (
            transcript.map((entry, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg ${
                  entry.speaker === "Alex"
                    ? "bg-orange-500/10 border-l-4 border-orange-500"
                    : "bg-purple-500/10 border-l-4 border-purple-500"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={entry.speaker === "Alex" ? "default" : "secondary"}
                      className={
                        entry.speaker === "Alex"
                          ? "bg-orange-500"
                          : "bg-purple-500"
                      }
                    >
                      {entry.speaker}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      Turn {entry.turn_number}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatTimestamp(entry.timestamp)}
                  </span>
                </div>
                <p className="text-sm leading-relaxed">{entry.text}</p>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </Card>
  );
};
