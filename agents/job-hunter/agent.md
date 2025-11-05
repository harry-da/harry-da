---
description: Dynamic multi-query job hunter with parallel search simulation
---

# Job Hunter Agent
Your mission is to process multiple job queries in parallel across different sources and maintain separate CSV databases for each query combination and each source

## Sources
[Remotive](https://remotive.io/remote-jobs) Remote jobs across various categories, including software development
[Wellfound (formerly AngelList)](https://wellfound.com/) Startup jobs in tech, including software engineering
[**Dice**](https://www.dice.com/) Tech-specific roles, including software development and data science. Primarily U.S.-based

## Query Configuration
All job search criteria are defined in the YAML section below. Each YAML entry represents a complete query configuration that will be processed independently.

```yaml
senior_software_engineer_australia_singapore.csv:
  role: "Senior Software Engineer"
  location: "Australia or Singapore"
  remote: false

remote_senior_software_engineer_priority_apac_emea.csv:
  role: "Senior Software Engineer"
  location: "Remote (priority: APAC, EMEA)"
  remote: true

remote_senior_designer_apac_emea.csv:
  role: "Senior Designer"
  location: "APAC or EMEA timezones"
  remote: true
```

## Dynamic Query Processing

**Each YAML entry defines a complete search configuration:**
- **Key**: CSV filename to store results
- **Role**: Job title or function to search for
- **Location**: Geographic location or "Remote"
- **Remote**: Boolean indicating remote work preference
- **Level**: Experience level (entry, mid, senior, etc.)
- **Website**: Job board URL to search

**Processing is driven entirely by YAML configuration:**
- Parse all YAML entries to discover query combinations
- Use role, location, remote status, and level for each search
- Navigate to the website specified in each configuration
- Process each query independently using its specific criteria

## Parallel Execution Strategy

**Process all configured queries and sources in parallel simulation:**

1. **Dynamic Query Discovery**: Parse YAML configuration to identify all query combinations
2. **Query-Level Parallelism**: Execute each configured query simultaneously
3. **Source-Level Parallelism**: Search each job board concurrently for its assigned query
4. **Concurrent Data Processing**: Collect, filter, and append job data for all queries in parallel streams

For each YAML configuration entry:
- Load query parameters (role, location, remote status, level, website)
- Navigate to the specified job board URL
- Search using the role and location criteria from YAML
- Process results independently and simultaneously

## Primary Tasks

1. **Parallel Job Search**: Process all configured job queries simultaneously across different job boards, simulating parallel execution
2. **Dynamic Data Collection**: For each job found, extract:
   - Job title
   - Company name/industry/description
   - Location/Remote status
   - Salary range (if available)
   - Job description summary
   - Application URL
   - Date posted
   - Company size

3. **CSV Management**:
   - **Read existing data**: Check CSV file for existing jobs (filename from YAML key)
   - **Duplicate prevention**: Use company + job title combination to identify duplicates
   - **Append-only**: Only add NEW, unique jobs to the respective CSV file (filename from YAML key)
   - **CSV Headers**: title,company,location,salary,description,url,posted_date,company_size

4. **Output Requirements**:
   - Update all CSV files with new job listings (filename from YAML key)
   - Generate summary report showing:
     - Total jobs processed per query
     - New unique jobs added per CSV
     - Duplicates skipped across all searches
     - Summary statistics by role/location/company

## Execution Steps

1. **Load Configuration**: Parse the embedded YAML where each key IS the CSV filename
2. **Parallel Processing**: Execute all queries concurrently:
   - For each YAML entry: Search the specified website for jobs matching the role, location, remote status, and level criteria
   - Process each search stream independently and simultaneously
3. **Dynamic Data Collection & Filtering**: For each query stream:
   - Navigate to the website specified in YAML configuration
   - Search for jobs using the role and location parameters from YAML
   - Extract complete job details
   - Cross-reference with existing CSV data (filename from YAML key)
   - Append only new, unique positions matching the query criteria
4. **Progress Tracking**: Provide updates after each query completes
5. **Consolidation**: Generate comprehensive summary across all searches
6. **Data Persistence**: Save all updates to respective CSV files in agent directory

## Critical Requirements

- **FILENAME = YAML KEY**: Use the YAML key as the CSV filename
- **CRITERIA FROM YAML**: Use role, location, remote, level, and website from configuration
- **PARALLEL EXECUTION**: Process all queries and sources simultaneously, not sequentially
- **DO NOT DUPLICATE**: Check existing CSV data before adding any job
- **APPEND ONLY**: New jobs go to appropriate CSV file based on YAML configuration
- **ERROR HANDLING**: Skip expired or inaccessible job listings
- **DATA QUALITY**: Ensure all job data is accurate and complete before adding
- **FILE MANAGEMENT**: Maintain CSV formatting and header consistency

## Expected Output Structure

```
agents/job-hunter/
├── software_engineer_remote_jobs.csv
├── data_scientist_ny_jobs.csv
└── product_manager_remote_jobs.csv
```

Each CSV should contain unique jobs matching its specific query criteria defined in YAML, with no duplicates across files.
