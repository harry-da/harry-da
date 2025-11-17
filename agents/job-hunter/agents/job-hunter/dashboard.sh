#!/bin/bash
# Job Hunter Quick Dashboard
# Run this script for instant access to your job search data

clear
echo "🚀 JOB HUNTER DASHBOARD"
echo "========================"
echo "Last Updated: $(date)"
echo ""

echo "📊 QUICK STATS:"
python3 job_search_helper.py --analyze | grep -A 10 "Quick Stats\|Top Companies\|Top Locations"

echo ""
echo "💎 HIGH-PAYING OPPORTUNITIES ($140K+):"
echo "----------------------------------------"
python3 job_search_helper.py --min-salary 140000 | grep -A 20 "Found.*matching opportunities"

echo ""
echo "🌍 REMOTE OPPORTUNITIES:"
echo "-------------------------"
python3 job_search_helper.py --location remote | grep -A 15 "Found.*matching opportunities"

echo ""
echo "🔧 AVAILABLE COMMANDS:"
echo "----------------------"
echo "• python3 job_search_helper.py --analyze          # Full market analysis"
echo "• python3 job_search_helper.py --detailed         # Detailed job listings"
echo "• python3 job_search_helper.py --min-salary 150000 # High-paying jobs"
echo "• python3 job_search_helper.py --location europe   # Location-specific"
echo "• python3 job_search_helper.py --company proxify   # Company-specific"
echo "• python3 job_hunter.py                           # Update job database"

echo ""
echo "📁 CSV FILES:"
echo "-------------"
ls -la *.csv | awk '{print "• " $9 " (" $5 " bytes, " $6 " " $7 ")"}'

echo ""
echo "🎯 QUICK ACTIONS:"
echo "-----------------"
echo "1. Run fresh job search: python3 job_hunter.py"
echo "2. View comprehensive guide: cat COMPREHENSIVE_JOB_HUNTING_GUIDE.md"
echo "3. Check high-paying jobs: python3 job_search_helper.py --min-salary 150000 --detailed"