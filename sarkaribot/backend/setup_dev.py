#!/usr/bin/env python
"""
Development environment setup script for SarkariBot.

This script helps set up the development environment by:
1. Creating necessary directories
2. Copying .env.example to .env if it doesn't exist
3. Running initial migrations
4. Creating a superuser (optional)
5. Validating the setup

Usage:
    python setup_dev.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up SarkariBot development environment...\n")
    
    # Set Django settings module for development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # 1. Create necessary directories
    print("📁 Creating necessary directories...")
    directories = ['logs', 'media', 'static', 'staticfiles']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    # 2. Copy .env.example to .env if it doesn't exist
    env_file = base_dir / '.env'
    env_example = base_dir / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        print("\n📄 Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("   ✅ .env file created")
        print("   ℹ️  Edit .env file to customize your settings")
    elif env_file.exists():
        print("\n📄 .env file already exists")
    else:
        print("\n⚠️  No .env.example found")
    
    # 3. Install dependencies (if requirements file exists)
    if Path('requirements/base_simple.txt').exists():
        print("\n📦 Installing Python dependencies...")
        success = run_command(
            'pip install -r requirements/base_simple.txt',
            'Installing requirements',
            check=False
        )
        if not success:
            print("   ⚠️  Some dependencies may have failed to install")
            print("   ℹ️  You can continue with basic Django functionality")
    
    # 4. Run Django checks
    print("\n🔍 Checking Django configuration...")
    success = run_command(
        'python manage.py check',
        'Running Django system checks'
    )
    
    if not success:
        print("❌ Django configuration has issues. Please fix them before continuing.")
        return False
    
    # 5. Run migrations
    print("\n🗄️  Setting up database...")
    run_command(
        'python manage.py makemigrations',
        'Creating migrations',
        check=False
    )
    
    success = run_command(
        'python manage.py migrate',
        'Running migrations'
    )
    
    if not success:
        print("❌ Database migration failed. Please check your database configuration.")
        return False
    
    # 6. Collect static files
    print("\n📦 Collecting static files...")
    run_command(
        'python manage.py collectstatic --noinput',
        'Collecting static files',
        check=False
    )
    
    # 7. Create superuser (optional)
    print("\n👤 Creating superuser...")
    create_superuser = input("Do you want to create a superuser? (y/N): ").lower().strip()
    if create_superuser in ['y', 'yes']:
        run_command(
            'python manage.py createsuperuser',
            'Creating superuser',
            check=False
        )
    
    # 8. Final validation
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Review and customize your .env file")
    print("   2. Start the development server: python manage.py runserver")
    print("   3. Visit http://localhost:8000 to see your application")
    print("   4. Visit http://localhost:8000/admin to access Django admin")
    print("   5. Visit http://localhost:8000/api/ to see the API documentation")
    
    print("\n🔧 Development commands:")
    print("   • python manage.py runserver          - Start development server")
    print("   • python manage.py shell              - Django shell")
    print("   • python manage.py makemigrations     - Create new migrations")
    print("   • python manage.py migrate            - Run migrations")
    print("   • python manage.py test               - Run tests")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)