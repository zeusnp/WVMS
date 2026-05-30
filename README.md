# Wood Carrying Vehicle Management System (WVMS)

A professional, enterprise-grade web-based management system for wood transportation vehicles, measurement records, parties, and logistics operations.

## 🚀 Features

### Core Modules
- ✅ **Authentication & RBAC**: Secure login with role-based access control
- ✅ **Dashboard**: Real-time analytics and KPIs
- ✅ **Vehicle Management**: Complete vehicle entry and tracking
- ✅ **Measurement Module**: Advanced wood measurement handling
- ✅ **Party Management**: Party and sub-party tracking
- ✅ **Vehicle Tracking**: Real-time status monitoring
- ✅ **Advanced Search**: Powerful filtering and search capabilities
- ✅ **Reporting & Export**: Excel, PDF, CSV exports
- ✅ **Audit Trail**: Complete activity logging
- ✅ **Mobile Responsive**: Fully responsive design
- ✅ **Dark Mode**: Theme customization

## 📊 Tech Stack

- **Frontend**: React 18+ with TypeScript
- **Backend**: Node.js/Express with TypeScript
- **Database**: PostgreSQL
- **Authentication**: JWT with refresh tokens
- **UI Framework**: Material-UI (MUI) v5+
- **State Management**: Redux Toolkit
- **Form Handling**: React Hook Form
- **Charts**: Recharts
- **Export**: ExcelJS, PDFKit

## 📁 Project Structure

```
WVMS/
├── frontend/                # React application
├── backend/                 # Node.js/Express API
├── shared/                  # Shared types and utilities
├── docs/                    # Documentation
├── docker-compose.yml       # Docker setup
└── package.json             # Root package configuration
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/zeusnp/WVMS.git
cd WVMS

# Install dependencies
cd backend && npm install
cd ../frontend && npm install

# Setup environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Run migrations
cd backend && npm run migrate

# Start services
npm run dev
```

## 📖 Documentation

See [docs/](./docs/) for detailed documentation including:
- [Architecture](./docs/ARCHITECTURE.md)
- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)
- [Roles & Permissions](./docs/ROLES_PERMISSIONS.md)

## 📝 User Roles

1. **Super Admin** - Full system access
2. **Admin** - Administrative operations
3. **Operator** - Data entry and operational
4. **Measurement Staff** - Measurement operations
5. **Viewer/Accountant** - Read-only with reporting

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Audit trail for all operations
- Rate limiting on API endpoints
- CORS protection
- CSRF protection

## 📦 Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📄 License

MIT

## 👨‍💻 Contributors

Created for professional wood transportation management.

---

**Status**: 🔨 Development in Progress
