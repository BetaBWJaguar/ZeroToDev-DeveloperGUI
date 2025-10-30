# -*- coding: utf-8 -*-
import gc
import os
import sys
import time
import psutil
import threading
import tempfile
import shutil
import atexit


class StartupOptimizer:
    _instance = None

    def __init__(self):
        self.start_time = time.time()
        self.temp_prefix = "zerotodev_"
        self.register_cleanup_hooks()

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def lazy_import(self, module_name: str):
        if module_name in sys.modules:
            return sys.modules[module_name]
        module = __import__(module_name)
        sys.modules[module_name] = module
        return module

    def run_in_background(self, func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    def log_startup_time(self):
        elapsed = round(time.time() - self.start_time, 3)
        print(f"✅ Startup completed in {elapsed} seconds")


    def cleanup_memory(self):
        try:
            gc.collect()
        except Exception as e:
            print(f"[WARN] GC cleanup failed: {e}")

    def clear_temp_files(self):
        temp_dir = tempfile.gettempdir()
        for item in os.listdir(temp_dir):
            if item.startswith(self.temp_prefix):
                try:
                    shutil.rmtree(os.path.join(temp_dir, item), ignore_errors=True)
                except Exception:
                    pass

    def kill_orphan_processes(self):
        for proc in psutil.process_iter(['name']):
            try:
                if "ffmpeg" in proc.info['name'].lower():
                    proc.kill()
            except Exception:
                pass

    def register_cleanup_hooks(self):
        atexit.register(self.cleanup_memory)
        atexit.register(self.clear_temp_files)
        atexit.register(self.kill_orphan_processes)


    @staticmethod
    def get_memory_usage_mb():
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / 1024 / 1024, 2)

    def print_memory_usage(self):
        mem = self.get_memory_usage_mb()
        print(f"💾 Current memory usage: {mem} MB")
