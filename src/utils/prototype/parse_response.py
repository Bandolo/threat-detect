import json
import re

def parse_raw(raw_text):
    """
    Parses the model's raw output, handling various formats:
      - Score: 83 or Threat Score: 83
      - Threat: X or Threat Label: X
      - Explanation: ... or detailed explanation in paragraphs
    Returns structured dict.
    """
    result = {"anomaly_score": None, "threat": None, "explanation": None}
    
    if not raw_text:
        return result
        
    lines = raw_text.splitlines()
    explanation_lines = []
    in_explanation = False
    
    for line in lines:
        # Check for score in various formats
        if m := re.search(r"(?:Threat\s*)?Score\s*:\s*(\d+)", line, re.IGNORECASE):
            result["anomaly_score"] = int(m.group(1))
        
        # Check for threat label in various formats
        elif m := re.search(r"Threat(?:\s*Label)?\s*:\s*(.+)", line, re.IGNORECASE):
            threat = m.group(1).strip()
            # If it's just "High" or similar, we need more context
            if threat.lower() in ["high", "medium", "low"]:
                # Look for more specific threat info in the text
                for potential_line in lines:
                    if "malware" in potential_line.lower():
                        result["threat"] = "Malware Execution"
                        break
                    elif "brute force" in potential_line.lower():
                        result["threat"] = "SSH Brute Force Attack"
                        break
                    elif "reconnaissance" in potential_line.lower():
                        result["threat"] = "Reconnaissance Activity"
                        break
                # If we still don't have a threat type, use the severity
                if not result["threat"]:
                    result["threat"] = f"{threat} Severity Threat"
            else:
                result["threat"] = threat
        
        # Check for explanation
        elif m := re.search(r"Explanation\s*:\s*(.+)", line, re.IGNORECASE):
            explanation_lines.append(m.group(1).strip())
            in_explanation = True
        
        # If we're in the explanation section, collect all lines
        elif in_explanation and line.strip():
            explanation_lines.append(line.strip())
    
    # If we found explanation lines, join them
    if explanation_lines:
        result["explanation"] = " ".join(explanation_lines)
    
    # If we still don't have an explanation, look for paragraphs in the text
    if not result["explanation"]:
        paragraphs = []
        current_paragraph = []
        for line in lines:
            if not line.strip():
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
            else:
                # Skip lines that are likely headers
                if not re.match(r"^[A-Za-z\s]+:\s*", line):
                    current_paragraph.append(line.strip())
        
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        
        if paragraphs:
            # Use the longest paragraph as the explanation
            result["explanation"] = max(paragraphs, key=len)
    
    return result