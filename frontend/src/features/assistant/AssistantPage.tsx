import React, { useState, useEffect, useRef } from "react";
import {
  BotMessageSquare,
  Mic,
  MicOff,
  Send,
  Upload,
  Sparkles,
  Volume2,
  Trash2,
  AlertCircle,
  FileAudio,
  User,
  Check,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { ChatMessage } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const AssistantPage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const audioInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [inputMessage, setInputMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: "assistant",
      content:
        "Hello! I am FoodVerse AI, your multimodal food intelligence agent. I can help with food nutrition scaling, freshness evaluations, kitchen hygiene practices, recipe suggestions, and personalized meal planning. You can type or upload an audio voice note below.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Audio / Speech-to-text
  const [isRecording, setIsRecording] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcribing, setTranscribing] = useState(false);
  const [transcriptNotice, setTranscriptNotice] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage.trim();
    if (!text) return;

    const userMsg: ChatMessage = { sender: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setLoading(true);
    setTranscriptNotice(null);

    try {
      const res = await api.chatAssistant({
        message: text,
        conversation_id: conversationId,
        modality: "text",
      });

      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        { sender: "assistant", content: res.reply },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          content:
            "I encountered an issue processing your query. Please check your network or backend AI configuration.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAudioFile(file);
    setTranscribing(true);
    setTranscriptNotice(null);

    try {
      const formData = new FormData();
      formData.append("audio", file);
      const res = await api.transcribeAudio(formData);
      setInputMessage(res.transcript);
      setTranscriptNotice("Voice transcribed! Review and press send.");
    } catch (err: any) {
      setTranscriptNotice(
        err.message ||
          "Could not transcribe audio. Speech-to-Text requires GEMINI_API_KEY or OPENAI_API_KEY in backend/.env."
      );
    } finally {
      setTranscribing(false);
    }
  };

  const startMicrophoneRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const file = new File([audioBlob], "recording.webm", { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());

        setTranscribing(true);
        try {
          const formData = new FormData();
          formData.append("audio", file);
          const res = await api.transcribeAudio(formData);
          setInputMessage(res.transcript);
          setTranscriptNotice("Microphone recording transcribed! You can edit or press Send.");
        } catch (err: any) {
          setTranscriptNotice(
            err.message ||
              "Could not transcribe recording. Configure GEMINI_API_KEY in backend/.env."
          );
        } finally {
          setTranscribing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setTranscriptNotice(
        "Microphone access denied or not supported by browser. You can still upload an audio file directly."
      );
    }
  };

  const stopMicrophoneRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto h-[calc(100vh-10rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
            <BotMessageSquare className="w-4 h-4" />
            <span>Multimodal Reasoning Hub</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
            FoodVerse Multimodal AI Assistant
          </h1>
        </div>

        <Badge variant="success" size="md">
          Live Reasoning
        </Badge>
      </div>

      {/* Chat Messages Panel */}
      <Card className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 flex flex-col">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 text-xs leading-relaxed max-w-[85%] ${
              msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
            }`}
          >
            <div
              className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 ${
                msg.sender === "user"
                  ? "bg-emerald-700 text-white font-bold"
                  : "bg-emerald-100 text-emerald-800"
              }`}
            >
              {msg.sender === "user" ? (
                <User className="w-3.5 h-3.5" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
              )}
            </div>

            <div
              className={`p-3.5 rounded-2xl ${
                msg.sender === "user"
                  ? "bg-emerald-700 text-white"
                  : "bg-gray-50 border border-gray-100 text-gray-800"
              }`}
            >
              <p className="whitespace-pre-line">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-400 p-2 animate-pulse">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600 animate-spin" />
            <span>FoodVerse AI is reasoning across nutrition science and culinary data...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </Card>

      {/* Transcription Notice Box */}
      {transcriptNotice && (
        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between">
          <span>{transcriptNotice}</span>
          <button
            onClick={() => setTranscriptNotice(null)}
            className="text-emerald-700 hover:text-emerald-950 font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Input Bar */}
      <Card className="p-3 sm:p-4">
        {/* Quick query buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 text-[11px]">
          <span className="text-gray-400 shrink-0 font-medium">Quick Prompts:</span>
          {[
            "How do I boost protein in a vegetarian diet?",
            "What visual cues indicate spoiled chicken?",
            "Healthy dinner recipe under 25 minutes",
          ].map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(prompt)}
              className="px-2.5 py-1 rounded-lg bg-gray-50 hover:bg-emerald-50 hover:text-emerald-800 border border-gray-200 text-gray-600 whitespace-nowrap transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 pt-1">
          {/* Audio recording button */}
          <button
            type="button"
            onClick={isRecording ? stopMicrophoneRecording : startMicrophoneRecording}
            className={`p-2.5 rounded-xl border transition-all ${
              isRecording
                ? "bg-rose-600 text-white border-rose-600 animate-pulse"
                : "bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200"
            }`}
            title={isRecording ? "Stop recording" : "Record voice query"}
          >
            {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          {/* Audio file upload button */}
          <button
            type="button"
            onClick={() => audioInputRef.current?.click()}
            className="p-2.5 rounded-xl bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200"
            title="Upload audio file"
          >
            <Upload className="w-4 h-4" />
          </button>
          <input
            ref={audioInputRef}
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={handleAudioUpload}
          />

          {/* Text Input */}
          <input
            type="text"
            placeholder={
              transcribing
                ? "Transcribing audio..."
                : isRecording
                ? "Listening to voice input..."
                : "Ask anything about nutrition, cooking, or freshness..."
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={loading || transcribing}
            className="flex-1 text-xs rounded-xl border border-gray-200 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />

          <Button
            variant="primary"
            size="md"
            onClick={() => handleSendMessage()}
            loading={loading || transcribing}
            icon={<Send className="w-4 h-4" />}
          >
            Send
          </Button>
        </div>
      </Card>
    </div>
  );
};
