# Noma Card House - TCG Sales Portal

Portal de vendas completo para a Noma Card House, especializada em Trading Card Games (TCG).

## 🚀 Features

### Customer Features
- **Product Catalog**: Browse packs, single cards, accessories, and sealed products
- **Search & Filters**: Find products by name, category, rarity, condition
- **Shopping Cart**: Add/remove items with persistent storage
- **Checkout**: Complete purchase with shipping information
- **Payment Methods**:
  - PIX
  - Credit Card
  - Apple Pay
  - Google Pay
- **Responsive Design**: Full mobile and tablet support

### Admin Features
- **Product Management**: Create, edit, delete products
- **Inventory Control**: Track stock quantities
- **Category Management**: Organize products by categories
- **Order Management**: View and manage customer orders
- **Image Upload**: Upload product images

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (TypeScript)
- **Database**: PostgreSQL with Prisma ORM
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Payments**: Stripe (supports PIX, Cards, Apple Pay, Google Pay)
- **Icons**: Lucide React

## 📦 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd NomaCardHouse
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/nomacardhouse"
NEXTAUTH_SECRET="your-secret-here"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

4. **Set up database**
```bash
npm run db:push
npm run db:seed
```

5. **Run development server**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

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

## 🗄️ Database Schema

- **User**: Admin users
- **Category**: Product categories
- **Product**: TCG products (packs, singles, sealed items)
- **Image**: Product images
- **Order**: Customer orders
- **OrderItem**: Order line items

## 🔐 Payment Integration

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from Dashboard
3. Configure webhook endpoint: `https://yourdomain.com/api/webhook/stripe`
4. Add webhook events:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `payment_intent.payment_failed`

### Supported Payment Methods

- **Credit/Debit Cards**: Via Stripe Checkout
- **PIX**: Brazilian instant payment (Stripe)
- **Apple Pay**: Mobile payments
- **Google Pay**: Mobile payments

## 📱 API Endpoints

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

## 🎨 Customization

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

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Database
Use a managed PostgreSQL service:
- **Supabase** (recommended)
- **Railway**
- **Neon**
- **PlanetScale**

## 📝 License

This project is licensed under the MIT License.

## 🤝 Support

For support, email contato@nomacardhouse.com or open an issue.

---

Built with ❤️ for TCG enthusiasts