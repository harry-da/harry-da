#!/usr/bin/env python3
"""
Quick Job Search Helper
Provides easy access to your personalized job database with filtering and analysis
"""

import csv
import argparse
from pathlib import Path
import re

def load_jobs_from_csv(csv_file):
    """Load jobs from a CSV file"""
    jobs = []
    if Path(csv_file).exists():
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('title') and row.get('company'):  # Skip empty rows
                    jobs.append(row)
    return jobs

def filter_jobs(jobs, salary_min=None, location_filter=None, company_filter=None):
    """Filter jobs based on criteria"""
    filtered = []
    
    for job in jobs:
        # Salary filtering
        if salary_min:
            salary_str = job.get('salary', '').lower()
            # Extract numbers from salary string
            numbers = re.findall(r'[\d,]+', salary_str)
            if numbers:
                # Get the first number (usually the minimum)
                salary_value = int(numbers[0].replace(',', ''))
                if '$' in salary_str and salary_value < salary_min:
                    continue
        
        # Location filtering
        if location_filter and location_filter.lower() not in job.get('location', '').lower():
            continue
            
        # Company filtering
        if company_filter and company_filter.lower() not in job.get('company', '').lower():
            continue
            
        filtered.append(job)
    
    return filtered

def display_job_summary(jobs):
    """Display a summary of jobs"""
    print(f"\n📊 Found {len(jobs)} matching opportunities:\n")
    print(f"{'Title':<40} {'Company':<20} {'Location':<25} {'Salary':<20}")
    print("-" * 105)
    
    for job in jobs:
        title = job.get('title', 'N/A')[:38]
        company = job.get('company', 'N/A')[:18]
        location = job.get('location', 'N/A')[:23]
        salary = job.get('salary', 'N/A')[:18]
        
        print(f"{title:<40} {company:<20} {location:<25} {salary:<20}")

def display_job_details(job):
    """Display detailed job information"""
    print(f"\n🎯 {job.get('title', 'N/A')}")
    print(f"🏢 Company: {job.get('company', 'N/A')} ({job.get('company_size', 'N/A')} employees)")
    print(f"📍 Location: {job.get('location', 'N/A')}")
    print(f"💰 Salary: {job.get('salary', 'N/A')}")
    print(f"📅 Posted: {job.get('posted_date', 'N/A')}")
    print(f"🔗 URL: {job.get('url', 'N/A')}")
    print(f"📝 Description: {job.get('description', 'N/A')}")
    print("-" * 80)

def analyze_market_data(all_jobs):
    """Provide market analysis of available jobs"""
    print("\n📈 MARKET ANALYSIS")
    print("=" * 50)
    
    # Company analysis
    companies = {}
    locations = {}
    salary_ranges = []
    
    for job in all_jobs:
        # Count companies
        company = job.get('company', 'Unknown')
        companies[company] = companies.get(company, 0) + 1
        
        # Count locations
        location = job.get('location', 'Unknown')
        locations[location] = locations.get(location, 0) + 1
        
        # Collect salary data
        salary_str = job.get('salary', '')
        if '$' in salary_str and salary_str.lower() != 'no salary listed':
            salary_ranges.append(salary_str)
    
    # Top companies
    print(f"\n🏆 Top Companies ({len(companies)} total):")
    top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
    for company, count in top_companies:
        print(f"  {company}: {count} positions")
    
    # Top locations
    print(f"\n🌍 Top Locations ({len(locations)} total):")
    top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
    for location, count in top_locations:
        print(f"  {location}: {count} positions")
    
    # Salary insights
    print(f"\n💰 Salary Information ({len(salary_ranges)} with salary data):")
    remote_count = len([j for j in all_jobs if 'remote' in j.get('location', '').lower()])
    print(f"  Remote positions: {remote_count} ({remote_count/len(all_jobs)*100:.1f}%)")
    
    # High-paying opportunities
    high_pay_jobs = []
    for job in all_jobs:
        salary = job.get('salary', '').lower()
        if any(term in salary for term in ['150', '160', '170', '180', '190', '200']):
            high_pay_jobs.append(job)
    
    if high_pay_jobs:
        print(f"\n💎 High-Paying Opportunities (${150}k+): {len(high_pay_jobs)} positions")
        for job in high_pay_jobs[:3]:  # Show top 3
            print(f"  • {job.get('title', 'N/A')} at {job.get('company', 'N/A')} - {job.get('salary', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(description='Job Search Helper - Access your personalized job database')
    parser.add_argument('--category', choices=[
        'senior_software_engineer_australia_singapore',
        'remote_senior_software_engineer_priority_apac_emea', 
        'software_developer_remote_global',
        'backend_engineer_remote_europe',
        'full_stack_engineer_us_canada',
        'devops_engineer_remote_europe',
        'product_manager_remote_global',
        'remote_senior_designer_apac_emea',
        'all'
    ], default='all', help='Job category to search')
    
    parser.add_argument('--min-salary', type=int, help='Minimum salary filter (e.g., 120000)')
    parser.add_argument('--location', help='Location filter (e.g., "remote", "europe", "australia")')
    parser.add_argument('--company', help='Company name filter')
    parser.add_argument('--detailed', action='store_true', help='Show detailed job descriptions')
    parser.add_argument('--analyze', action='store_true', help='Show market analysis')
    
    args = parser.parse_args()
    
    # Load job data
    all_jobs = []
    csv_files = []
    
    if args.category == 'all':
        csv_files = [
            'senior_software_engineer_australia_singapore.csv',
            'remote_senior_software_engineer_priority_apac_emea.csv',
            'software_developer_remote_global.csv',
            'backend_engineer_remote_europe.csv',
            'full_stack_engineer_us_canada.csv',
            'devops_engineer_remote_europe.csv',
            'product_manager_remote_global.csv',
            'remote_senior_designer_apac_emea.csv'
        ]
    else:
        csv_files = [f"{args.category}.csv"]
    
    print(f"🔍 Loading jobs from {len(csv_files)} database(s)...")
    
    for csv_file in csv_files:
        jobs = load_jobs_from_csv(csv_file)
        for job in jobs:
            job['source_file'] = csv_file
        all_jobs.extend(jobs)
    
    print(f"📊 Loaded {len(all_jobs)} total opportunities")
    
    # Apply filters
    if args.min_salary or args.location or args.company:
        filtered_jobs = filter_jobs(all_jobs, args.min_salary, args.location, args.company)
        print(f"🎯 {len(filtered_jobs)} jobs match your criteria")
        jobs_to_show = filtered_jobs
    else:
        jobs_to_show = all_jobs
    
    # Display results
    if args.analyze:
        analyze_market_data(all_jobs)
    elif args.detailed:
        print(f"\n📋 DETAILED JOB LISTINGS")
        print("=" * 50)
        for job in jobs_to_show:
            display_job_details(job)
    else:
        display_job_summary(jobs_to_show)
        
        if jobs_to_show:
            print(f"\n💡 Use --detailed flag to see full job descriptions")
            print(f"💡 Use --analyze flag to see market analysis")
    
    # Quick stats
    if not args.analyze:
        print(f"\n📈 Quick Stats:")
        remote_jobs = len([j for j in jobs_to_show if 'remote' in j.get('location', '').lower()])
        print(f"  Remote positions: {remote_jobs}/{len(jobs_to_show)} ({remote_jobs/len(jobs_to_show)*100:.1f}%)")
        
        companies = len(set(j.get('company', '') for j in jobs_to_show))
        print(f"  Unique companies: {companies}")

if __name__ == "__main__":
    main()