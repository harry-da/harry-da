# Job Hunter Agent 🔍

A sophisticated multi-query parallel job search system that processes multiple job queries simultaneously across different job boards and maintains separate CSV databases for each query combination.

## Features ✨

- **Parallel Processing**: Execute multiple job searches simultaneously across different sources
- **Dynamic Configuration**: YAML-driven query definitions with flexible parameters
- **Duplicate Prevention**: Intelligent deduplication using company + job title combinations
- **Multi-Source Support**: Remotive, Wellfound (AngelList), and Dice job boards
- **CSV Database Management**: Separate CSV files for each query with append-only operations
- **Comprehensive Logging**: Detailed progress tracking and error handling

## Architecture 🏗️

```
agents/job-hunter/
├── job_config.yaml              # Query configurations (YAML key = CSV filename)
├── job_hunter.py               # Main job search engine
├── run_job_hunter.sh          # Execution runner script
├── *.csv                      # Generated job databases (one per query)
└── README.md                  # This documentation
```

## Configuration 📝

Job searches are defined in `job_config.yaml` where each YAML key becomes the CSV filename:

```yaml
senior_software_engineer_australia_singapore.csv:
  role: "Senior Software Engineer"
  location: "Australia or Singapore"
  remote: false
  level: "senior"
  website: "https://remotive.io/remote-jobs"

remote_senior_software_engineer_priority_apac_emea.csv:
  role: "Senior Software Engineer"
  location: "Remote (priority: APAC, EMEA)"
  remote: true
  level: "senior"
  website: "https://wellfound.com/"

remote_senior_designer_apac_emea.csv:
  role: "Senior Designer"
  location: "APAC or EMEA timezones"
  remote: true
  level: "senior"
  website: "https://www.dice.com/"
```

### Configuration Parameters

- **Key**: CSV filename where results will be stored
- **role**: Job title or function to search for
- **location**: Geographic location or remote timezone preferences
- **remote**: Boolean indicating remote work preference
- **level**: Experience level (entry, mid, senior, staff, principal)
- **website**: Job board URL to search

## Usage 🚀

### Quick Start

```bash
cd agents/job-hunter
./run_job_hunter.sh
```

### Python Direct Execution

```bash
cd agents/job-hunter
python3 job_hunter.py
```

### Custom Configuration

1. Modify `job_config.yaml` with your desired job searches
2. Run the job hunter
3. Check generated CSV files for results

## Output Format 📊

Each CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| title | Job title |
| company | Company name |
| location | Job location or remote status |
| salary | Salary range (if available) |
| description | Job description summary |
| url | Application URL |
| posted_date | Date posted (YYYY-MM-DD) |
| company_size | Company size range |

## Parallel Execution Strategy 🔄

The system uses ThreadPoolExecutor for true parallel processing:

1. **Dynamic Query Discovery**: Parse YAML to identify all query combinations
2. **Query-Level Parallelism**: Execute each configured query simultaneously
3. **Source-Level Parallelism**: Search each job board concurrently
4. **Concurrent Data Processing**: Collect, filter, and append job data in parallel streams

## Job Board Sources 🌐

### Remotive.io
- **Focus**: Remote jobs across various categories
- **Specialties**: Software development, design, marketing
- **Coverage**: Global remote positions

### Wellfound (AngelList)
- **Focus**: Startup jobs in tech
- **Specialties**: Software engineering, product, growth
- **Coverage**: Startup ecosystem globally

### Dice.com
- **Focus**: Tech-specific roles
- **Specialties**: Software development, data science, cybersecurity
- **Coverage**: Primarily U.S.-based with some remote options

## Duplicate Prevention 🛡️

The system prevents duplicates using:

1. **Unique Key Generation**: `company_name + job_title` (normalized, lowercase)
2. **Pre-execution Check**: Read existing CSV data before adding new jobs
3. **Batch Deduplication**: Prevent duplicates within the same search batch
4. **Cross-Query Independence**: Each query maintains its own unique job set

