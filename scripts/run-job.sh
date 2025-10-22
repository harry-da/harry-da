#!/bin/bash
set -e

# Script to run opencode agent jobs
# Usage: ./run-job.sh <job-id>

if [ -z "$1" ]; then
  echo "Error: Job ID is required"
  echo "Usage: $0 <job-id>"
  exit 1
fi

JOB_ID="$1"
JOB_DIR="jobs/${JOB_ID}"
AGENT_FILE="${JOB_DIR}/agent.md"
RESULTS_DIR="${JOB_DIR}/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${RESULTS_DIR}/result_${TIMESTAMP}.md"
WORKDIR=$(mktemp -d)

# Check if agent file exists
if [ ! -f "$AGENT_FILE" ]; then
  echo "Error: Agent file not found at $AGENT_FILE"
  exit 1
fi

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "Running job: ${JOB_ID}"
echo "Agent file: ${AGENT_FILE}"
echo "Output file: ${OUTPUT_FILE}"
echo "Work directory: ${WORKDIR}"
echo "============================================"
echo ""

# Copy agent file to opencode agent directory
mkdir -p ~/.config/opencode/agent
cp "$AGENT_FILE" ~/.config/opencode/agent/"${JOB_ID}.md"

echo "Copied agent to ~/.config/opencode/agent/${JOB_ID}.md"
echo ""

# Change to empty work directory and run opencode
cd "$WORKDIR"
echo "Running: opencode run @${JOB_ID}"
echo ""

# Run opencode
if opencode run "@${JOB_ID}" > "${OUTPUT_FILE}" 2>&1; then
  echo "OpenCode execution completed successfully"
else
  echo "OpenCode execution failed"
  cat "${OUTPUT_FILE}"
fi

# Clean up work directory
cd -
rm -rf "$WORKDIR"

echo ""
echo "Job completed!"
echo "Results saved to: $OUTPUT_FILE"

# Keep only the last 10 results to avoid repository bloat
cd "$RESULTS_DIR"
ls -t result_*.md 2>/dev/null | tail -n +11 | xargs -r rm --
echo "Cleaned up old results (keeping last 10)"
