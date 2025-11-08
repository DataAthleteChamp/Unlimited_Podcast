import { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";

interface RealAudioPlayerProps {
  onVolumeChange: (volume: number) => void;
  audioUrl?: string;
  speaker?: string;
}

interface AudioQueueItem {
  url: string;
  speaker: string;
}

export const RealAudioPlayer = ({
  onVolumeChange,
  audioUrl,
  speaker
}: RealAudioPlayerProps) => {
  const [bars, setBars] = useState<number[]>(Array(40).fill(0));
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const animationRef = useRef<number>();
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // Queue to prevent interruptions
  const audioQueueRef = useRef<AudioQueueItem[]>([]);
  const isProcessingQueueRef = useRef(false);
  const currentAudioUrlRef = useRef<string | undefined>();
  const currentSpeakerRef = useRef<string | undefined>();

  // Color gradient based on speaker
  const getBarColor = (index: number) => {
    const position = index / (bars.length - 1);

    if (speaker === "mira") {
      // Mira: Pink to Purple gradient
      if (position < 0.5) {
        return `hsl(${330 + position * 40}, 75%, 60%)`;
      } else {
        return `hsl(${280 - (position - 0.5) * 40}, 70%, 65%)`;
      }
    } else {
      // Alex: Yellow to Orange gradient
      if (position < 0.5) {
        return `hsl(${60 - position * 60}, 100%, 60%)`;
      } else {
        return `hsl(${30 - (position - 0.5) * 60}, 90%, 60%)`;
      }
    }
  };

  // Animate bars continuously
  useEffect(() => {
    const animate = () => {
      // More active animation when playing, calm when not
      const intensity = isPlaying ? 0.7 : 0.2;
      const baseHeight = isPlaying ? 0.3 : 0;

      const newBars = Array(40)
        .fill(0)
        .map(() => Math.random() * intensity + baseHeight);
      setBars(newBars);

      const avgVolume = newBars.reduce((a, b) => a + b, 0) / newBars.length;
      onVolumeChange(avgVolume);

      animationRef.current = requestAnimationFrame(animate);
    };

    // Start animation
    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, onVolumeChange]);

  // Process audio queue
  const processQueue = async () => {
    if (isProcessingQueueRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isProcessingQueueRef.current = true;
    const nextItem = audioQueueRef.current.shift();

    if (nextItem && audioRef.current) {
      const audio = audioRef.current;
      const fullUrl = nextItem.url.startsWith('http') ? nextItem.url : `${API_URL}${nextItem.url}`;

      currentAudioUrlRef.current = nextItem.url;
      currentSpeakerRef.current = nextItem.speaker;

      audio.src = fullUrl;
      try {
        await audio.play();
      } catch (error) {
        console.error("Error playing audio:", error);
        isProcessingQueueRef.current = false;
        processQueue(); // Try next item
      }
    }
  };

  // Add new audio to queue when URL changes
  useEffect(() => {
    if (audioUrl && speaker && audioUrl !== currentAudioUrlRef.current) {
      // Add to queue
      audioQueueRef.current.push({ url: audioUrl, speaker });
      console.log(`Queued audio for ${speaker}, queue length: ${audioQueueRef.current.length}`);

      // Start processing if not already
      processQueue();
    }
  }, [audioUrl, speaker, API_URL]);

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);
  const handleEnded = () => {
    setIsPlaying(false);
    isProcessingQueueRef.current = false;

    // Play next in queue
    if (audioQueueRef.current.length > 0) {
      console.log(`Audio ended, processing next in queue (${audioQueueRef.current.length} remaining)`);
      processQueue();
    } else {
      console.log("Audio ended, queue empty");
    }
  };

  return (
    <div className="flex flex-col items-center gap-2 w-full">
      {/* Audio element */}
      <audio
        ref={audioRef}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        className="hidden"
      />

      {/* Visualizer */}
      <div className="flex items-center justify-center gap-1 h-32 w-full">
        {bars.map((height, index) => (
          <div
            key={index}
            className="w-1 rounded-full transition-all duration-100"
            style={{
              height: `${height * 100}%`,
              backgroundColor: getBarColor(index)
            }}
          />
        ))}
      </div>

      {/* Status indicator */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {isPlaying ? (
          <>
            <Volume2 className="w-4 h-4 animate-pulse" />
            <span>Now Playing</span>
          </>
        ) : (
          <>
            <VolumeX className="w-4 h-4" />
            <span>Idle</span>
          </>
        )}
      </div>
    </div>
  );
};
