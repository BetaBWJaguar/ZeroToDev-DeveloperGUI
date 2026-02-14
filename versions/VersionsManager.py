class VersionManager:
    VERSION = (1, 3, 1)

    @classmethod
    def get(cls):
        return ".".join(map(str, cls.VERSION))

    @classmethod
    def get_short(cls):
        return f"{cls.VERSION[0]}.{cls.VERSION[1]}"

    @classmethod
    def get_windows(cls):
        return f"{cls.VERSION[0]}.{cls.VERSION[1]}.{cls.VERSION[2]}.0"

    @classmethod
    def get_windows_tuple(cls):
        return (*cls.VERSION, 0)

    @classmethod
    def set(cls, major, minor, patch):
        cls.VERSION = (major, minor, patch)
