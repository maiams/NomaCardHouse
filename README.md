# Noma Card House - TCG E-commerce Platform

Backend API for a Brazil-focused trading card game (TCG) e-commerce platform.

## Tech Stack

- Python 3.12
- Django 5.0 + Django REST Framework
- PostgreSQL 16
- Redis 7
- Celery (async task processing)
- Docker + Docker Compose

## Features

- TCG product catalog with variants (condition, language, foil)
- Real-time inventory management with anti-oversell protection
- Shopping cart with automatic reservation expiration
- Brazilian checkout support (CPF, CEP, Brazilian address format)
- Modular payment gateway abstraction (Pix, Boleto, Credit Card)
- RESTful API with consistent response format
- Django admin interface for product/order management

## Project Structure

```
backend/
├── apps/
│   ├── products/       # Product catalog and SKUs
│   ├── inventory/      # Stock management with reservations
│   ├── cart/           # Shopping cart with timed reservations
│   ├── orders/         # Order processing
│   ├── payments/       # Payment provider abstraction
│   └── core/           # Shared utilities
├── config/             # Django settings and configuration
├── scripts/            # Management scripts (seed data, etc.)
└── requirements/       # Python dependencies
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd NomaCardHouse
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Start services with Docker Compose:

```bash
docker-compose up -d
```

4. Run migrations:

```bash
docker-compose exec backend python manage.py migrate
```

5. Create superuser for admin access:

```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Load sample data:

```bash
docker-compose exec backend python manage.py shell < scripts/seed_data.py
```

7. Access the application:

- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- API Browsable: http://localhost:8000/api/v1/products/ (in browser)

## API Endpoints

### Products

```bash
# List all products
GET /api/v1/products/

# Get product details
GET /api/v1/products/{slug}/

# List SKUs
GET /api/v1/products/skus/

# Get specific SKU
GET /api/v1/products/skus/{id}/
```

### Cart

All cart endpoints require `X-Session-ID` header.

```bash
# Get current cart
GET /api/v1/cart/
Header: X-Session-ID: {uuid}

# Add item to cart
POST /api/v1/cart/add_item/
Header: X-Session-ID: {uuid}
Body: {
  "sku_id": "uuid",
  "quantity": 1
}

# Update cart item quantity
PATCH /api/v1/cart/items/{item_id}/
Header: X-Session-ID: {uuid}
Body: {
  "quantity": 2
}

# Remove item from cart
DELETE /api/v1/cart/items/{item_id}/
Header: X-Session-ID: {uuid}

# Clear cart
POST /api/v1/cart/clear/
Header: X-Session-ID: {uuid}
```

### Orders

```bash
# List orders
GET /api/v1/orders/

# Get order details
GET /api/v1/orders/{order_number}/

# Checkout
POST /api/v1/orders/checkout/
Header: X-Session-ID: {uuid}
Body: {
  "customer_email": "customer@example.com",
  "customer_name": "João Silva",
  "customer_cpf": "123.456.789-00",
  "customer_phone": "+55 11 98765-4321",
  "shipping_street": "Rua Augusta",
  "shipping_number": "123",
  "shipping_complement": "Apto 45",
  "shipping_neighborhood": "Consolação",
  "shipping_city": "São Paulo",
  "shipping_state": "SP",
  "shipping_cep": "01304-001",
  "payment_method": "PIX",
  "notes": "Optional delivery notes"
}
```

## API Examples

### Browse Products

```bash
curl http://localhost:8000/api/v1/products/
```

Response:
```json
{
  "success": true,
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "name": "Lightning Bolt",
      "slug": "lightning-bolt",
      "brand": "Magic: The Gathering",
      "set_name": "Core Set 2021",
      "rarity": "COMMON",
      "min_price_brl": "5.00",
      "is_in_stock": true
    }
  ]
}
```

### Add to Cart

```bash
curl -X POST http://localhost:8000/api/v1/cart/add_item/ \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: 12345678-1234-1234-1234-123456789abc" \
  -d '{
    "sku_id": "your-sku-uuid",
    "quantity": 2
  }'
```

