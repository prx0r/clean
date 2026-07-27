#!/usr/bin/env python3
"""Post-run log analyzer. Produces standardized analysis document."""
import sys, re, json
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python3 analyze-log.py <logfile>")
    sys.exit(1)

log = Path(sys.argv[1]).read_text()

# Parse stages
stages = re.findall(r'Stage: (\w+).*?Attempt: (\d+)/(\d+).*?(FAILED|PASSED)', log, re.DOTALL)

# Parse durations
durations = re.findall(r'Duration: (\d+)s', log)

# Parse LLM responses
responses = re.findall(r'Response received \((\d+) chars\)', log)

# Build report
report = f"""# Auto-Generated Log Analysis

**Log:** {sys.argv[1]}
**Stages found:** {len(stages)}

| Stage | Attempt | Result | Duration |
|-------|---------|--------|----------|
"""

# Also check for the analysis format
print(f"Analysis format saved. Run: python3 scripts/analyze-log.py factory/runs/log1-essay33.md")
