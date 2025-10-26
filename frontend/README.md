# Virtual Secretary - Frontend

Vue.js 3 frontend with Vuetify for the virtual secretary system.

## 🚀 Technologies

- **Vue.js 3** - JavaScript framework
- **Vuetify 3** - Material Design component library
- **Vuex 4** - State management
- **Vue Router 4** - Routing
- **Axios** - HTTP client
- **Socket.io** - WebSocket for real-time communication
- **Chart.js** - Charts and visualizations
- **Vite** - Build tool and dev server
- **Sass** - CSS preprocessor

## 📦 Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp env.example .env
```

3. Edit the `.env` file with your configurations.

## 🛠️ Development

To start the development server:

```bash
npm run dev
```

The server will be available at `http://localhost:3000`.

## 🏗️ Build

To create the production build:

```bash
npm run build
```

Files will be generated in the `dist/` folder.

## 📁 Project Structure

```
src/
├── components/          # Reusable components
├── views/              # Application pages
├── store/              # State management (Vuex)
│   ├── modules/        # Store modules
│   └── index.js        # Store configuration
├── router/             # Route configuration
├── services/           # Services (API, WebSocket)
├── utils/              # Utilities
├── assets/             # Static resources
│   ├── styles/         # Global styles
│   └── images/         # Images
├── locales/            # Localization files
├── App.vue             # Root component
└── main.js             # Entry point
```

## 🎨 Main Components

### Views
- **Login** - Authentication page
- **Dashboard** - Main panel with statistics
- **Appointments** - Appointment list and management
- **Services** - Service management
- **Users** - User management
- **Coupons** - Coupon management
- **Reports** - Reports and analytics

### Store Modules
- **auth** - Authentication and user
- **appointments** - Appointments
- **services** - Services
- **users** - Users
- **coupons** - Coupons
- **reports** - Reports
- **notifications** - Notifications
- **ui** - User interface

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VUE_APP_API_URL` | Backend API URL | `http://localhost:8000/api` |
| `VUE_APP_WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `VUE_APP_NAME` | Application name | `Virtual Secretary` |
| `VUE_APP_VERSION` | Application version | `1.0.0` |

### Development Proxy

Vite is configured to proxy requests:
- `/api/*` → Django Backend
- `/ws/*` → WebSocket

## 📱 Responsiveness

The frontend is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (up to 767px)

## 🎯 Features

### Authentication
- Login with email/password
- Social login (Google, Facebook, Microsoft)
- Password recovery
- Profile management

### Dashboard
- Real-time statistics
- Interactive charts
- Upcoming appointments
- Recent activity

### Appointments
- Paginated list with filters
- Creation and editing
- Confirmation/cancellation
- Detail view
- Advanced search

### Services
- Full CRUD
- Categorization
- Pricing and duration
- Availability

### Users
- User management
- Permission control
- Customizable profiles

### Coupons
- Coupon creation
- Automatic validation
- Usage control
- Usage reports

### Reports
- Financial reports
- Appointment statistics
- Actor performance
- Data export

## 🔌 Backend Integration

The frontend communicates with the Django backend through:
- **REST API** - For CRUD operations
- **WebSocket** - For real-time updates
- **Authentication** - Token-based authentication

## 🚀 Deploy

### Production Build
```bash
npm run build
```

### Docker
```bash
docker build -t virtual-secretary-frontend .
docker run -p 3000:80 virtual-secretary-frontend
```

### Nginx
Configure Nginx to serve static files and proxy to the API.

## 🧪 Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

## 📝 Available Scripts

| Script | Description |
|--------|-------------|
| `dev` | Development server |
| `build` | Production build |
| `preview` | Build preview |
| `lint` | Code linting |
| `test` | Unit tests |

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 🆘 Support

For support, contact us through:
- Email: support@virtualsecretary.com
- Issues: [GitHub Issues](https://github.com/virtual-secretary/frontend/issues)

