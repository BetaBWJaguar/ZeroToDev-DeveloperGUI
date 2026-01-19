import threading
import time

from ai_system.data_collection.DataCollectionManager import DataCollectionManager
from ai_system.data_collection.DataCollectionDatabaseManager import DataCollectionDatabaseManager
from logs_manager.LogsHelperManager import LogsHelperManager


class SnapshotService:
    _thread = None
    _running = False
    _user = None
    _logger = None
    _interval = 15

    @classmethod
    def start(cls, user, logger, interval=15):
        if cls._running:
            return

        cls._user = user
        cls._logger = logger
        cls._interval = interval
        cls._running = True

        cls._thread = threading.Thread(
            target=cls._loop,
            daemon=True
        )
        cls._thread.start()

        LogsHelperManager.log_success(
            logger,
            "SNAPSHOT_SERVICE_STARTED",
            {"user": user.username}
        )

    @classmethod
    def stop(cls):
        cls._running = False

        if cls._logger:
            LogsHelperManager.log_success(
                cls._logger,
                "SNAPSHOT_SERVICE_STOPPED"
            )

    @classmethod
    def _loop(cls):
        while cls._running:
            try:
                runtime_collector = DataCollectionManager()
                db_collector = DataCollectionDatabaseManager()

                payload = {
                    "preferences": {
                        "tts": runtime_collector.get_tts_preferences(),
                        "stt": runtime_collector.get_stt_preferences()
                    },
                    "usage_statistics": runtime_collector.get_usage_statistics(),
                    "behavior": runtime_collector.get_behavior_for_ai(),
                    "system_usage": runtime_collector.get_system_usage_data(),
                    "output_files": runtime_collector.get_output_files(limit=1000)
                }

                user_id = (
                    cls._user.id.get("id")
                    if isinstance(cls._user.id, dict)
                    else cls._user.id
                )

                db_collector.collect_and_save_user_data(user_id, payload)

                LogsHelperManager.log_success(
                    cls._logger,
                    "USER_SNAPSHOT_BACKGROUND_SAVED",
                    {"user": cls._user.username}
                )

            except Exception as e:
                LogsHelperManager.log_error(
                    cls._logger,
                    "USER_SNAPSHOT_BACKGROUND_FAILED",
                    str(e)
                )

            time.sleep(cls._interval)
