import React, { useState, useEffect, useRef } from "react";
import {
  Video,
  Upload,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  FileText,
  Info,
  Sparkles,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { Card } from "../../components/common/Card";
import { Badge } from "../../components/common/Badge";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../api/client";
import { HygieneReport } from "../../types";
import { useAuth } from "../../context/AuthContext";

export const HygienePage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<HygieneReport | null>(null);
  const [history, setHistory] = useState<HygieneReport[]>([]);

  useEffect(() => {
    if (isAuthenticated) {
      api.getHygieneHistory().then(setHistory).catch(() => null);
    }
  }, [isAuthenticated]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setVideoPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please choose a video file (MP4 or MOV, max 50MB).");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("video", selectedFile);
      formData.append("interval_seconds", "2.0");

      const result = await api.analyzeHygieneVideo(formData);
      setReport(result);

      if (isAuthenticated) {
        api.getHygieneHistory().then(setHistory).catch(() => null);
      }
    } catch (err: any) {
      setError(err.message || "Failed to process video frames. Please check file format.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (risk: string) => {
    if (risk.toLowerCase() === "low") {
      return (
        <Badge variant="success" size="md">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Low Risk Profile
        </Badge>
      );
    } else if (risk.toLowerCase() === "moderate" || risk.toLowerCase() === "medium") {
      return (
        <Badge variant="warning" size="md">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          Moderate Risk Profile
        </Badge>
      );
    } else {
      return (
        <Badge variant="danger" size="md">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
          High Risk Profile
        </Badge>
      );
    }
  };

  const getSeverityBadge = (sev: string) => {
    if (sev.toLowerCase() === "low") {
      return <Badge variant="success" size="sm">Low Priority</Badge>;
    } else if (sev.toLowerCase() === "medium" || sev.toLowerCase() === "moderate") {
      return <Badge variant="warning" size="sm">Medium Priority</Badge>;
    } else {
      return <Badge variant="danger" size="sm">High Priority</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
          <Video className="w-4 h-4" />
          <span>Computer Vision & OpenCV Keyframe Sampling</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Restaurant & Kitchen Hygiene Video Monitoring
        </h1>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-2xl">
          Upload commercial kitchen footage to automatically extract keyframes and evaluate
          observable food handling practices, glove usage, hair restraints, and surface cross-contamination.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6">
            <h2 className="text-sm font-bold text-gray-900 mb-4">
              Upload Kitchen Footage
            </h2>

            {!videoPreviewUrl ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-200 hover:border-emerald-500 rounded-2xl p-8 text-center cursor-pointer bg-gray-50/50 hover:bg-emerald-50/20 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-white shadow-sm border border-gray-200 flex items-center justify-center mx-auto mb-3 text-emerald-700 group-hover:scale-105 transition-transform">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-xs font-bold text-gray-900">
                  Select kitchen video file
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  Supports MP4, MOV, WEBM (Max 50MB, up to 120s)
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="video/mp4,video/quicktime,video/webm"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-2xl overflow-hidden border border-gray-200 bg-black aspect-video max-h-64 flex items-center justify-center">
                  <video
                    src={videoPreviewUrl}
                    controls
                    className="max-h-full max-w-full"
                  />
                </div>
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={handleAnalyze}
                  loading={loading}
                  icon={<Video className="w-4 h-4" />}
                >
                  Extract Frames & Run Hygiene Audit
                </Button>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setVideoPreviewUrl(null);
                  }}
                  className="w-full text-center text-xs text-gray-500 hover:text-gray-700"
                >
                  Choose Different Video
                </button>
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}
          </Card>

          {/* Regulatory Disclaimer Card */}
          <Card className="p-5 bg-gray-50/80 border-gray-200">
            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                  Auditing Scope & Boundaries
                </h3>
                <p className="text-[11px] text-gray-600 leading-relaxed">
                  Video auditing analyzes sampled keyframes and serves as an internal quality checklist. It does not replace mandatory local public health agency inspections or formal HACCP hazard certification.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Report (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <Card className="p-12">
              <LoadingSpinner
                message="Sampling keyframes with OpenCV and running hygiene vision models..."
                size="lg"
              />
            </Card>
          ) : report ? (
            <div className="space-y-6">
              <Card className="p-6 space-y-6">
                {/* Overall summary header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-100">
                  <div>
                    <span className="text-xs text-gray-400 uppercase font-semibold block mb-1">
                      Overall Visual Hygiene Risk
                    </span>
                    {getRiskBadge(report.overall_risk_level)}
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500 block">Frames Analyzed</span>
                    <span className="text-sm font-bold text-gray-900">
                      {report.total_frames_analyzed} keyframes
                      {report.video_duration_s ? ` (${report.video_duration_s}s)` : ""}
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-950 leading-relaxed">
                  <p className="font-semibold mb-1 text-emerald-900 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> Executive Summary:
                  </p>
                  <p>{report.overall_summary}</p>
                </div>

                {/* Timestamped Observations */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                    Timestamped Keyframe Findings ({report.findings.length})
                  </h3>
                  <div className="space-y-3">
                    {report.findings.map((f, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl border border-gray-100 bg-white shadow-subtle flex flex-col sm:flex-row items-start gap-4"
                      >
                        {f.frame_image_url && (
                          <div className="w-24 h-16 rounded-lg bg-gray-100 overflow-hidden shrink-0 border border-gray-200">
                            <img
                              src={`http://localhost:8000${f.frame_image_url}`}
                              alt={`Frame at ${f.timestamp_s}s`}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-emerald-800">
                                {f.category}
                              </span>
                              <span className="text-[11px] font-semibold text-gray-400 flex items-center gap-1">
                                <Clock className="w-3 h-3" /> {f.timestamp_s}s
                              </span>
                            </div>
                            {getSeverityBadge(f.severity)}
                          </div>
                          <p className="text-xs text-gray-700 leading-relaxed">
                            {f.observation}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Practical Recommendations */}
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Corrective Hygiene Action Items
                  </h3>
                  <div className="space-y-2">
                    {report.practical_recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-gray-50 border border-gray-100 text-xs text-gray-700"
                      >
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="text-[11px] text-gray-400 border-t border-gray-100 pt-3">
                  {report.disclaimer}
                </div>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto text-blue-700">
                <Video className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto">
                <h3 className="text-base font-bold text-gray-900">
                  Ready to Process Video
                </h3>
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Upload footage from a kitchen preparation station or restaurant line. Keyframes will be analyzed for glove protocol, hair restraints, and food segregation.
                </p>
              </div>
            </Card>
          )}

          {/* Past Audits */}
          {isAuthenticated && history.length > 0 && (
            <Card className="p-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                <span>Recent Video Audits</span>
                <span className="text-xs text-gray-400">{history.length} records</span>
              </h3>
              <div className="divide-y divide-gray-100">
                {history.slice(0, 5).map((item, idx) => (
                  <div
                    key={item.id || idx}
                    className="py-3 flex items-center justify-between gap-4 text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">
                        {item.total_frames_analyzed} Frames • {item.overall_risk_level} Risk
                      </p>
                      <p className="text-[11px] text-gray-400 truncate max-w-xs">
                        {item.overall_summary}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setReport(item)}
                    >
                      View Report
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
