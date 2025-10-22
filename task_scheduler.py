#!/usr/bin/env python3
"""
Agentic Task Scheduler
Runs scheduled tasks defined in tasks.yml and sends prompts to opencode
"""

import yaml
import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import argparse

def load_tasks(config_path="tasks.yml"):
    """Load tasks from YAML configuration file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('tasks', [])
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return []

def should_run_task(task, current_time=None):
    """
    Check if a task should run based on its schedule
    For simplicity, this will be handled by GitHub Actions cron
    This function can be extended for more complex scheduling logic
    """
    return True

def create_output_directory(output_path):
    """Create output directory if it doesn't exist"""
    Path(output_path).mkdir(parents=True, exist_ok=True)

def generate_filename(template, task_name, current_time=None):
    """Generate filename from template"""
    if current_time is None:
        current_time = datetime.now()
    
    return template.format(
        date=current_time.strftime("%Y-%m-%d"),
        datetime=current_time.strftime("%Y-%m-%d_%H-%M-%S"),
        task=task_name
    )

def run_opencode_task(task, dry_run=False):
    """Run a single task through opencode"""
    print(f"Running task: {task['name']}")
    
    if dry_run:
        print(f"DRY RUN - Would execute: {task['prompt']}")
        return {"status": "dry_run", "output": "Dry run - no actual execution"}
    
    try:
        # Create a temporary file with the prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(task['prompt'])
            prompt_file = f.name
        
        # Run opencode with the prompt
        # Note: This assumes opencode CLI is available in the environment
        result = subprocess.run([
            'opencode', 'run', '--prompt-file', prompt_file
        ], capture_output=True, text=True, timeout=300)
        
        # Clean up temp file
        os.unlink(prompt_file)
        
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout, "error": result.stderr}
        else:
            return {"status": "error", "output": result.stdout, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "output": "", "error": "Task timed out after 5 minutes"}
    except Exception as e:
        return {"status": "exception", "output": "", "error": str(e)}

def save_output(task, result, current_time=None):
    """Save task output to the specified location"""
    if current_time is None:
        current_time = datetime.now()
    
    output_config = task.get('output', {})
    output_type = output_config.get('type', 'plain')
    output_path = output_config.get('path', 'reports')
    filename_template = output_config.get('filename_template', '{task}-{date}.txt')
    
    # Create output directory
    create_output_directory(output_path)
    
    # Generate filename
    filename = generate_filename(filename_template, task['name'], current_time)
    filepath = os.path.join(output_path, filename)
    
    # Prepare content based on output type
    if output_type == 'yaml':
        content = {
            'task': task['name'],
            'description': task.get('description', ''),
            'executed_at': current_time.isoformat(),
            'prompt': task['prompt'],
            'result': result
        }
        with open(filepath, 'w') as f:
            yaml.dump(content, f, default_flow_style=False)
    else:  # plain text
        content = f"""Task: {task['name']}
Description: {task.get('description', '')}
Executed at: {current_time.isoformat()}
Prompt: {task['prompt']}

Result:
{result.get('output', '')}

Status: {result.get('status', 'unknown')}
Errors: {result.get('error', 'None')}
"""
        with open(filepath, 'w') as f:
            f.write(content)
    
    print(f"Output saved to: {filepath}")
    return filepath

def run_scheduled_tasks(config_path="tasks.yml", task_filter=None, dry_run=False):
    """Run all scheduled tasks or a specific task"""
    tasks = load_tasks(config_path)
    
    if not tasks:
        print("No tasks found in configuration")
        return
    
    current_time = datetime.now()
    results = []
    
    for task in tasks:
        # Skip task if filter is specified and doesn't match
        if task_filter and task['name'] != task_filter:
            continue
            
        if should_run_task(task, current_time):
            print(f"\n{'='*50}")
            print(f"Executing task: {task['name']}")
            print(f"Description: {task.get('description', 'No description')}")
            print(f"{'='*50}")
            
            result = run_opencode_task(task, dry_run)
            
            if not dry_run:
                output_file = save_output(task, result, current_time)
                result['output_file'] = output_file
            
            results.append({
                'task': task['name'],
                'result': result
            })
        else:
            print(f"Skipping task: {task['name']} (not scheduled to run)")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Agentic Task Scheduler')
    parser.add_argument('--config', default='tasks.yml', help='Path to tasks configuration file')
    parser.add_argument('--task', help='Run specific task by name')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - don\'t actually execute tasks')
    parser.add_argument('--list', action='store_true', help='List all available tasks')
    
    args = parser.parse_args()
    
    if args.list:
        tasks = load_tasks(args.config)
        print("Available tasks:")
        for task in tasks:
            print(f"  - {task['name']}: {task.get('description', 'No description')}")
            print(f"    Schedule: {task.get('schedule', 'No schedule')}")
        return
    
    results = run_scheduled_tasks(args.config, args.task, args.dry_run)
    
    if results:
        print(f"\n{'='*50}")
        print("EXECUTION SUMMARY")
        print(f"{'='*50}")
        
        for result in results:
            task_name = result['task']
            status = result['result']['status']
            print(f"{task_name}: {status}")
        
        print(f"\nTotal tasks executed: {len(results)}")
    else:
        print("\nNo tasks were executed.")

if __name__ == "__main__":
    main()