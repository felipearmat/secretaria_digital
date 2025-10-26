# Virtual Secretary

Virtual appointment and management system for service companies with WhatsApp and Google Calendar integration, featuring multi-language support and feature flags.

## 🚀 Features

### Company and User Management
- Role-based system: Super Admin, Admin, Manager, Actor, User
- Company and user management
- Granular permission control
- Multi-language support (Portuguese/English)

### Appointments
- Appointment creation and management
- Appointment approval system
- Recurrences (daily, weekly, monthly)
- Time blocks and availability
- Conflict validation
- Real-time availability checking

### Services and Pricing
- Service registration per actor
- Custom pricing per actor
- Service duration management
- Dynamic pricing with discounts

### Coupon System
- Company-wide or actor-specific coupons
- Percentage or fixed value discounts
- Usage limits and expiration
- Service-specific restrictions

### Financial Management
- Cost control per actor
- Financial reports
- Payment management
- Individual and company accountability

### Notifications
- Real-time notifications via WebSocket
- WhatsApp integration
- Automatic emails
- Appointment reminders
- Multi-channel notification system

### Feature Flags
- Dynamic feature control
- Localization management
- A/B testing capabilities
- Environment-specific configurations

## 🛠️ Technologies

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL (with SQLite for testing)
- **Cache/Message Broker**: Redis, RabbitMQ
- **Async Tasks**: Celery with priority queues
- **WebSocket**: Django Channels
- **Frontend**: Vue.js 3 with Vuetify (planned)
- **Containerization**: Docker, Docker Compose
- **Feature Flags**: Django Waffle
- **Internationalization**: Django i18n with model translation
- **Testing**: Pytest with coverage support

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- Python 3.9+ (for local development)
- PostgreSQL (for local development)

## 🚀 Installation and Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd secretaria_digital
```

### 2. Configure environment variables
```bash
cp config.env .env
```

Edit the `.env` file with your configurations:
```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
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
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/google-calendar/callback/

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

### 3. Run with Docker Compose
```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d
```

### 4. Access the application
- **Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Redis**: localhost:6379

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/users/login/` - User login
- `POST /api/auth/users/logout/` - User logout
- `GET /api/auth/users/me/` - Current user info

### Companies
- `GET /api/companies/` - List companies
- `POST /api/companies/` - Create company
- `GET /api/companies/{id}/` - Company details
- `GET /api/companies/{id}/statistics/` - Company statistics

### Appointments
- `GET /api/appointments/` - List appointments
- `POST /api/appointments/` - Create appointment
- `GET /api/appointments/availability/` - Check availability
- `POST /api/appointments/{id}/confirm/` - Confirm appointment
- `POST /api/appointments/{id}/cancel/` - Cancel appointment

### Services
- `GET /api/appointments/services/` - List services
- `POST /api/appointments/services/` - Create service
- `GET /api/appointments/services/by_actor/` - Services by actor

### Feature Flags
- `GET /api/feature-flags/flags/` - List feature flags
- `GET /api/feature-flags/flags/active/` - Active flags
- `GET /api/feature-flags/localization/` - Localization config

## 📁 Project Structure

```
secretaria_digital/
├── apps/
│   ├── empresas/              # Company management
│   ├── autenticacao/          # User authentication and authorization
│   ├── appointments/          # Appointments and services
│   ├── notificacoes/          # Notification system
│   ├── pagamentos/            # Payments and coupons
│   ├── google_calendar/       # Google Calendar integration
│   └── feature_flags/         # Feature flags and localization
├── secretariaVirtual/         # Django project settings
├── docker/                   # Docker configurations
├── scripts/                  # Utility scripts
├── locale/                   # Internationalization files
├── docker-compose.yml        # Service orchestration
├── requirements.txt          # Python dependencies
├── pytest.ini              # Test configuration
├── run_tests.py             # Test runner script
├── FEATURE_FLAGS.md         # Feature flags documentation
├── POSTGRES_SETUP.md        # PostgreSQL setup guide
└── comandos.md              # Useful commands
```

## 🔧 Development Setup

### Database Setup
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Initialize feature flags
docker-compose exec web python manage.py init_feature_flags

# Test PostgreSQL connection
python scripts/test_postgres_connection.py
```

### Testing
```bash
# Run tests with SQLite (faster)
python run_tests.py

# Run tests with PostgreSQL
python run_tests.py postgres

# Run tests with coverage
python run_tests.py coverage

# Run specific tests
python run_tests.py pattern test_models
```

### Django Shell
```bash
# Access Django shell
docker-compose exec web python manage.py shell

# Or locally
python manage.py shell
```

## 📊 Celery Queues

The system uses two queues for asynchronous processing:

- **high**: High priority tasks (urgent notifications, WhatsApp)
- **low**: Low priority tasks (emails, reminders, cleanup)

### Workers
- **celery**: General worker (processes both queues)
- **celery_high**: Dedicated worker for high priority queue
- **celery_beat**: Periodic task scheduler

### Periodic Tasks
- Google Calendar synchronization (hourly)
- Token refresh (hourly)
- Log cleanup (daily)
- Incremental sync (every 15 minutes)

## 🔐 Permission System

### Super Admin
- Full system access
- Can manage all companies
- Can configure feature flags
- Can manage localization settings

### Admin
- Full access within company
- Can manage users and actors
- Can configure company settings
- Access to company reports

### Manager
- Can create actors, appointments, users
- Can manage costs and coupons
- Access to company reports
- Can manage recurring schedules

### Actor
- Can create own appointments
- Can manage own costs
- Access to own reports
- Can set availability and blocks

### User
- Can view actor schedules
- Can request appointments (requires approval)
- Can manage own profile
- Can use coupons

## 🔌 Integrations

### Google Calendar
- Automatic appointment synchronization
- Event creation in actor's calendar
- OAuth 2.0 authentication
- Real-time sync with conflict detection
- Token refresh automation

### WhatsApp (Twilio)
- Confirmation notifications
- Appointment reminders
- Status notifications
- Multi-language support
- Template-based messages

### Feature Flags
- Dynamic feature control
- Localization management
- A/B testing capabilities
- Environment-specific configurations

## 📈 Monitoring

### Logs
- Application logs in `/code/logs/django.log`
- Celery logs via `docker-compose logs celery`
- Database logs via `docker-compose logs db`

### Metrics
- RabbitMQ Management: http://localhost:15672
- Redis monitoring via Redis commands
- Database performance via PostgreSQL logs
- Feature flag usage via Django admin

### Health Checks
```bash
# Check service status
docker-compose ps

# Check database connectivity
python scripts/test_postgres_connection.py

# Check Celery workers
docker-compose exec web python manage.py shell
>>> from celery import current_app
>>> current_app.control.inspect().active()
```

## 🚀 Deployment

For production, configure:
1. Production environment variables
2. SSL/HTTPS certificates
3. Database backup strategy
4. Log monitoring and rotation
5. Domain configuration
6. Feature flags for production
7. Localization settings
8. Performance monitoring

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use feature flags for new functionality
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more details.

## 📚 Documentation

- [Feature Flags Guide](FEATURE_FLAGS.md)
- [PostgreSQL Setup](POSTGRES_SETUP.md)
- [Useful Commands](comandos.md)
- [API Documentation](api/) (coming soon)