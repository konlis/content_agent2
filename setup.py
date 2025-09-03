"""
Setup Script for Content Agent
Handles initial setup, environment configuration, and dependency installation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}\n")

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Error: Python 3.11 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    try:
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip.exe")
        else:  # macOS/Linux
            pip_path = Path("venv/bin/pip")
        
        if not pip_path.exists():
            print("❌ Virtual environment pip not found")
            return False
        
        print("📦 Installing dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Setup .env file from template"""
    env_file = Path(".env")
    env_template = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_template.exists():
        print("❌ .env.example template not found")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "uploads", "exports"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def check_optional_services():
    """Check for optional services (PostgreSQL, Redis)"""
    print("\n🔍 Checking optional services:")
    
    # Check PostgreSQL
    try:
        subprocess.run(["psql", "--version"], capture_output=True, check=True)
        print("✅ PostgreSQL is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  PostgreSQL not found (SQLite will be used)")
    
    # Check Redis
    try:
        subprocess.run(["redis-server", "--version"], capture_output=True, check=True)
        print("✅ Redis is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Redis not found (caching will be disabled)")
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete! 🎉")
    
    print("Next steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OPENAI_API_KEY")
    print("   - ANTHROPIC_API_KEY") 
    print("   - GOOGLE_API_KEY")
    print("   - SERPAPI_KEY")
    
    print("\n2. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    
    print("\n3. Run the application:")
    print("   python main.py --mode frontend")
    
    print("\n4. Open your browser:")
    print("   http://localhost:8501")
    
    print("\n📖 For more information, see README.md")
    print("🐛 For issues, check the troubleshooting section")

def interactive_setup():
    """Interactive setup process"""
    print_header("Content Agent - Interactive Setup")
    
    print("This script will help you set up Content Agent on your system.")
    print("The setup process includes:")
    print("• Python version check")
    print("• Virtual environment creation")
    print("• Dependency installation")
    print("• Environment configuration")
    print("• Directory creation")
    
    response = input("\nContinue with setup? (y/N): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return False
    
    return True

def main():
    """Main setup function"""
    try:
        # Interactive confirmation
        if not interactive_setup():
            return
        
        # Step 1: Check Python version
        print_step(1, "Checking Python version")
        if not check_python_version():
            return
        
        # Step 2: Create virtual environment
        print_step(2, "Setting up virtual environment")
        if not create_virtual_environment():
            return
        
        # Step 3: Install dependencies
        print_step(3, "Installing dependencies")
        if not install_dependencies():
            return
        
        # Step 4: Setup environment file
        print_step(4, "Setting up environment configuration")
        if not setup_environment_file():
            return
        
        # Step 5: Create directories
        print_step(5, "Creating necessary directories")
        if not create_directories():
            return
        
        # Step 6: Check optional services
        print_step(6, "Checking optional services")
        check_optional_services()
        
        # Step 7: Print next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")

if __name__ == "__main__":
    main()