## Example Output 📈

```
============================================================
JOB SEARCH SUMMARY
============================================================
Total Queries Processed: 3
Successful Queries: 3
Total New Jobs Added: 9
Total Duplicates Skipped: 0

Per-Query Results:
----------------------------------------
senior_software_engineer_australia_singapore.csv:
  New jobs: 3
  Duplicates: 0
remote_senior_software_engineer_priority_apac_emea.csv:
  New jobs: 3
  Duplicates: 0
remote_senior_designer_apac_emea.csv:
  New jobs: 3
  Duplicates: 0

CSV files updated in current directory:
  - senior_software_engineer_australia_singapore.csv
  - remote_senior_software_engineer_priority_apac_emea.csv
  - remote_senior_designer_apac_emea.csv
```

## Customization 🔧

### Adding New Job Boards

1. Create a new search method in `JobSearcher` class:
```python
def _search_newboard(self, role: str, location: str, remote: bool) -> List[JobListing]:
    # Implementation for new job board
    pass
```

2. Add logic to `_search_jobs_for_config` method:
```python
elif "newboard" in website.lower():
    jobs = self._search_newboard(role, location, remote)
    all_jobs.extend(jobs)
```

### Custom Query Parameters

Add new parameters to YAML configuration and update the search methods accordingly.

### Data Processing Extensions

Extend the `JobListing` dataclass with additional fields as needed.

## Error Handling 🚨

- **Network Issues**: Graceful handling of connection timeouts
- **Data Quality**: Validation of job data before CSV insertion  
- **File Permissions**: Proper error messages for file access issues
- **Configuration Errors**: Validation of YAML configuration format

## Performance 🚀

- **Concurrent Execution**: Multiple job searches run simultaneously
- **Memory Efficient**: Streaming data processing without loading entire datasets
- **Incremental Updates**: Only new jobs are added to CSV files
- **Fast Deduplication**: Hash-based duplicate detection

## Current Search Status 📊

The system is actively tracking **40 unique positions** across **8 categories**:

- Senior Software Engineer (Australia/Singapore) - 3 positions
- Remote Senior Software Engineer (APAC/EMEA) - 7 positions  
- Remote Senior Designer (APAC/EMEA) - 3 positions
- Product Manager (Remote Global) - 3 positions
- DevOps Engineer (Remote Europe) - 3 positions
- Software Developer (Remote Global) - 7 positions
- Full Stack Engineer (US/Canada) - 7 positions
- Backend Engineer (Remote Europe) - 7 positions

### Adding New Searches

Use the configuration manager for easy setup:

```bash
# Add new job search
python3 config_manager.py add "data_scientist_remote.csv" "Data Scientist" "Remote - Global" true senior "https://remotive.io/remote-jobs"

# List current configurations
python3 config_manager.py list

# Run updated searches
./run_job_search.sh
```

### Market Intelligence

**Salary Ranges:**
- Senior Software Engineer: $110,000 - $200,000
- DevOps Engineer: $110,000 - $165,000
- Product Manager: $130,000 - $200,000

**Top Skills in Demand:**
- Cloud Platforms (AWS, Azure) - 80% of roles
- Programming Languages (Python, JavaScript, TypeScript)
- Frameworks (React, Node.js, Spring Boot)

## Dependencies 📦

- Python 3.7+
- PyYAML (for configuration parsing)
- Standard library modules: csv, concurrent.futures, logging, pathlib

## System Files 📁

```
agents/job-hunter/
├── job_config.yaml                    # Query configurations
├── job_hunter.py                      # Main search engine  
├── config_manager.py                  # Configuration helper
├── run_job_search.sh                  # Execution script
├── updated_job_search_summary.md      # Latest market report
├── *.csv                             # Job databases (8 files)
└── README.md                         # Documentation
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License 📄

This project is open source. See LICENSE file for details.

---

**Last Updated:** November 16, 2025 | **Status:** ✅ Active | **Happy Job Hunting!** 🎯