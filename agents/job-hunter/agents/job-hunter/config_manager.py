#!/usr/bin/env python3
"""
Job Hunter Configuration Manager
Utility to add new job search configurations dynamically
"""

import yaml
from pathlib import Path

def add_job_config(
    filename: str,
    role: str,
    location: str,
    remote: bool = True,
    level: str = "senior",
    website: str = "https://remotive.io/remote-jobs"
):
    """Add a new job configuration to the YAML file"""
    
    config_path = Path("job_config.yaml")
    
    # Load existing configuration
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    
    # Add new configuration
    if not filename.endswith('.csv'):
        filename += '.csv'
        
    config[filename] = {
        'role': role,
        'location': location,
        'remote': remote,
        'level': level,
        'website': website
    }
    
    # Save updated configuration
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=True)
    
    print(f"✅ Added configuration for: {filename}")
    print(f"   Role: {role}")
    print(f"   Location: {location}")
    print(f"   Remote: {remote}")
    print(f"   Level: {level}")
    print(f"   Website: {website}")

def list_configurations():
    """List all current job configurations"""
    config_path = Path("job_config.yaml")
    
    if not config_path.exists():
        print("❌ No job_config.yaml found")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("📋 Current Job Configurations:")
    print("-" * 50)
    
    for filename, details in config.items():
        print(f"📄 {filename}")
        print(f"   Role: {details['role']}")
        print(f"   Location: {details['location']}")
        print(f"   Remote: {details['remote']}")
        print(f"   Level: {details['level']}")
        print(f"   Website: {details['website']}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("Job Hunter Configuration Manager")
        print("Usage:")
        print("  python3 config_manager.py list")
        print("  python3 config_manager.py add <filename> <role> <location> [remote] [level] [website]")
        print("\nExamples:")
        print("  python3 config_manager.py add 'product_manager_remote.csv' 'Product Manager' 'Remote' true senior 'https://wellfound.com/'")
        print("  python3 config_manager.py add 'data_scientist_sf.csv' 'Data Scientist' 'San Francisco' false mid 'https://dice.com/'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_configurations()
    elif command == "add" and len(sys.argv) >= 5:
        filename = sys.argv[2]
        role = sys.argv[3]
        location = sys.argv[4]
        remote = sys.argv[5].lower() == 'true' if len(sys.argv) > 5 else True
        level = sys.argv[6] if len(sys.argv) > 6 else "senior"
        website = sys.argv[7] if len(sys.argv) > 7 else "https://remotive.io/remote-jobs"
        
        add_job_config(filename, role, location, remote, level, website)
    else:
        print("❌ Invalid command or insufficient arguments")
        print("Use 'python3 config_manager.py' for usage instructions")