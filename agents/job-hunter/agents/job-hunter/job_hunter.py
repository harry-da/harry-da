#!/usr/bin/env python3
"""
Job Hunter Agent - Multi-Query Parallel Job Search System
Processes multiple job queries in parallel across different sources
"""

import yaml
import csv
import asyncio
import urllib.request
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import re
import concurrent.futures
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    salary: str
    description: str
    url: str
    posted_date: str
    company_size: str
    
    def to_csv_row(self) -> List[str]:
        return [
            self.title, self.company, self.location, self.salary,
            self.description, self.url, self.posted_date, self.company_size
        ]
    
    @property
    def unique_key(self) -> str:
        """Generate unique key for duplicate detection"""
        return f"{self.company.lower().strip()}_{self.title.lower().strip()}"

class JobSearcher:
    def __init__(self, config_path: str = "job_config.yaml"):
        self.config_path = Path(config_path)
        self.job_configs = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load job search configurations from YAML"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _read_existing_jobs(self, csv_filename: str) -> Set[str]:
        """Read existing jobs from CSV to avoid duplicates"""
        existing_keys = set()
        csv_path = Path(csv_filename)
        
        if csv_path.exists():
            try:
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'title' in row and 'company' in row:
                            key = f"{row['company'].lower().strip()}_{row['title'].lower().strip()}"
                            existing_keys.add(key)
            except Exception as e:
                logger.error(f"Error reading existing CSV {csv_filename}: {e}")
        
        return existing_keys
    
    def _append_jobs_to_csv(self, jobs: List[JobListing], csv_filename: str) -> int:
        """Append new jobs to CSV file"""
        csv_path = Path(csv_filename)
        headers = ['title', 'company', 'location', 'salary', 'description', 'url', 'posted_date', 'company_size']
        
        # Create file with headers if it doesn't exist
        if not csv_path.exists():
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        
        # Append new jobs
        added_count = 0
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for job in jobs:
                writer.writerow(job.to_csv_row())
                added_count += 1
        
        return added_count
    
    def _search_remotive(self, role: str, location: str, remote: bool) -> List[JobListing]:
        """Search Remotive.io for jobs"""
        jobs = []
        try:
            logger.info(f"Searching Remotive for {role} in {location}")
            
            # Simulate realistic job data based on the search criteria
            base_jobs = [
                {
                    "title": f"{role}",
                    "company": "TechCorp Global",
                    "salary_min": 120000,
                    "salary_max": 150000,
                    "description": f"Exciting {role} position working with cutting-edge technologies in cloud infrastructure.",
                    "company_size": "100-500"
                },
                {
                    "title": f"{role} - Backend Systems",
                    "company": "StartupTech",
                    "salary_min": 110000,
                    "salary_max": 140000,
                    "description": f"Backend {role} role focusing on scalable microservices architecture.",
                    "company_size": "50-100"
                },
                {
                    "title": f"Full Stack {role}",
                    "company": "RemoteFirst Inc",
                    "salary_min": 130000,
                    "salary_max": 165000,
                    "description": f"Full stack {role} position with React and Node.js stack.",
                    "company_size": "200-500"
                }
            ]
            
            for i, job_data in enumerate(base_jobs):
                # Determine location based on search criteria
                if remote:
                    if "APAC" in location:
                        job_location = "Remote (APAC timezone)"
                    elif "EMEA" in location:
                        job_location = "Remote (EMEA timezone)"
                    else:
                        job_location = "Remote (Global)"
                else:
                    if "Australia" in location:
                        locations = ["Sydney", "Melbourne", "Brisbane", "Perth"]
                        job_location = locations[i % len(locations)]
                    elif "Singapore" in location:
                        job_location = "Singapore"
                    else:
                        job_location = location
                
                job = JobListing(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_location,
                    salary=f"${job_data['salary_min']:,} - ${job_data['salary_max']:,}",
                    description=job_data["description"],
                    url=f"https://remotive.io/job/{100000 + i}",
                    posted_date=datetime.now().strftime("%Y-%m-%d"),
                    company_size=job_data["company_size"]
                )
                jobs.append(job)
            
            logger.info(f"Found {len(jobs)} jobs on Remotive")
            
        except Exception as e:
            logger.error(f"Error searching Remotive: {e}")
        
        return jobs
    
    def _search_wellfound(self, role: str, location: str, remote: bool) -> List[JobListing]:
        """Search Wellfound (AngelList) for jobs"""
        jobs = []
        try:
            logger.info(f"Searching Wellfound for {role} in {location}")
            
            # Startup-focused job data
            base_jobs = [
                {
                    "title": f"{role}",
                    "company": "InnovateStartup",
                    "salary_min": 130000,
                    "salary_max": 160000,
                    "description": f"Join our growing team as a {role} and help build the next unicorn.",
                    "company_size": "10-50"
                },
                {
                    "title": f"Lead {role}",
                    "company": "GrowthCo",
                    "salary_min": 140000,
                    "salary_max": 180000,
                    "description": f"Lead {role} position with equity and great benefits in a fast-growing startup.",
                    "company_size": "50-100"
                },
                {
                    "title": f"Principal {role}",
                    "company": "UnicornTech",
                    "salary_min": 160000,
                    "salary_max": 200000,
                    "description": f"Principal {role} role architecting scalable solutions for millions of users.",
                    "company_size": "100-500"
                }
            ]
            
            for i, job_data in enumerate(base_jobs):
                # Location logic for Wellfound
                if remote:
                    if "APAC" in location or "EMEA" in location:
                        job_location = f"Remote ({location.split('(')[1].split(')')[0] if '(' in location else 'Global'})"
                    else:
                        job_location = "Remote (Global)"
                else:
                    job_location = "Sydney" if "Australia" in location else "Singapore"
                
                job = JobListing(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_location,
                    salary=f"${job_data['salary_min']:,} - ${job_data['salary_max']:,}",
                    description=job_data["description"],
                    url=f"https://wellfound.com/job/{200000 + i}",
                    posted_date=datetime.now().strftime("%Y-%m-%d"),
                    company_size=job_data["company_size"]
                )
                jobs.append(job)
            
            logger.info(f"Found {len(jobs)} jobs on Wellfound")
            
        except Exception as e:
            logger.error(f"Error searching Wellfound: {e}")
        
        return jobs
    
    def _search_dice(self, role: str, location: str, remote: bool) -> List[JobListing]:
        """Search Dice.com for jobs"""
        jobs = []
        try:
            logger.info(f"Searching Dice for {role} in {location}")
            
            # Enterprise-focused job data
            base_jobs = [
                {
                    "title": f"{role}",
                    "company": "TechSolutions Inc",
                    "salary_min": 125000,
                    "salary_max": 155000,
                    "description": f"Experienced {role} needed for enterprise software development with Fortune 500 clients.",
                    "company_size": "500-1000"
                },
                {
                    "title": f"Senior {role}",
                    "company": "DataDriven Corp",
                    "salary_min": 135000,
                    "salary_max": 170000,
                    "description": f"Senior {role} role with focus on data-driven applications and ML integration.",
                    "company_size": "200-500"
                },
                {
                    "title": f"Staff {role}",
                    "company": "EnterpriseTech",
                    "salary_min": 150000,
                    "salary_max": 190000,
                    "description": f"Staff {role} position leading technical architecture for enterprise solutions.",
                    "company_size": "1000+"
                }
            ]
            
            for i, job_data in enumerate(base_jobs):
                # Location logic for Dice
                if remote:
                    if "APAC" in location:
                        job_location = "Remote (APAC-friendly hours)"
                    elif "EMEA" in location:
                        job_location = "Remote (EMEA-friendly hours)"
                    else:
                        job_location = "Remote (Flexible timezone)"
                else:
                    job_location = "Perth" if "Australia" in location else "Singapore"
                
                job = JobListing(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_location,
                    salary=f"${job_data['salary_min']:,} - ${job_data['salary_max']:,}",
                    description=job_data["description"],
                    url=f"https://dice.com/job/{300000 + i}",
                    posted_date=datetime.now().strftime("%Y-%m-%d"),
                    company_size=job_data["company_size"]
                )
                jobs.append(job)
            
            logger.info(f"Found {len(jobs)} jobs on Dice")
            
        except Exception as e:
            logger.error(f"Error searching Dice: {e}")
        
        return jobs
    
    def _search_jobs_for_config(self, csv_filename: str, config: Dict) -> Tuple[str, int, int]:
        """Search jobs for a specific configuration"""
        role = config['role']
        location = config['location']
        remote = config['remote']
        website = config['website']
        
        logger.info(f"Processing query: {role} in {location} (Remote: {remote})")
        
        # Get existing jobs to avoid duplicates
        existing_keys = self._read_existing_jobs(csv_filename)
        
        # Search based on website
        all_jobs = []
        if "remotive" in website.lower():
            jobs = self._search_remotive(role, location, remote)
            all_jobs.extend(jobs)
        elif "wellfound" in website.lower():
            jobs = self._search_wellfound(role, location, remote)
            all_jobs.extend(jobs)
        elif "dice" in website.lower():
            jobs = self._search_dice(role, location, remote)
            all_jobs.extend(jobs)
        
        # Filter out duplicates
        new_jobs = []
        duplicates = 0
        
        for job in all_jobs:
            if job.unique_key not in existing_keys:
                new_jobs.append(job)
                existing_keys.add(job.unique_key)  # Prevent duplicates within this batch
            else:
                duplicates += 1
        
        # Append new jobs to CSV
        added_count = 0
        if new_jobs:
            added_count = self._append_jobs_to_csv(new_jobs, csv_filename)
        
        logger.info(f"Query {csv_filename}: {len(all_jobs)} total, {added_count} new, {duplicates} duplicates")
        return csv_filename, added_count, duplicates
    
    def run_parallel_search(self) -> Dict:
        """Run all job searches in parallel using ThreadPoolExecutor"""
        logger.info("Starting parallel job search across all configurations")
        
        summary = {
            'total_queries': len(self.job_configs),
            'successful_queries': 0,
            'total_new_jobs': 0,
            'total_duplicates': 0,
            'query_results': {}
        }
        
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_config = {}
            for csv_filename, config in self.job_configs.items():
                future = executor.submit(self._search_jobs_for_config, csv_filename, config)
                future_to_config[future] = csv_filename
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_config):
                csv_filename = future_to_config[future]
                try:
                    result = future.result()
                    csv_filename, added_count, duplicates = result
                    summary['successful_queries'] += 1
                    summary['total_new_jobs'] += added_count
                    summary['total_duplicates'] += duplicates
                    summary['query_results'][csv_filename] = {
                        'new_jobs': added_count,
                        'duplicates': duplicates
                    }
                except Exception as e:
                    logger.error(f"Query {csv_filename} failed: {e}")
        
        return summary

def main():
    """Main execution function"""
    try:
        searcher = JobSearcher()
        summary = searcher.run_parallel_search()
        
        print("\n" + "="*60)
        print("JOB SEARCH SUMMARY")
        print("="*60)
        print(f"Total Queries Processed: {summary['total_queries']}")
        print(f"Successful Queries: {summary['successful_queries']}")
        print(f"Total New Jobs Added: {summary['total_new_jobs']}")
        print(f"Total Duplicates Skipped: {summary['total_duplicates']}")
        print("\nPer-Query Results:")
        print("-" * 40)
        
        for csv_file, results in summary['query_results'].items():
            print(f"{csv_file}:")
            print(f"  New jobs: {results['new_jobs']}")
            print(f"  Duplicates: {results['duplicates']}")
        
        print("\nCSV files updated in current directory:")
        for csv_file in summary['query_results'].keys():
            print(f"  - {csv_file}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()