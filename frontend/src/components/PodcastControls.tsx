import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Play, Square, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface PodcastControlsProps {
  onStatusChange?: (running: boolean) => void;
}

export const PodcastControls = ({ onStatusChange }: PodcastControlsProps) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/podcast/start`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to start podcast");
      }

      const data = await response.json();
      setIsRunning(true);
      onStatusChange?.(true);
      toast.success("Podcast started! Alex and Mira will begin discussing soon.");
    } catch (error) {
      console.error("Error starting podcast:", error);
      toast.error("Failed to start podcast");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/podcast/stop`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to stop podcast");
      }

      const data = await response.json();
      setIsRunning(false);
      onStatusChange?.(false);
      toast.info("Podcast stopped");
    } catch (error) {
      console.error("Error stopping podcast:", error);
      toast.error("Failed to stop podcast");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-4 bg-card border-border">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-lg">Podcast Control</h3>
          <p className="text-sm text-muted-foreground">
            {isRunning ? "Podcast is running" : "Ready to start"}
          </p>
        </div>
        <div className="flex gap-2">
          {!isRunning ? (
            <Button
              onClick={handleStart}
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Podcast
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleStop}
              disabled={isLoading}
              variant="destructive"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Stopping...
                </>
              ) : (
                <>
                  <Square className="w-4 h-4 mr-2" />
                  Stop Podcast
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};
