# Noma Card House - Frontend

Next.js 14 App Router frontend for Noma Card House TCG e-commerce platform.

## Tech Stack

- Next.js 14 (App Router)
- TypeScript 5
- Tailwind CSS 3
- shadcn/ui + Radix UI
- next-intl (i18n)
- Framer Motion

## Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Backend API running on http://localhost:8000

## Running Frontend + Backend Together

### Step 1: Start the Backend

From the project root:

```bash
cd backend
docker-compose up -d
```

Wait for all services to start. The backend API will be available at http://localhost:8000

To verify backend is running:
```bash
curl http://localhost:8000/api/v1/products/
```

### Step 2: Start the Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

### Step 3: Verify Integration

1. Open http://localhost:3000 in your browser
2. Navigate to the catalog page
3. Products from the backend should appear
4. Try adding a product to cart
5. Complete a test checkout

## Installation

```bash
npm install
```

## Environment Variables

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

If the backend is running on a different port or host:

```env
NEXT_PUBLIC_API_URL=http://your-backend-host:port/api/v1
```

## Development

```bash
npm run dev
```

Application will be available at http://localhost:3000

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Check that the backend CORS settings in `backend/config/settings/base.py` include:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
   ]
   ```

2. Restart the backend after changing CORS settings

### Connection Refused

If the frontend cannot connect to the backend:

1. Verify backend is running: `docker-compose ps` in backend directory
2. Check backend logs: `docker-compose logs backend`
3. Ensure NEXT_PUBLIC_API_URL in `.env.local` matches your backend URL
4. Try accessing the backend API directly in your browser

### Port Conflicts

If port 3000 or 8000 is already in use:

- Frontend: Set a different port with `PORT=3001 npm run dev`
- Backend: Update port in `docker-compose.yml` and update NEXT_PUBLIC_API_URL accordingly

### Session/Cart Issues

If cart operations fail:

1. Check browser console for errors
2. Verify X-Session-ID header is being sent (check Network tab in DevTools)
3. Clear browser localStorage and cookies, then refresh
4. Check backend logs for session-related errors

## Build

```bash
npm run build
npm start
```

## Internationalization

### Current Setup

The application uses next-intl for Portuguese (Brazil) translations. All UI text is rendered in pt-BR while source code remains in English.

### Translation Files

Translation keys are stored in `messages/pt-BR.json`:

```json
{
  "nav": {
    "home": "Início",
    "catalog": "Catálogo",
    "cart": "Carrinho",
    "account": "Conta"
  },
  "footer": {
    "about": "Sobre",
    "contact": "Contato",
    "terms": "Termos",
    "privacy": "Privacidade",
    "rights": "Todos os direitos reservados"
  }
}
```

### Adding New Translations

1. Add keys to `messages/pt-BR.json`:

```json
{
  "products": {
    "title": "Produtos",
    "addToCart": "Adicionar ao Carrinho"
  }
}
```

2. Use in components:

```tsx
import { useTranslations } from 'next-intl';

export function ProductCard() {
  const t = useTranslations('products');

  return (
    <div>
      <h2>{t('title')}</h2>
      <button>{t('addToCart')}</button>
    </div>
  );
}
```

### Server Components

For Server Components, use `getTranslations`:

```tsx
import { getTranslations } from 'next-intl/server';

export async function ServerComponent() {
  const t = await getTranslations('products');

  return <h1>{t('title')}</h1>;
}
```

## API Client

### Session Management

The API client automatically manages session IDs for cart operations:

- Generates UUID on first visit
- Persists in localStorage and cookies
- Automatically injects `X-Session-ID` header

### Usage Example

```tsx
import { api } from '@/lib/api/client';

// Fetch products
const products = await api.products.list();

// Add to cart (automatic session ID)
await api.cart.addItem(skuId, quantity);
```

## UI Components

### shadcn/ui Components

Base UI components are in `components/ui/`:

- `button.tsx`
- `separator.tsx`

Add new components using shadcn CLI:

```bash
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
```

### Layout Components

Common layout components in `components/layout/`:

- `Header.tsx` - Navigation bar with cart/account icons
- `Footer.tsx` - Site footer with links

### Common Components

Reusable components in `components/common/`:

- `Container.tsx` - Max-width content wrapper
- `Logo.tsx` - Brand logo with link

## Accessibility

The application meets WCAG 2.2 AA standards:

- Semantic HTML elements
- Keyboard navigation support
- Focus visible indicators
- Skip-to-main-content link
- Reduced motion support via `prefers-reduced-motion`
- ARIA labels on interactive elements

## Theme

### Color Tokens

Theme colors are defined in `app/[locale]/globals.css` using HSL variables:

```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96.1%;
  --accent: 210 40% 96.1%;
  /* ... */
}
```

### Typography

- Primary: Inter (sans-serif)
- Monospace: JetBrains Mono

## Project Structure

```
frontend/
├── app/
│   └── [locale]/
│       ├── layout.tsx          # Root layout with providers
│       ├── page.tsx             # Landing page
│       └── globals.css          # Global styles
├── components/
│   ├── common/                  # Reusable components
│   ├── layout/                  # Layout components
│   └── ui/                      # shadcn/ui components
├── lib/
│   ├── api/                     # API client
│   │   ├── client.ts            # Typed fetch wrapper
│   │   ├── session.ts           # Session management
│   │   └── types.ts             # TypeScript types
│   ├── i18n/                    # i18n configuration
│   └── utils.ts                 # Utility functions
├── messages/
│   └── pt-BR.json               # Portuguese translations
└── public/                      # Static assets
```

## Code Standards

All source code must be in English:
- File names
- Variable names
- Function names
- Comments
- Internal documentation

UI text must be in Portuguese (pt-BR) via translation files.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
