import { useEffect, useState } from "react";

interface AudioVisualizerProps {
  onVolumeChange: (volume: number) => void;
}

export const AudioVisualizer = ({ onVolumeChange }: AudioVisualizerProps) => {
  const [bars, setBars] = useState<number[]>(Array(40).fill(0));

  useEffect(() => {
    const interval = setInterval(() => {
      const newBars = Array(40)
        .fill(0)
        .map(() => Math.random());
      setBars(newBars);
      
      // Calculate average volume (0 to 1)
      const avgVolume = newBars.reduce((a, b) => a + b, 0) / newBars.length;
      onVolumeChange(avgVolume);
    }, 100);

    return () => clearInterval(interval);
  }, [onVolumeChange]);

  // Color gradient: yellow -> orange -> pink -> purple -> blue
  const getBarColor = (index: number) => {
    const position = index / (bars.length - 1);
    if (position < 0.25) {
      // Yellow to Orange
      return `hsl(${60 - position * 120}, 100%, 60%)`;
    } else if (position < 0.5) {
      // Orange to Pink
      return `hsl(${30 - (position - 0.25) * 80}, 90%, 60%)`;
    } else if (position < 0.75) {
      // Pink to Purple
      return `hsl(${330 + (position - 0.5) * 80}, 75%, 60%)`;
    } else {
      // Purple to Blue
      return `hsl(${280 - (position - 0.75) * 80}, 70%, 65%)`;
    }
  };

  return (
    <div className="flex items-center justify-center gap-1 h-32">
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
  );
};
