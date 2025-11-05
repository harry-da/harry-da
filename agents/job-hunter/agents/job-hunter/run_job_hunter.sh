#!/bin/bash
# Job Hunter Agent Runner Script

echo "🔍 Starting Job Hunter Agent..."
echo "Processing multiple job queries in parallel across different sources"
echo ""

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Install required packages if needed (basic packages only)
echo "📦 Checking dependencies..."

# Run the job hunter
echo "🚀 Executing parallel job search..."
python3 job_hunter.py

echo ""
echo "✅ Job search completed!"
echo "📊 Check the generated CSV files for results"