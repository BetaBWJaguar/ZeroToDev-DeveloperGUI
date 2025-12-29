from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict

from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager


class DataCollection:
    def __init__(self):
        self.logger = LogsManager.get_logger("DataCollection")

    def collect_tts_preferences(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "tts_service": MemoryManager.get("tts_service", "edge"),
            "tts_language": MemoryManager.get("tts_lang", "en"),
            "tts_voice": MemoryManager.get("tts_voice", "female"),
            "tts_format": MemoryManager.get("tts_format", "mp3"),
            "markup_enabled": MemoryManager.get("markup_enabled", False),
            "zip_export_enabled": MemoryManager.get("zip_export_enabled", False),
            "collected_at": datetime.utcnow().isoformat()
        }

    def collect_stt_preferences(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "stt_model": MemoryManager.get("stt_model", "vosk"),
            "stt_language": MemoryManager.get("stt_lang", "en"),
            "stt_device": MemoryManager.get("stt_device", "cpu"),
            "collected_at": datetime.utcnow().isoformat()
        }

    def collect_output_files(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        output_dir = PathHelper.resource_path("output")
        if not output_dir.exists():
            return []

        files = []
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "user_id": user_id,
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return sorted(files, key=lambda x: x["created_at"], reverse=True)[:limit]

    def collect_tts_usage_from_logs(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        log_file = PathHelper.resource_path("logs/json/logs.jsonl")
        if not log_file.exists():
            return []

        tts_events = []
        tts_event_types = [
            "TTS_PREVIEW_START", "TTS_PREVIEW_STOP", "PREVIEW", "CONVERT",
            "CONVERT_REQUEST", "SYNTH_DONE", "ASYNC_SYNTH_DONE",
            "CHUNK_SYNTH", "CHUNK_SPLIT"
        ]

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if len(tts_events) >= limit:
                        break
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get("name") == "MicrosoftEdgeTTSService":
                            event = log_entry.get("message", "")
                            if any(evt in event for evt in tts_event_types):
                                tts_events.append({
                                    "user_id": user_id,
                                    "timestamp": log_entry.get("timestamp"),
                                    "event": log_entry.get("name"),
                                    "message": event,
                                    "level": log_entry.get("level")
                                })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to read logs: {e}")

        return tts_events

    def collect_stt_usage_from_logs(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        log_file = PathHelper.resource_path("logs/json/logs.jsonl")
        if not log_file.exists():
            return []

        stt_events = []
        stt_event_types = [
            "STT_LOAD", "STT_TRANSCRIBE", "STT_UNLOAD",
            "TRANSCRIBE_START", "TRANSCRIBE_DONE", "TRANSCRIBE_FAIL"
        ]

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if len(stt_events) >= limit:
                        break
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get("name") in ["VoskSTT", "WhisperSTT", "STTEngine"]:
                            event = log_entry.get("message", "")
                            if any(evt in event for evt in stt_event_types):
                                stt_events.append({
                                    "user_id": user_id,
                                    "timestamp": log_entry.get("timestamp"),
                                    "event": log_entry.get("name"),
                                    "message": event,
                                    "level": log_entry.get("level")
                                })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to read logs: {e}")

        return stt_events

    def collect_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        tts_logs = self.collect_tts_usage_from_logs(user_id, limit=1000)
        stt_logs = self.collect_stt_usage_from_logs(user_id, limit=1000)
        output_files = self.collect_output_files(user_id, limit=1000)

        tts_preview_count = sum(1 for log in tts_logs if "PREVIEW" in log["message"])
        tts_convert_count = sum(1 for log in tts_logs if "CONVERT" in log["message"] and "CONVERT_FAIL" not in log["message"])
        tts_fail_count = sum(1 for log in tts_logs if "FAIL" in log["message"])

        format_counts = defaultdict(int)
        for file in output_files:
            format_counts[file["extension"]] += 1

        total_output_size = sum(f["size_bytes"] for f in output_files)

        return {
            "user_id": user_id,
            "tts": {
                "total_events": len(tts_logs),
                "preview_count": tts_preview_count,
                "convert_count": tts_convert_count,
                "failure_count": tts_fail_count,
                "success_rate": round((tts_convert_count / max(len(tts_logs), 1)) * 100, 2)
            },
            "stt": {
                "total_events": len(stt_logs),
                "transcribe_count": sum(1 for log in stt_logs if "TRANSCRIBE" in log["message"]),
                "failure_count": sum(1 for log in stt_logs if "FAIL" in log["message"])
            },
            "output": {
                "total_files": len(output_files),
                "total_size_bytes": total_output_size,
                "format_distribution": dict(format_counts)
            },
            "collected_at": datetime.utcnow().isoformat()
        }

    def collect_user_behavior_for_recommendation(self, user_id: str) -> Dict[str, Any]:
        tts_prefs = self.collect_tts_preferences(user_id)
        stt_prefs = self.collect_stt_preferences(user_id)
        stats = self.collect_usage_statistics(user_id)

        return {
            "user_id": user_id,
            "tts_preferences": {
                "service": tts_prefs.get("tts_service"),
                "language": tts_prefs.get("tts_language"),
                "voice": tts_prefs.get("tts_voice"),
                "format": tts_prefs.get("tts_format"),
                "uses_markup": tts_prefs.get("markup_enabled"),
                "uses_zip_export": tts_prefs.get("zip_export_enabled")
            },
            "stt_preferences": {
                "model": stt_prefs.get("stt_model"),
                "language": stt_prefs.get("stt_language"),
                "device": stt_prefs.get("stt_device")
            },
            "usage_patterns": {
                "tts_frequency": stats["tts"]["total_events"],
                "tts_success_rate": stats["tts"]["success_rate"],
                "tts_preview_ratio": round(
                    stats["tts"]["preview_count"] / max(stats["tts"]["total_events"], 1) * 100, 2
                ),
                "stt_frequency": stats["stt"]["total_events"],
                "total_output_files": stats["output"]["total_files"],
                "preferred_format": self._get_preferred_format(stats["output"]["format_distribution"])
            },
            "activity_summary": {
                "last_activity": self._get_last_activity(tts_prefs.get("collected_at")),
                "total_storage_used_bytes": stats["output"]["total_size_bytes"]
            }
        }

    def collect_system_usage_data(self) -> Dict[str, Any]:
        log_file = PathHelper.resource_path("logs/json/logs.jsonl")
        output_dir = PathHelper.resource_path("output")

        service_usage = defaultdict(int)
        language_usage = defaultdict(int)
        format_usage = defaultdict(int)

        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            msg = log_entry.get("message", "")
                            
                            # Extract service usage
                            if "service" in msg:
                                if "edge" in msg.lower():
                                    service_usage["edge"] += 1
                                elif "google" in msg.lower():
                                    service_usage["google"] += 1
                            
                            # Extract language usage
                            if "lang" in msg.lower():
                                for lang_code in ["en", "tr", "de", "es", "fr", "it"]:
                                    if lang_code in msg:
                                        language_usage[lang_code] += 1

                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.error(f"Failed to analyze system logs: {e}")


        if output_dir.exists():
            for file_path in output_dir.glob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext:
                        format_usage[ext] += 1

        return {
            "tts_service_usage": dict(service_usage),
            "language_usage": dict(language_usage),
            "output_format_usage": dict(format_usage),
            "total_output_files": sum(format_usage.values()),
            "collected_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def _get_preferred_format(format_dist: Dict[str, int]) -> Optional[str]:
        if not format_dist:
            return None
        return max(format_dist.items(), key=lambda x: x[1])[0]

    @staticmethod
    def _get_last_activity(timestamp: Optional[str]) -> Optional[str]:
        return timestamp

    def collect_all_users_behavior(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        all_data = []

        for user_id in user_ids:
            behavior = self.collect_user_behavior_for_recommendation(user_id)
            all_data.append(behavior)

        return all_data
