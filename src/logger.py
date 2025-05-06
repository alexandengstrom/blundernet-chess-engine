import datetime

class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40
    }

    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m",
    }

    _level = LEVELS["DEBUG"]

    @classmethod
    def set_level(cls, level):
        level = level.upper()
        if level not in cls.LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        cls._level = cls.LEVELS[level]

    @staticmethod
    def _log(level, message):
        if Logger.LEVELS[level] >= Logger._level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            color = Logger.COLORS.get(level, "")
            reset = Logger.COLORS["RESET"]
            print(f"{color}[{timestamp}] {level}: {message}{reset}")

    @staticmethod
    def debug(message):
        Logger._log("DEBUG", message)

    @staticmethod
    def info(message):
        Logger._log("INFO", message)

    @staticmethod
    def warning(message):
        Logger._log("WARNING", message)

    @staticmethod
    def error(message):
        Logger._log("ERROR", message)