Response:
```json
{
  "success": true,
  "message": "Item added to cart successfully",
  "data": {
    "id": "cart-uuid",
    "session_id": "12345678-1234-1234-1234-123456789abc",
    "total_items": 2,
    "subtotal_brl": "10.00",
    "items": [...]
  }
}
```

### Complete Checkout

```bash
curl -X POST http://localhost:8000/api/v1/orders/checkout/ \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: 12345678-1234-1234-1234-123456789abc" \
  -d '{
    "customer_email": "joao@example.com",
    "customer_name": "João Silva",
    "customer_cpf": "123.456.789-00",
    "customer_phone": "+55 11 98765-4321",
    "shipping_street": "Rua Augusta",
    "shipping_number": "123",
    "shipping_neighborhood": "Consolação",
    "shipping_city": "São Paulo",
    "shipping_state": "SP",
    "shipping_cep": "01304-001",
    "payment_method": "PIX"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "order": {
      "order_number": "NCH-20250117-12345",
      "status": "PENDING",
      "total_brl": "10.00"
    },
    "payment": {
      "method": "PIX",
      "status": "PENDING",
      "pix_qr_code": "00020126580014br.gov.bcb.pix...",
      "pix_copy_paste": "00020126580014br.gov.bcb.pix...",
      "expires_at": "2025-01-17T20:00:00Z"
    }
  }
}
```

## Cart Reservation Logic

The system implements anti-oversell protection using inventory reservations:

1. When item is added to cart, inventory is reserved for 15 minutes
2. Reserved stock is locked and unavailable to other users
3. Reservations expire automatically via Celery tasks
4. On checkout, reserved inventory is consumed
5. If cart expires, reservations are released

This prevents race conditions and ensures accurate stock levels.

## Payment Provider Integration

The payment system uses a modular adapter pattern:

1. Base `PaymentProvider` interface in `apps/payments/providers/base.py`
2. Stub provider for development in `apps/payments/providers/stub.py`
3. To add new provider (e.g., Mercado Pago):
   - Implement `PaymentProvider` interface
   - Add to `get_payment_provider()` factory function
   - Update settings with provider credentials

Stub provider returns fake Pix/Boleto data for testing without real payment processing.

## Development

### Run tests

```bash
docker-compose exec backend pytest
```

### Access Django shell

```bash
docker-compose exec backend python manage.py shell
```

### Create migrations

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### View logs

```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Celery Tasks

Periodic tasks for maintenance:

- `cleanup_expired_carts`: Remove carts older than 30 days
- `cleanup_expired_reservations`: Release expired inventory reservations

Configure schedules in Django admin under Periodic Tasks.

## Security Features

- CSRF protection enabled
- CORS restricted to configured origins
- Session-based authentication
- Rate limiting on sensitive endpoints (planned)
- Webhook signature verification (planned)
- Input validation on all endpoints
- SQL injection protection via ORM
- XSS protection via DRF serializers

## Environment Variables

Key variables in `.env`:

```
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
CART_RESERVATION_TIMEOUT_MINUTES=15
CART_EXPIRY_DAYS=30
```

## Next Steps for Stage 2B (Frontend)

- Next.js 14 with App Router
- TypeScript + Tailwind CSS + shadcn/ui
- Portuguese UI with next-intl
- Product catalog with filters
- Cart management with real-time reservation status
- Checkout flow with Brazilian address validation
- Pix/Boleto payment display

## Production Deployment

For production deployment:

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production`
2. Configure production database (PostgreSQL)
3. Set up Redis instance
4. Configure S3 for media storage
5. Set `DEBUG=False`
6. Use Gunicorn as WSGI server
7. Set up Nginx reverse proxy
8. Enable HTTPS with SSL certificate
9. Configure Sentry for error tracking
10. Set up Celery Beat for scheduled tasks

## License

Proprietary - Noma Card House
