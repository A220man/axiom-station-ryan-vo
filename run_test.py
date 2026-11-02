#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([
    sys.executable, "-m", "pytest", 
    "tests/test_contradiction_detection.py::TestContradictionEngine::test_ratio_contradiction", 
    "-v"
], cwd="/var/lib/alan-portfolio/workspaces/ryan/axiom-station-ryan-vo/backend", capture_output=True, text=True)

print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
