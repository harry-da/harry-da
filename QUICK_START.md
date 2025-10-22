# Quick Start Guide for OpenCode Cron Jobs

## Running Jobs Manually

### Via GitHub Actions UI
1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "Cron Jobs" from the workflows list
4. Click "Run workflow" button
5. Enter the job-id (e.g., `daily-summary` or `weekly-report`)
6. Click "Run workflow" to execute

### Via GitHub CLI (gh)
```bash
# Run daily-summary job
gh workflow run cron-jobs.yml -f job-id=daily-summary

# Run weekly-report job
gh workflow run cron-jobs.yml -f job-id=weekly-report
```

## Testing Locally

Test the job script without running OpenCode:
```bash
bash scripts/run-job.sh daily-summary
```

This will:
- Validate the agent.md file exists
- Extract the prompt
- Create the result directory structure
- Generate a placeholder result file

## Understanding Results

Results are stored in `jobs/<job-id>/results/` with filenames like:
```
result_20251022_104038.md
```

Format: `result_YYYYMMDD_HHMMSS.md`

Each result file contains:
- Timestamp of execution
- Job ID
- Original prompt
- OpenCode-generated result (when run in GitHub Actions)

## Creating a New Job

### 1. Create Job Directory and Agent File
```bash
mkdir -p jobs/my-custom-job
cat > jobs/my-custom-job/agent.md << 'EOF'
# My Custom Job

## Description
This job does something useful on a schedule.

## Prompt
Your detailed instructions for OpenCode.
Ask it to analyze, generate, or process something specific.
EOF
```

### 2. Update Workflow File
Edit `.github/workflows/cron-jobs.yml`:

**Add schedule trigger:**
```yaml
'on':
  schedule:
    - cron: '0 9 * * *'    # existing
    - cron: '0 10 * * 1'   # existing
    - cron: '0 15 * * 3'   # new: Wednesdays at 3 PM UTC
```

**Add to matrix:**
```yaml
strategy:
  matrix:
    include:
      - job-id: daily-summary
        schedule: '0 9 * * *'
      - job-id: weekly-report
        schedule: '0 10 * * 1'
      - job-id: my-custom-job
        schedule: '0 15 * * 3'
```

### 3. Test Your Job
```bash
# Test locally
bash scripts/run-job.sh my-custom-job

# Or trigger via GitHub Actions
gh workflow run cron-jobs.yml -f job-id=my-custom-job
```

## Cron Schedule Examples

```
# Every day at 2:30 AM UTC
0 2 * * *

# Every Monday at 9 AM UTC
0 9 * * 1

# Every hour
0 * * * *

# Every 15 minutes
*/15 * * * *

# First day of every month at midnight
0 0 1 * *

# Weekdays at 9 AM UTC
0 9 * * 1-5
```

## Troubleshooting

### Job Not Running
- Check the cron schedule is correct
- Verify the job-id matches the directory name
- Ensure the schedule in matrix matches the trigger schedule

### Prompt Not Found
- Verify `agent.md` has a `## Prompt` section
- Check the section header is exactly `## Prompt` (case-sensitive)

### Results Not Committed
- Check GitHub Actions logs for errors
- Verify the workflow has `contents: write` permission
- Ensure `GH_PAT` secret is configured

### OpenCode Errors
- Verify `GH_PAT` secret has correct token
- Check `HOME_TAR` secret is properly configured
- Review OpenCode action logs in GitHub Actions

## Best Practices

1. **Keep Prompts Clear**: Write specific, detailed prompts for best results
2. **Test Locally First**: Always test the script locally before deploying
3. **Monitor Results**: Regularly check result files for quality
4. **Limit Frequency**: Don't schedule jobs too frequently to avoid rate limits
5. **Clean Results**: The script keeps last 10 results automatically

## Example Prompts

### Code Quality Report
```markdown
## Prompt
Analyze the repository's code quality. Review recent commits and generate a report covering:
- Code complexity metrics
- Potential bugs or issues
- Best practice violations
- Security concerns
- Recommendations for improvements
```

### Dependency Updates
```markdown
## Prompt
Check for outdated dependencies in the project. Generate a report including:
- List of outdated packages with current and latest versions
- Security vulnerabilities in dependencies
- Recommended update strategy
- Breaking changes to be aware of
```

### Documentation Coverage
```markdown
## Prompt
Analyze the project's documentation coverage. Report on:
- Functions/modules lacking documentation
- README completeness
- API documentation quality
- Examples and usage guides
- Suggestions for improvement
```
