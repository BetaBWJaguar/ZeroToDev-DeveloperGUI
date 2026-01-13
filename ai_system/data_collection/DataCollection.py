from typing import Any, Dict, List, Optional, Generator, Tuple
from datetime import datetime
import json
from collections import defaultdict
import heapq

from PathHelper import PathHelper
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsManager import LogsManager


class DataCollection:
    OUTPUT_DIR_PATH = "output"
    
    TTS_EVENT_TYPES = frozenset([
        "TTS_PREVIEW_START", "TTS_PREVIEW_STOP", "PREVIEW", "CONVERT",
        "CONVERT_REQUEST", "SYNTH_DONE", "ASYNC_SYNTH_DONE",
        "CHUNK_SYNTH", "CHUNK_SPLIT"
    ])
    
    STT_VALID_ACTIONS = frozenset({"TRANSCRIPTION_COMPLETE", "TRANSCRIBE_FAIL"})
    
    LANGUAGE_CODES = frozenset(["en", "tr", "de"])
    
    def __init__(self):
        self.logger = LogsManager.get_logger("DataCollection")
        self._log_dir = PathHelper.resource_path("logs/json")
        self._log_base_name = "logs.jsonl"
        self._output_dir_path = PathHelper.resource_path(self.OUTPUT_DIR_PATH)

    def collect_tts_preferences(self) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        return {
            "tts_service": MemoryManager.get("tts_service", "edge"),
            "tts_language": MemoryManager.get("tts_lang", "en"),
            "tts_voice": MemoryManager.get("tts_voice", "female"),
            "tts_format": MemoryManager.get("tts_format", "mp3"),
            "markup_enabled": MemoryManager.get("markup_enabled", False),
            "zip_export_enabled": MemoryManager.get("zip_export_enabled", False),
            "collected_at": timestamp
        }

    def collect_stt_preferences(self) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        return {
            "stt_model": MemoryManager.get("stt_model", "vosk"),
            "stt_language": MemoryManager.get("stt_lang", "en"),
            "stt_device": MemoryManager.get("stt_device", "cpu"),
            "collected_at": timestamp
        }

    def collect_output_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self._output_dir_path.exists():
            return []

        files = []
        for file_path in self._output_dir_path.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        if limit >= len(files):
            return sorted(files, key=lambda x: x["created_at"], reverse=True)
        
        return heapq.nlargest(limit, files, key=lambda x: x["created_at"])

    def collect_tts_usage_from_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        log_files = self._get_log_files()
        if not log_files:
            return []

        tts_events = []
        
        for log_entry, parsed in self._read_log_entries(limit):
            event_type = parsed.get("event")
            if event_type in self.TTS_EVENT_TYPES:
                tts_events.append({
                    "timestamp": log_entry.get("timestamp"),
                    "source": log_entry.get("name"),
                    "event": event_type,
                    "data": parsed.get("data", {}),
                    "level": log_entry.get("level")
                })
                if len(tts_events) >= limit:
                    break

        return tts_events

    def collect_stt_usage_from_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        log_files = self._get_log_files()
        if not log_files:
            return []

        stt_events = []
        
        for log_entry, parsed in self._read_log_entries(limit):
            event_type = parsed.get("event")
            data = parsed.get("data", {})
            
            final_event = self._get_stt_event(event_type, data)
            if final_event:
                stt_events.append({
                    "timestamp": log_entry.get("timestamp"),
                    "source": log_entry.get("name"),
                    "event": final_event,
                    "data": data,
                    "level": log_entry.get("level"),
                })
                if len(stt_events) >= limit:
                    break

        return stt_events



    def collect_usage_statistics(self) -> Dict[str, Any]:
        tts_logs = self.collect_tts_usage_from_logs(limit=1000)
        stt_logs = self.collect_stt_usage_from_logs(limit=1000)
        output_files = self.collect_output_files(limit=1000)

        tts_event_counts = self._count_tts_events(tts_logs)
        stt_event_counts = self._count_stt_events(stt_logs)
        format_counts, total_output_size = self._analyze_output_files(output_files)

        return {
            "tts": {
                "total_events": len(tts_logs),
                "preview_count": tts_event_counts["preview"],
                "convert_count": tts_event_counts["convert"],
                "failure_count": tts_event_counts["failure"],
                "success_rate": round(
                    (tts_event_counts["convert"] / max(len(tts_logs), 1)) * 100,
                    2
                )
            },
            "stt": {
                "total_events": len(stt_logs),
                "transcribe_count": stt_event_counts["transcribe"],
                "failure_count": stt_event_counts["failure"]
            },
            "output": {
                "total_files": len(output_files),
                "total_size_bytes": total_output_size,
                "format_distribution": dict(format_counts)
            },
            "collected_at": datetime.utcnow().isoformat()
        }

    def collect_user_behavior_for_recommendation(self) -> Dict[str, Any]:
        tts_prefs = self.collect_tts_preferences()
        stt_prefs = self.collect_stt_preferences()
        stats = self.collect_usage_statistics()

        return {
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
        service_usage = defaultdict(int)
        language_usage = defaultdict(int)
        format_usage = defaultdict(int)

        log_files = self._get_log_files()
        if not log_files:
            return {
                "tts_service_usage": {},
                "language_usage": {},
                "output_format_usage": {},
                "total_output_files": 0,
                "collected_at": datetime.utcnow().isoformat()
            }

        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            msg = log_entry.get("message", "")

                            self._analyze_message_for_service(msg, service_usage)
                            self._analyze_message_for_language(msg, language_usage)

                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.error(
                    f"Failed to analyze system logs {log_file}: {e}"
                )

        if self._output_dir_path.exists():
            for file_path in self._output_dir_path.glob("*"):
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

    def _read_log_entries(
            self,
            limit: int
    ) -> Generator[Tuple[Dict[str, Any], Dict[str, Any]], None, None]:
        count = 0

        for log_file in self._get_log_files():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in reversed(list(f)):
                        if count >= limit:
                            return
                        try:
                            log_entry = json.loads(line.strip())
                            raw_message = log_entry.get("message")

                            if not raw_message or not raw_message.startswith("{"):
                                continue

                            parsed = json.loads(raw_message)
                            yield log_entry, parsed
                            count += 1

                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.error(f"Failed to read log file {log_file}: {e}")

    def _get_log_files(self) -> List:
        if not self._log_dir.exists():
            return []

        return sorted(
            self._log_dir.glob(self._log_base_name + "*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )


    def _get_stt_event(self, event_type: Optional[str], data: Dict[str, Any]) -> Optional[str]:
        if event_type == "SUCCESS":
            action = data.get("action")
            if action in self.STT_VALID_ACTIONS:
                return action
        elif event_type == "TRANSCRIBE_FAIL":
            return event_type
        return None

    def _count_tts_events(self, tts_logs: List[Dict[str, Any]]) -> Dict[str, int]:
        preview_events = {"PREVIEW_REQUEST", "TTS_PREVIEW_START"}
        convert_events = {"CONVERT_REQUEST", "CONVERT_DONE", "SUCCESS"}
        fail_events = {"ERROR", "CONVERT_FAIL"}
        
        counts = {"preview": 0, "convert": 0, "failure": 0}
        
        for log in tts_logs:
            event = log.get("event")
            if event in preview_events:
                counts["preview"] += 1
            elif event in convert_events:
                counts["convert"] += 1
            elif event in fail_events:
                counts["failure"] += 1
        
        return counts

    def _count_stt_events(self, stt_logs: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {"transcribe": 0, "failure": 0}
        
        for log in stt_logs:
            event = log.get("event")
            if event == "TRANSCRIPTION_COMPLETE":
                counts["transcribe"] += 1
            elif event == "TRANSCRIBE_FAIL":
                counts["failure"] += 1
        
        return counts

    def _analyze_output_files(self, output_files: List[Dict[str, Any]]) -> Tuple[defaultdict, int]:
        format_counts = defaultdict(int)
        total_size = 0
        
        for file in output_files:
            ext = file.get("extension")
            if ext:
                format_counts[ext] += 1
            total_size += file.get("size_bytes", 0)
        
        return format_counts, total_size

    def _analyze_message_for_service(self, msg: str, service_usage: defaultdict) -> None:
        if "service" in msg:
            msg_lower = msg.lower()
            if "edge" in msg_lower:
                service_usage["edge"] += 1
            elif "google" in msg_lower:
                service_usage["google"] += 1

    def _analyze_message_for_language(self, msg: str, language_usage: defaultdict) -> None:
        if "lang" in msg.lower():
            for lang_code in self.LANGUAGE_CODES:
                if lang_code in msg:
                    language_usage[lang_code] += 1

    @staticmethod
    def _get_preferred_format(format_dist: Dict[str, int]) -> Optional[str]:
        if not format_dist:
            return None
        return max(format_dist.items(), key=lambda x: x[1])[0]

    @staticmethod
    def _get_last_activity(timestamp: Optional[str]) -> Optional[str]:
        return timestamp
