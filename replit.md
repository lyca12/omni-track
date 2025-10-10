# OmniTrack - Order & Inventory Management Platform

## Overview

OmniTrack is a multi-role order and inventory management system built with Streamlit. The application provides distinct interfaces for administrators, staff members, and customers to manage products, orders, and inventory. It features user authentication with role-based access control, real-time inventory tracking, order processing workflows, and analytics dashboards. The system supports demo accounts for testing and uses PostgreSQL for persistent data storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Problem:** Need a web-based interface that supports multiple user roles with different capabilities and views.

**Solution:** Streamlit-based multi-page application with role-based navigation and session state management.

**Key Design Decisions:**
- **Session State Management:** Uses Streamlit's session state to maintain authentication status, user role, and username across page navigation
- **Role-Based UI:** Different dashboard pages for admin, staff, and customer roles with conditional rendering based on user permissions
- **Page Structure:** Modular page architecture with separate files for each major feature (admin_dashboard.py, staff_dashboard.py, customer_dashboard.py, product_management.py, order_management.py)
- **Component Reusability:** Shared utilities for formatting, metrics calculation, and common UI patterns

**Pros:** Rapid development, built-in UI components, automatic refresh handling
**Cons:** Limited customization compared to traditional web frameworks, state management can be complex for larger applications

### Backend Architecture

**Problem:** Need secure user authentication, data persistence, and business logic separation.

**Solution:** Layered architecture with dedicated managers for authentication and database operations.

**Key Components:**

1. **Authentication Layer (auth.py)**
   - Uses bcrypt for password hashing with salt generation
   - Supports demo accounts with predefined roles (admin_demo, staff_demo, customer_demo)
   - Session management through environment-based secret keys
   - Role-based user registration (admin, staff, customer)

2. **Database Layer (database.py)**
   - PostgreSQL connection management using psycopg2
   - Automatic database initialization with schema creation
   - Uses RealDictCursor for dictionary-based result sets
   - Connection pooling through method-based connection retrieval

3. **Data Models (models.py)**
   - Dataclass-based models for type safety and structure
   - Enums for OrderStatus (PLACED, PAID, DELIVERED, CANCELLED) and UserRole (ADMIN, STAFF, CUSTOMER)
   - Core entities: User, Product, Order, OrderItem, CartItem
   - Business logic properties (e.g., is_low_stock on Product model)

4. **Utility Layer (utils.py)**
   - Formatting functions for currency and datetime display
   - Status visualization with emoji indicators
   - Business metrics calculations (revenue, completion rates, average order values)
   - Low stock detection logic

**Architecture Pattern:** Service-oriented design with manager classes handling specific domains (auth, database)

**Pros:** Clear separation of concerns, testable components, type safety through dataclasses
**Cons:** Some coupling between database and business logic layers

### Data Storage Solutions

**Problem:** Need reliable, structured data storage for users, products, orders, and order items.

**Solution:** PostgreSQL relational database with normalized schema.

**Database Schema:**

1. **Users Table**
   - Primary key: serial ID
   - Unique constraint on username
   - Stores password hash (bcrypt), role, and creation timestamp

2. **Products Table** (partial schema visible)
   - Tracks inventory with stock_quantity field
   - Supports categorization and SKU management
   - Low stock threshold configuration per product

3. **Orders and Order Items**
   - Foreign key relationships to users and products
   - Status tracking through enum values
   - Order total calculations

**Configuration:** 
- Supports both Streamlit secrets and .env file for database URL configuration
- Automatic fallback mechanism with user-friendly error messages for missing configuration
- Database URL can be provided via `st.secrets['DATABASE_URL']` or environment variable

**Pros:** ACID compliance, complex query support, mature ecosystem
**Cons:** Requires external PostgreSQL service, migration management needed for schema changes

### Authentication and Authorization

**Problem:** Secure multi-role access control with different permission levels.

**Solution:** Password-based authentication with bcrypt hashing and role-based access control.

**Security Mechanisms:**
- **Password Security:** bcrypt with automatic salt generation (strength factor configurable)
- **Session Management:** Session secret from environment variables with fallback to default (should be overridden in production)
- **Role Enforcement:** Three-tier role system (admin, staff, customer) with different capabilities
- **Demo Mode:** Special demo accounts bypass password verification for testing purposes

**Authorization Model:**
- Admins: Full access to all features including user management, analytics, and system configuration
- Staff: Access to order processing, inventory updates, and operational dashboards
- Customers: Limited to shopping, cart management, and own order viewing

**Alternatives Considered:** OAuth integration would provide social login but adds complexity; JWT tokens could enable stateless auth but Streamlit's session state works well for this use case.

**Pros:** Simple implementation, adequate security for most use cases, easy demo account setup
**Cons:** Session secret management needs attention in production, no built-in password reset flow

### External Dependencies

**Third-Party Libraries:**
- **streamlit:** Web application framework and UI components
- **psycopg2-binary:** PostgreSQL database adapter
- **bcrypt:** Password hashing library (version 4.0.1)
- **pandas:** Data manipulation and analysis
- **plotly:** Interactive data visualization for analytics dashboards
- **python-dotenv:** Environment variable management

**External Services:**
- **PostgreSQL Database:** Required external database service (typically provided by Replit or other hosting platform)
- Configuration expected via DATABASE_URL environment variable or Streamlit secrets

**Python Runtime:** Python 3.11 specified in runtime.txt

**Integration Notes:**
- Database connection details managed through environment configuration
- No external API integrations currently implemented
- Visualization relies on plotly for chart rendering within Streamlit