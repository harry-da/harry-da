#!/bin/bash

echo "🔍 Job Hunter - Comprehensive Job Search System"
echo "=============================================="
echo ""

# Check if config exists
if [ ! -f "job_config.yaml" ]; then
    echo "❌ Configuration file not found!"
    exit 1
fi

echo "📋 Current Search Configurations:"
echo "--------------------------------"
grep ".csv:" job_config.yaml | sed 's/.csv://' | sed 's/^/  ✓ /'
echo ""

echo "🚀 Starting Parallel Job Search..."
echo "Time: $(date)"
echo ""

# Run the job hunter
python3 job_hunter.py

echo ""
echo "📊 Final Results Summary:"
echo "------------------------"
total_jobs=0
for file in *.csv; do
    if [ -f "$file" ]; then
        count=$(($(wc -l < "$file") - 1))  # Subtract header
        echo "  📄 $file: $count jobs"
        total_jobs=$((total_jobs + count))
    fi
done

echo ""
echo "🎯 Total Jobs Tracked: $total_jobs across all categories"
echo "📈 Updated Summary Report: updated_job_search_summary.md"
echo ""
echo "✅ Job search completed successfully!"
echo "⏰ Run this script daily for fresh opportunities"