import json
import re

def parse_raw(raw_text):
    """
    Parses the model's raw output, expecting something like:
      Score: 83
      Threat: Unauthorized login
      Explanation: ...
    Returns structured dict.
    """
    result = {"anomaly_score": None, "threat": None, "explanation": None}
    lines = raw_text.splitlines()
    for line in lines:
        if m := re.match(r"Score\s*:\s*(\d+)", line, re.IGNORECASE):
            result["anomaly_score"] = int(m.group(1))
        elif m := re.match(r"Threat\s*:\s*(.+)", line, re.IGNORECASE):
            result["threat"] = m.group(1).strip()
        elif m := re.match(r"Explanation\s*:\s*(.+)", line, re.IGNORECASE):
            result["explanation"] = m.group(1).strip()
    return result