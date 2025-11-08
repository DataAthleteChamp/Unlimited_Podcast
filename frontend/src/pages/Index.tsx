import { useState, useCallback, useEffect } from "react";
import { AgentAvatar } from "@/components/AgentAvatar";
import { RealAudioPlayer } from "@/components/RealAudioPlayer";
import { TopicCard } from "@/components/TopicCard";
import { ChatSidebar } from "@/components/ChatSidebar";
import { PodcastControls } from "@/components/PodcastControls";
import { PodcastStatus } from "@/components/PodcastStatus";
import { QueueView } from "@/components/QueueView";
import { toast } from "sonner";
interface Topic {
  id: number;
  title: string;
  description: string;
  votes: number;
}
interface Message {
  text: string;
  sender: string;
  timestamp: string;
}
const Index = () => {
  const [volume, setVolume] = useState(0);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [votedTopicId, setVotedTopicId] = useState<number | null>(null);
  const [isLoadingTopics, setIsLoadingTopics] = useState(false);
  const [podcastRunning, setPodcastRunning] = useState(false);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | undefined>();
  const [currentSpeaker, setCurrentSpeaker] = useState<string | undefined>();
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  // SSE connection for real-time updates
  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/api/stream`);

    eventSource.addEventListener("NOW_PLAYING", (event) => {
      try {
        const data = JSON.parse(event.data);
        setCurrentAudioUrl(data.audio_url);
        setCurrentSpeaker(data.speaker);
      } catch (error) {
        console.error("Error parsing NOW_PLAYING event:", error);
      }
    });

    eventSource.addEventListener("TOPIC_CHANGED", (event) => {
      try {
        const data = JSON.parse(event.data);
        // New topic started - transcript will be cleared by backend
        toast.info(`Now discussing: ${data.topic_text}`);
      } catch (error) {
        console.error("Error parsing TOPIC_CHANGED event:", error);
      }
    });

    eventSource.addEventListener("QUEUE_UPDATED", () => {
      // Queue updated - QueueView component will handle display
    });

    eventSource.addEventListener("TRANSCRIPT_UPDATE", () => {
      // Transcript updates handled by polling
    });

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [API_URL]);

  // Poll for now playing audio
  useEffect(() => {
    if (!podcastRunning) return;

    const pollNowPlaying = async () => {
      try {
        const response = await fetch(`${API_URL}/api/podcast/now`);
        if (response.ok) {
          const data = await response.json();
          if (data && data.audio_url) {
            setCurrentAudioUrl(data.audio_url);
            setCurrentSpeaker(data.speaker);
          }
        }
      } catch (error) {
        console.error("Error polling now playing:", error);
      }
    };

    pollNowPlaying();
    const interval = setInterval(pollNowPlaying, 5000);

    return () => clearInterval(interval);
  }, [API_URL, podcastRunning]);

  const handleVolumeChange = useCallback((newVolume: number) => {
    setVolume(newVolume);
  }, []);
  const handleMessagesUpdate = async (messages: Message[]) => {
    if (messages.length === 0) return;

    setIsLoadingTopics(true);
    try {
      console.log("Generating topics from messages:", messages);

      const response = await fetch(`${API_URL}/api/topics/suggestions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          messages
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Failed to fetch topics:", response.status, errorText);
        throw new Error(`Failed to fetch topic suggestions: ${response.status}`);
      }

      const newTopics = await response.json();
      console.log("Received topics:", newTopics);

      if (Array.isArray(newTopics) && newTopics.length > 0) {
        setTopics(newTopics);
        toast.success("New topic suggestions generated!");
      } else {
        console.warn("No topics received");
        toast.info("Try sending another message to generate topics");
      }
    } catch (error) {
      console.error("Error fetching topics:", error);
      toast.error("Failed to generate topic suggestions. Check console for details.");
    } finally {
      setIsLoadingTopics(false);
    }
  };
  const handleVote = async (topicId: number) => {
    // First, update local state immediately for responsiveness
    const topic = topics.find(t => t.id === topicId);
    if (!topic) return;

    if (votedTopicId === topicId) {
      // Unvote - remove from local state
      setTopics(prev => prev.map(t => t.id === topicId ? {
        ...t,
        votes: Math.max(0, t.votes - 1) // Don't go below 0
      } : t));
      setVotedTopicId(null);
      toast.info("Vote removed");
      return; // Don't add to queue if unvoting
    }

    // Voting on a new topic
    setTopics(prev => prev.map(t => {
      if (t.id === topicId) return {
        ...t,
        votes: t.votes + 1
      };
      if (t.id === votedTopicId) return {
        ...t,
        votes: Math.max(0, t.votes - 1) // Don't go below 0
      };
      return t;
    }));
    setVotedTopicId(topicId);

    // Create topic in backend and add to queue
    try {
      const createResponse = await fetch(`${API_URL}/api/topic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: topic.title,
          nickname: "WebUser"
        })
      });

      if (createResponse.ok) {
        const createdTopic = await createResponse.json();

        // Add to podcast queue
        const queueResponse = await fetch(
          `${API_URL}/api/podcast/queue/add/${createdTopic.id}`,
          { method: "POST" }
        );

        if (queueResponse.ok) {
          const queueData = await queueResponse.json();
          if (queueData.success) {
            toast.success(`Added to queue at position ${queueData.position}! 🎉`);
          } else {
            toast.info(queueData.message);
          }
        }
      }
    } catch (error) {
      console.error("Error adding topic to queue:", error);
      toast.error("Failed to add topic to queue");
    }
  };
  const handleRemove = (topicId: number) => {
    setTopics(prev => prev.filter(t => t.id !== topicId));
    if (votedTopicId === topicId) {
      setVotedTopicId(null);
    }
    toast.info("Topic removed");
  };
  return <div className="h-screen bg-background overflow-hidden">
      <div className="container mx-auto p-6 h-full flex flex-col">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-4">
            The Endless Podcast
          </h1>
          <p className="text-xl text-muted-foreground">
            Watch two AI agents discuss topics in real-time
          </p>
        </div>

        {/* Main Layout */}
        <div className="grid lg:grid-cols-[1fr_400px] gap-6 flex-1 overflow-hidden">
          {/* Main Content */}
          <div className="space-y-6 overflow-y-auto">
            {/* Podcast Controls */}
            <PodcastControls onStatusChange={setPodcastRunning} />

            {/* Agents Display */}
            <div className="flex items-center justify-center gap-2 sm:gap-4 p-2 sm:p-4 bg-card rounded-lg border border-border animate-scale-in overflow-hidden">
              <AgentAvatar name="Alex" type="alex" volume={volume} />
              <div className="w-full max-w-md">
                <RealAudioPlayer
                  onVolumeChange={handleVolumeChange}
                  audioUrl={currentAudioUrl}
                  speaker={currentSpeaker}
                />
              </div>
              <AgentAvatar name="Mira" type="mira" volume={volume} />
            </div>

            {/* Status and Queue Grid */}
            <div className="grid md:grid-cols-2 gap-4">
              <PodcastStatus />
              <QueueView />
            </div>

            {/* Topic Voting Section */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">
                Vote for Topics
              </h2>

              {isLoadingTopics ? <div className="text-center py-12 text-muted-foreground">
                  Generating topic suggestions...
                </div> : topics.length === 0 ? <div className="text-center py-12 text-muted-foreground">
                  Start a conversation to see AI-generated topic suggestions
                </div> : <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {topics.map(topic => <TopicCard key={topic.id} {...topic} isVoted={votedTopicId === topic.id} onVote={() => handleVote(topic.id)} onRemove={() => handleRemove(topic.id)} />)}
                </div>}
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="h-full overflow-hidden">
            <ChatSidebar onMessagesUpdate={handleMessagesUpdate} />
          </div>
        </div>
      </div>
    </div>;
};
export default Index;