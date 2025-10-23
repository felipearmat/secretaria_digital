#!/usr/bin/env python
"""
Initial setup script for the Virtual Secretary project.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Executes a command and displays the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error: {e.stderr}")
        return False


def main():
    """Main setup script function."""
    print("🚀 Setting up Virtual Secretary project...")
    
    # Check if Docker is installed
    if not run_command("docker --version", "Checking Docker"):
        print("❌ Docker is not installed. Please install Docker first.")
        sys.exit(1)
    
    # Check if Docker Compose is installed
    if not run_command("docker-compose --version", "Checking Docker Compose"):
        print("❌ Docker Compose is not installed. Please install Docker Compose first.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Django Settings
DJANGO_SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=secretaria_virtual
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Test Database
TEST_DB_NAME=secretaria_virtual_test

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Google Calendar Integration
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/google-calendar/callback/
GOOGLE_CALENDAR_AUTO_SYNC=True
GOOGLE_CALENDAR_SYNC_INTERVAL=3600
GOOGLE_CALENDAR_CLEANUP_DAYS=30

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://redis:6379/0
""")
        print("✅ .env file created")
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("✅ Logs directory created")
    
    # Build Docker images
    if not run_command("docker-compose build", "Building Docker images"):
        sys.exit(1)
    
    # Run migrations
    if not run_command("docker-compose run --rm web python manage.py migrate", "Running migrations"):
        sys.exit(1)
    
    # Initialize feature flags
    if not run_command("docker-compose run --rm web python manage.py init_feature_flags", "Initializing feature flags"):
        print("⚠️ Feature flags initialization failed, continuing...")
    
    # Create superuser
    print("👤 Creating superuser...")
    print("Enter superuser data:")
    username = input("Username: ")
    email = input("Email: ")
    
    create_superuser_cmd = f"""
docker-compose run --rm web python manage.py createsuperuser --username {username} --email {email} --noinput
"""
    
    if run_command(create_superuser_cmd, "Creating superuser"):
        print("✅ Superuser created successfully!")
        print(f"Username: {username}")
        print("Password: admin123 (change on first login)")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Run: docker-compose up")
    print("2. Access: http://localhost:8000")
    print("3. Admin: http://localhost:8000/admin")
    print("4. RabbitMQ: http://localhost:15672 (guest/guest)")
    print("5. API: http://localhost:8000/api/")
    print("\n🔧 For development:")
    print("- Run migrations: docker-compose exec web python manage.py migrate")
    print("- Django shell: docker-compose exec web python manage.py shell")
    print("- Run tests: python run_tests.py")
    print("- Run tests with PostgreSQL: python run_tests.py postgres")
    print("- Test PostgreSQL: python scripts/test_postgres_connection.py")
    print("- Logs: docker-compose logs -f")
    print("\n🌐 Feature Flags:")
    print("- Initialize flags: docker-compose exec web python manage.py init_feature_flags")
    print("- Test flags: docker-compose exec web python manage.py test_feature_flags")


if __name__ == "__main__":
    main()
