import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ThumbsUp, X } from "lucide-react";

interface TopicCardProps {
  id: number;
  title: string;
  description: string;
  votes: number;
  isVoted: boolean;
  onVote: () => void;
  onRemove: () => void;
}

export const TopicCard = ({
  title,
  description,
  votes,
  isVoted,
  onVote,
  onRemove,
}: TopicCardProps) => {
  return (
    <Card
      className={`p-6 bg-gradient-card hover:shadow-card-hover transition-all duration-300 ${
        isVoted ? "ring-2 ring-accent" : ""
      }`}
    >
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        
        <div className="flex items-center justify-between">
          <Button
            variant={isVoted ? "default" : "outline"}
            size="sm"
            onClick={onVote}
            className="gap-2"
          >
            <ThumbsUp className="w-4 h-4" />
            {votes}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onRemove}
            className="text-destructive hover:text-destructive"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};
