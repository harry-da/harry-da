# Automated OpenCode Jobs

This repository contains automated jobs that run on a schedule using GitHub Actions and OpenCode agents.

## Structure

```
jobs/
├── daily-summary/
│   ├── agent.md          # Job definition and prompt
│   └── results/          # Generated results (timestamped)
├── weekly-report/
│   ├── agent.md
│   └── results/
└── <job-id>/
    ├── agent.md
    └── results/
```

## How It Works

1. **Job Definitions**: Each job is defined in a directory under `jobs/<job-id>/` with an `agent.md` file
2. **Agent Format**: The `agent.md` file contains:
   - A description of what the agent does
   - A prompt section (starting with `## Prompt`) that will be sent to OpenCode
3. **Scheduled Execution**: The `.github/workflows/cron-jobs.yml` workflow runs jobs on a schedule
4. **Results Storage**: Job results are saved to `jobs/<job-id>/results/result_<timestamp>.md`

## Agent File Format

Each `agent.md` file should follow this structure:

```markdown
# Job Name

## Description
Brief description of what this agent does.

## Prompt
The actual prompt that will be sent to OpenCode.
This can span multiple lines and include detailed instructions.
```

## Cron Schedule

Jobs are configured in `.github/workflows/cron-jobs.yml`:

- **daily-summary**: Runs every day at 9:00 AM UTC (`0 9 * * *`)
- **weekly-report**: Runs every Monday at 10:00 AM UTC (`0 10 * * 1`)

The workflow uses a matrix strategy to manage multiple scheduled jobs efficiently. When a scheduled event triggers, the workflow checks which job matches the schedule and runs only that one.

## Adding a New Job

1. Create a new directory under `jobs/` with your job ID:
   ```bash
   mkdir -p jobs/my-new-job
   ```

2. Create an `agent.md` file with your job definition:
   ```bash
   cat > jobs/my-new-job/agent.md << 'EOF'
   # My New Job
   
   ## Description
   Description of what this job does.
   
   ## Prompt
   Your detailed prompt for OpenCode here.
   EOF
   ```

3. Add your job to the matrix in `.github/workflows/cron-jobs.yml` under the `run-scheduled-job` job:
   ```yaml
   strategy:
     matrix:
       include:
         - job-id: daily-summary
           schedule: '0 9 * * *'
         - job-id: weekly-report
           schedule: '0 10 * * 1'
         - job-id: my-new-job
           schedule: '0 12 * * *'  # Your cron schedule
   ```

4. Also add the corresponding schedule trigger at the top of the workflow:
   ```yaml
   'on':
     schedule:
       - cron: '0 9 * * *'
       - cron: '0 10 * * 1'
       - cron: '0 12 * * *'  # Your cron schedule
   ```

## Manual Execution

You can manually trigger any job using the GitHub Actions UI:

1. Go to the "Actions" tab
2. Select "Cron Jobs" workflow
3. Click "Run workflow"
4. Enter the job ID (e.g., `daily-summary`)
5. Click "Run workflow"

## Local Testing

Test a job locally without OpenCode:

```bash
bash scripts/run-job.sh daily-summary
```

This will create the output structure but won't execute the actual OpenCode prompt (that requires the GitHub Action environment).

## Results

- Results are stored as markdown files in `jobs/<job-id>/results/`
- Each result file is timestamped: `result_YYYYMMDD_HHMMSS.md`
- Only the last 10 results are kept per job to avoid repository bloat
- Results are automatically committed and pushed by the GitHub Action
