# OpenCode Scheduled Agents

This repository contains automated agents that run on a schedule using GitHub Actions and OpenCode CLI.

## Structure

```
agents/
├── daily-summary/
│   ├── agent.md          # OpenCode agent definition
│   └── logs/             # Agent execution logs (timestamped YAML results)
├── weekly-report/
│   ├── agent.md
│   └── logs/
└── <agent-id>/
    ├── agent.md
    └── logs/
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

1. **Agent Definitions**: Each agent is defined in `agents/<agent-id>/agent.md` using OpenCode agent format
2. **Scheduled Execution**: The `.github/workflows/scheduled-agents.yml` workflow runs agents on a schedule
3. **OpenCode CLI**: The workflow installs OpenCode CLI and runs each agent
4. **Results Storage**: Agent results are saved to `agents/<agent-id>/logs/<timestamp>.log` in YAML format
5. **Execution Logs**: The `logs/` directory contains timestamped execution logs in YAML format

## Cron Schedule

Agents are configured in `.github/workflows/scheduled-agents.yml`:

- **daily-summary**: Runs every day at 9:00 AM UTC (`0 9 * * *`)
- **weekly-report**: Runs every Monday at 10:00 AM UTC (`0 10 * * 1`)

## Adding a New Agent

1. Create a new directory under `agents/`:
   ```bash
   mkdir -p agents/my-new-agent
   ```

2. Create an `agent.md` file with OpenCode agent format:
   ```bash
   cat > agents/my-new-agent/agent.md << 'EOF'
   ---
   description: Brief description
   ---
   
   Your agent instructions here.
   EOF
   ```

3. Add your agent to the matrix in `.github/workflows/scheduled-agents.yml`:
   ```yaml
   strategy:
     matrix:
       include:
         - job-id: daily-summary
           schedule: '0 9 * * *'
         - job-id: weekly-report
           schedule: '0 10 * * 1'
          - job-id: my-new-agent
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

Run any agent manually using the GitHub Actions UI:

1. Go to the "Actions" tab
2. Select "Scheduled Agents" workflow
3. Click "Run workflow"
4. Enter the job-id (e.g., `daily-summary`)
5. Click "Run workflow"

Or use GitHub CLI:
```bash
gh workflow run scheduled-agents.yml -f job-id=daily-summary
```

## Local Testing

Test the script locally (requires OpenCode CLI installed):

```bash
# Install OpenCode
curl -fsSL https://opencode.ai/install | bash

# Run an agent
bash scripts/run-agent daily-summary
```

## Authentication

The workflow uses:
- `HOME_TAR` secret: Contains the base64-encoded tar of home directory with OpenCode auth config
- GitHub Actions automatically extracts this to set up authentication

## Results Management

- Results are stored as YAML files: `<timestamp>.log`
- Only the last 10 results are kept per agent to avoid repository bloat
- Results are automatically committed and pushed by the GitHub Action
- The `logs/` directory contains timestamped YAML execution logs that the agent can access across runs
