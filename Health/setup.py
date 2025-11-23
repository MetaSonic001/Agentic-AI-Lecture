#!/usr/bin/env python3
"""
Setup script for Doctor's Admin Automator
Creates necessary directories and initializes the system
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        'data',
        'logs',
        'prescriptions',
        'agents',
        'utils'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}/")
    
    # Create .gitkeep files to preserve empty directories
    for directory in ['data', 'logs', 'prescriptions']:
        gitkeep = Path(directory) / '.gitkeep'
        gitkeep.touch()

def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("\n⚠️  WARNING: .env file not found!")
        print("   Please create .env file with your GROQ_API_KEY")
        print("   You can copy .env.example and add your API key\n")
        return False
    
    print("✓ .env file found")
    return True

def verify_installation():
    """Verify all required packages are installed"""
    required_packages = [
        'streamlit',
        'crewai',
        'langchain_groq',
        'dotenv',
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} NOT installed")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt\n")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🩺 Doctor's Admin Automator - Setup Script")
    print("=" * 60)
    print()
    
    print("Step 1: Creating directory structure...")
    create_directory_structure()
    print()
    
    print("Step 2: Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    print("Step 3: Verifying package installation...")
    packages_ok = verify_installation()
    print()
    
    if env_ok and packages_ok:
        print("=" * 60)
        print("✅ Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Ensure your GROQ_API_KEY is set in .env file")
        print("2. Run: streamlit run main.py")
        print("3. Open http://localhost:8501 in your browser")
        print()
    else:
        print("=" * 60)
        print("⚠️  Setup incomplete - please fix the issues above")
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()