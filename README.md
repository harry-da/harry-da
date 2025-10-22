# OpenCode Cron Jobs

This repository contains automated jobs that run on a schedule using GitHub Actions and OpenCode CLI.

## Structure

```
jobs/
├── daily-summary/
│   ├── agent.md          # OpenCode agent definition
│   └── space/            # Job memory space (timestamped results, AGENTS.md, etc.)
├── weekly-report/
│   ├── agent.md
│   └── space/
└── <job-id>/
    ├── agent.md
    └── space/
```

## OpenCode Agent Format

Each `agent.md` file follows the OpenCode agent format with YAML frontmatter:

```markdown
---
description: Brief description of what the agent does
---

Your system prompt and instructions for the agent go here.
```

See [OpenCode Agents Documentation](https://opencode.ai/docs/agents/#markdown) for more details.

## How It Works

1. **Job Definitions**: Each job is defined in `jobs/<job-id>/agent.md` using OpenCode agent format
2. **Scheduled Execution**: The `.github/workflows/cron-jobs.yml` workflow runs jobs on a schedule
3. **OpenCode CLI**: The workflow installs OpenCode CLI and runs each agent
4. **Results Storage**: Job results are saved to `jobs/<job-id>/space/result_<timestamp>.md`
5. **Memory Space**: The `space/` directory serves as cross-run memory for the job, which can include AGENTS.md and other files that can be updated by the job itself

## Cron Schedule

Jobs are configured in `.github/workflows/cron-jobs.yml`:

- **daily-summary**: Runs every day at 9:00 AM UTC (`0 9 * * *`)
- **weekly-report**: Runs every Monday at 10:00 AM UTC (`0 10 * * 1`)

## Adding a New Job

1. Create a new directory under `jobs/`:
   ```bash
   mkdir -p jobs/my-new-job
   ```

2. Create an `agent.md` file with OpenCode agent format:
   ```bash
   cat > jobs/my-new-job/agent.md << 'EOF'
   ---
   description: Brief description
   ---
   
   Your agent instructions here.
   EOF
   ```

3. Add your job to the matrix in `.github/workflows/cron-jobs.yml`:
   ```yaml
   strategy:
     matrix:
       include:
         - job-id: daily-summary
           schedule: '0 9 * * *'
         - job-id: weekly-report
           schedule: '0 10 * * 1'
         - job-id: my-new-job
           schedule: '0 12 * * *'
   ```

4. Add the corresponding schedule trigger:
   ```yaml
   'on':
     schedule:
       - cron: '0 9 * * *'
       - cron: '0 10 * * 1'
       - cron: '0 12 * * *'
   ```

## Manual Execution

Run any job manually using the GitHub Actions UI:

1. Go to the "Actions" tab
2. Select "Cron Jobs" workflow
3. Click "Run workflow"
4. Enter the job-id (e.g., `daily-summary`)
5. Click "Run workflow"

Or use GitHub CLI:
```bash
gh workflow run cron-jobs.yml -f job-id=daily-summary
```

## Local Testing

Test the script locally (requires OpenCode CLI installed):

```bash
# Install OpenCode
curl -fsSL https://opencode.ai/install | bash

# Run a job
bash scripts/run-job.sh daily-summary
```

## Authentication

The workflow uses:
- `HOME_TAR` secret: Contains the base64-encoded tar of home directory with OpenCode auth config
- GitHub Actions automatically extracts this to set up authentication

## Results Management

- Results are stored as markdown files: `result_YYYYMMDD_HHMMSS.md`
- Only the last 10 results are kept per job to avoid repository bloat
- Results are automatically committed and pushed by the GitHub Action
- The `space/` directory can contain additional files like AGENTS.md that the job can update across runs
