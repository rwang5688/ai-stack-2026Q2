#!/usr/bin/env python3
"""
Application Merge Helper Script

This script helps merge your local Streamlit application with the authentication
template for deployment. It provides guidance and validation for the merge process.

Usage:
    python merge_app.py --help
    python merge_app.py --validate
    python merge_app.py --backup
"""

import os
import sys
import argparse
import shutil
from datetime import datetime

def validate_files():
    """Validate that required files exist for merging."""
    print("🔍 Validating files for merge process...")
    
    # Check source file (local app)
    local_app = "../multi_agent_bedrock/app.py"
    if not os.path.exists(local_app):
        print(f"❌ Source file not found: {local_app}")
        return False
    else:
        print(f"✅ Source file found: {local_app}")
    
    # Check target file (deployment template)
    deploy_app = "docker_app/app.py"
    if not os.path.exists(deploy_app):
        print(f"❌ Target file not found: {deploy_app}")
        return False
    else:
        print(f"✅ Target file found: {deploy_app}")
    
    # Check authentication utilities
    auth_file = "docker_app/utils/auth.py"
    if not os.path.exists(auth_file):
        print(f"❌ Authentication utilities not found: {auth_file}")
        return False
    else:
        print(f"✅ Authentication utilities found: {auth_file}")
    
    # Check configuration
    config_file = "docker_app/config_file.py"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    else:
        print(f"✅ Configuration file found: {config_file}")
    
    print("\n✅ All required files are present!")
    return True

def backup_current_app():
    """Create a backup of the current deployed app."""
    deploy_app = "docker_app/app.py"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"docker_app/app_backup_{timestamp}.py"
    
    try:
        shutil.copy2(deploy_app, backup_file)
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def analyze_local_app():
    """Analyze the local app to provide merge guidance."""
    local_app = "../multi_agent_bedrock/app.py"
    
    print("🔍 Analyzing local application...")
    
    try:
        with open(local_app, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count lines
        lines = content.split('\n')
        print(f"📊 Local app has {len(lines)} lines")
        
        # Check for imports
        imports = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        print(f"📦 Found {len(imports)} import statements")
        
        # Check for functions
        functions = [line for line in lines if line.strip().startswith('def ')]
        print(f"🔧 Found {len(functions)} function definitions")
        
        # Check for Streamlit components
        st_components = [line for line in lines if 'st.' in line]
        print(f"🎨 Found {len(st_components)} Streamlit components")
        
        # Check for potential conflicts
        conflicts = []
        if 'st.set_page_config' in content:
            conflicts.append("Page configuration (may conflict with auth setup)")
        if 'authenticator' in content:
            conflicts.append("Authentication code (may conflict with deployment auth)")
        
        if conflicts:
            print("⚠️  Potential merge conflicts:")
            for conflict in conflicts:
                print(f"   - {conflict}")
        else:
            print("✅ No obvious merge conflicts detected")
        
        return True
    except Exception as e:
        print(f"❌ Failed to analyze local app: {e}")
        return False

def show_merge_instructions():
    """Display step-by-step merge instructions."""
    print("\n" + "="*60)
    print("📋 MERGE INSTRUCTIONS")
    print("="*60)
    
    print("""
1. 🔒 KEEP AUTHENTICATION SECTION (Lines 1-25 in deployed app.py)
   - Do NOT modify the authentication imports
   - Do NOT change the authenticator setup
   - Do NOT remove the login enforcement

2. 📝 COPY APPLICATION LOGIC
   - Copy your imports (except 'import streamlit as st')
   - Copy your constants and configuration
   - Copy your function definitions
   - Copy your main application flow

3. 🎨 MERGE SIDEBAR COMPONENTS
   - Keep the authentication UI at the top of sidebar
   - Add your sidebar content AFTER the divider
   - Preserve the logout button functionality

4. 🧪 TEST THE INTEGRATION
   - Test locally with authentication commented out
   - Test deployment with authentication active
   - Verify both auth and app features work

5. 📚 REFERENCE DOCUMENTATION
   - See APP_MERGE_GUIDE.md for detailed instructions
   - Check MULTI_AGENT_BEDROCK.md for deployment steps
    """)

def main():
    parser = argparse.ArgumentParser(description="Application Merge Helper")
    parser.add_argument("--validate", action="store_true", help="Validate files for merge")
    parser.add_argument("--backup", action="store_true", help="Create backup of current app")
    parser.add_argument("--analyze", action="store_true", help="Analyze local app for merge guidance")
    parser.add_argument("--instructions", action="store_true", help="Show merge instructions")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        # No arguments provided, show help
        parser.print_help()
        return
    
    print("🚀 Application Merge Helper")
    print("="*40)
    
    if args.validate:
        if not validate_files():
            sys.exit(1)
    
    if args.backup:
        backup_file = backup_current_app()
        if not backup_file:
            sys.exit(1)
    
    if args.analyze:
        if not analyze_local_app():
            sys.exit(1)
    
    if args.instructions:
        show_merge_instructions()
    
    print("\n✅ Merge helper completed successfully!")
    print("📖 For detailed instructions, see: APP_MERGE_GUIDE.md")

if __name__ == "__main__":
    main()