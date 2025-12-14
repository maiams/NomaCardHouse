# Noma Card House - TCG Sales Portal

Complete e-commerce platform for Noma Card House, a Trading Card Game specialist retailer.

## Features

### Customer Features
- Product catalog with packs, single cards, accessories, and sealed products
- Search and filtering by name, category, rarity, and condition
- Shopping cart with persistent storage
- Checkout with shipping information
- Multiple payment methods: PIX, Credit Card, Apple Pay, Google Pay
- Responsive design for mobile and tablet devices

### Admin Features
- Product management (create, edit, delete)
- Inventory tracking and stock control
- Category management
- Order management and tracking
- Product image upload

## Tech Stack

- Framework: Next.js 14 (TypeScript)
- Database: PostgreSQL with Prisma ORM
- Styling: Tailwind CSS
- State Management: Zustand
- Payments: Stripe (supports PIX, Cards, Apple Pay, Google Pay)
- Icons: Lucide React

## Installation

### Quick Start (Recommended)

**Linux/macOS:**
```bash
git clone <repository-url>
cd NomaCardHouse
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
git clone <repository-url>
cd NomaCardHouse
setup.bat
```

The setup script will:
- Install dependencies
- Create `.env` file
- Start PostgreSQL with Docker
- Setup database schema
- Seed with sample data

Then run:
```bash
npm run dev
```

### Manual Installation

1. Clone the repository
```bash
git clone <repository-url>
cd NomaCardHouse
```

2. Install dependencies
```bash
npm install
```

3. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL="postgresql://noma:noma123@localhost:5432/nomacardhouse"
NEXTAUTH_SECRET="your-secret-here"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

4. Start PostgreSQL with Docker
```bash
docker-compose up -d postgres
```

5. Set up database
```bash
npm run db:push
npm run db:seed
```

6. Run development server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Full Docker Setup

To run everything in Docker (app + database):

1. Edit `docker-compose.yml` - Uncomment the `app` service
2. Run:
```bash
docker-compose up -d
```

### Admin Credentials

After seeding, login with:
- Email: admin@nomacardhouse.com
- Password: admin123

## Project Structure

```
NomaCardHouse/
├── prisma/
│   ├── schema.prisma       # Database schema
│   └── seed.ts            # Seed data
├── public/
│   └── uploads/           # Product images
├── src/
│   ├── app/
│   │   ├── admin/         # Admin panel pages
│   │   ├── api/           # API routes
│   │   ├── cart/          # Shopping cart
│   │   ├── checkout/      # Checkout process
│   │   └── products/      # Product catalog
│   ├── components/
│   │   ├── ui/            # Reusable UI components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── ProductCard.tsx
│   ├── lib/
│   │   ├── prisma.ts      # Prisma client
│   │   └── utils.ts       # Utility functions
│   └── store/
│       └── cart.ts        # Cart state management
└── package.json
```

## Database Schema

- User: Admin users
- Category: Product categories
- Product: TCG products (packs, singles, sealed items)
- Image: Product images
- Order: Customer orders
- OrderItem: Order line items

## Payment Integration

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from Dashboard
3. Configure webhook endpoint: `https://yourdomain.com/api/webhook/stripe`
4. Add webhook events:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `payment_intent.payment_failed`

### Supported Payment Methods

- Credit/Debit Cards: Via Stripe Checkout
- PIX: Brazilian instant payment (Stripe)
- Apple Pay: Mobile payments
- Google Pay: Mobile payments

## API Endpoints

### Products
- `GET /api/products` - List products (with filters)
- `POST /api/products` - Create product
- `GET /api/products/[id]` - Get product details
- `PUT /api/products/[id]` - Update product
- `DELETE /api/products/[id]` - Delete product

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order

### Upload
- `POST /api/upload` - Upload product image

### Checkout
- `POST /api/checkout` - Create Stripe checkout session

## Customization

### Colors
Edit `tailwind.config.ts` to customize the primary color:

```ts
colors: {
  primary: {
    50: '#f0f9ff',
    // ... customize colors
  },
}
```

### Logo
Replace the text logo in `src/components/Header.tsx` with your logo image.

## Deployment

### Option 1: Vercel + Managed Database

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

Managed Database Options:
- Supabase - Free PostgreSQL with dashboard
- Railway - Easy PostgreSQL hosting
- Neon - Serverless Postgres
- Render - Free PostgreSQL tier

### Option 2: Docker Deployment

Using Docker Compose (Full Stack):
```bash
# Edit docker-compose.yml and uncomment the app service
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

Using Dockerfile Only:
```bash
# Build image
docker build -t noma-card-house .

# Run with environment variables
docker run -p 3000:3000 \
  -e DATABASE_URL="postgresql://..." \
  -e STRIPE_SECRET_KEY="sk_..." \
  -e NEXTAUTH_SECRET="..." \
  noma-card-house
```

### Production Environment Variables

Required for production:
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
NEXTAUTH_SECRET=<generate with: openssl rand -base64 32>
NEXTAUTH_URL=https://yourdomain.com
NEXT_PUBLIC_APP_URL=https://yourdomain.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## License

This project is licensed under the MIT License.

## Support

For support, email contato@nomacardhouse.com or open an issue.
