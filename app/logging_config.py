import logging, sys, json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        for k in ("user_id","request_id","duration_ms","status_code","path","method","client","error"):
            if hasattr(record, k): data[k] = getattr(record, k)
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data)

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    return root

logger = setup_logging()
