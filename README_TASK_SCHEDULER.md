# Agentic Task Scheduler

An automated task scheduler that runs prompts through opencode on a configurable schedule and saves the results.

## Components

### 1. Configuration File (`tasks.yml`)
Defines the tasks to be executed, their schedules, prompts, and output settings.

**Structure:**
```yaml
tasks:
  - name: "task-name"
    description: "Task description"
    schedule: "cron-expression"  # Used by GitHub Actions
    prompt: "The prompt to send to opencode"
    output:
      type: "yaml" | "plain"
      path: "output/directory"
      filename_template: "filename-{date}.ext"
```

### 2. Task Scheduler Script (`task_scheduler.py`)
Python script that:
- Reads task configurations from `tasks.yml`
- Executes prompts through opencode
- Saves results in specified formats and locations

**Usage:**
```bash
# Run all scheduled tasks
python task_scheduler.py

# Run a specific task
python task_scheduler.py --task task-name

# Dry run (don't actually execute)
python task_scheduler.py --dry-run

# List available tasks
python task_scheduler.py --list
```

### 3. GitHub Actions Workflow
Automates the execution of tasks based on cron schedules.

**Features:**
- Automatic execution based on cron schedules
- Manual triggering with task selection
- Dry run mode for testing
- Automatic commit of results

## Setup Instructions

### 1. Copy the workflow file
Since GitHub Actions requires workflow permissions to create workflow files directly, you need to manually copy the workflow:

```bash
# Copy the generated workflow file to the workflows directory
cp task-scheduler-workflow.yml .github/workflows/task-scheduler.yml
```

### 2. Configure your tasks
Edit `tasks.yml` to define your specific tasks, prompts, and schedules.

### 3. Ensure required secrets
Make sure these secrets are configured in your repository:
- `GH_PAT`: GitHub Personal Access Token for opencode
- `HOME_TAR`: Base64-encoded tar of home directory files (if needed by opencode)

### 4. Test the setup
Run a dry run to test your configuration:
```bash
python task_scheduler.py --dry-run
```

## Example Tasks

The default configuration includes:
- **Daily Code Review**: Automated code quality review
- **Weekly Security Audit**: Security vulnerability assessment  
- **Dependency Check**: Outdated dependency detection
- **Documentation Review**: Documentation improvement suggestions

## Output Structure

Results are saved in the `reports/` directory with the following structure:
```
reports/
├── daily-reviews/
│   └── review-2024-01-15.yml
├── security-audits/
│   └── security-audit-2024-01-15.yml
├── dependencies/
│   └── deps-2024-01-17.txt
└── documentation/
    └── docs-review-2024-01-19.yml
```

## Customization

### Adding New Tasks
1. Add a new task entry to `tasks.yml`
2. Update the workflow schedule if needed
3. Modify the task determination logic in the workflow

### Changing Output Formats
- `yaml`: Structured YAML output with metadata
- `plain`: Simple text format

### Scheduling
Uses standard cron expressions:
- `0 9 * * *`: Daily at 9 AM UTC
- `0 10 * * 1`: Weekly on Monday at 10 AM UTC
- `0 8 * * 3`: Weekly on Wednesday at 8 AM UTC

## Troubleshooting

### Workflow not triggering
- Check that the workflow file is in `.github/workflows/`
- Verify cron expressions are valid
- Ensure repository has Actions enabled

### Task execution failures
- Check opencode CLI installation
- Verify required secrets are configured
- Review task logs in Actions tab

### Permission issues
- Ensure workflow has `contents: write` permission
- Check that GitHub token has necessary scopes