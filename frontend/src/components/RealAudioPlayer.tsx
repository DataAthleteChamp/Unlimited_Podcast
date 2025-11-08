import { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";

interface RealAudioPlayerProps {
  onVolumeChange: (volume: number) => void;
  audioUrl?: string;
  speaker?: string;
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

  // Play audio when URL changes
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      const audio = audioRef.current;
      const fullUrl = audioUrl.startsWith('http') ? audioUrl : `${API_URL}${audioUrl}`;

      audio.src = fullUrl;
      audio.play().catch((error) => {
        console.error("Error playing audio:", error);
      });
    }
  }, [audioUrl, API_URL]);

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);
  const handleEnded = () => setIsPlaying(false);

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
