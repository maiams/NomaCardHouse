import { getTranslations } from 'next-intl/server';
import { Container } from '@/components/common/Container';
import { Button } from '@/components/ui/button';
import { Link } from '@/lib/i18n/routing';
import { ProductGrid } from '@/components/products/ProductGrid';
import { ProductGridSkeleton } from '@/components/products/ProductGridSkeleton';
import api from '@/lib/api/client';
import { Suspense } from 'react';

async function FeaturedProducts() {
  const t = await getTranslations('home');

  try {
    const response = await api.products.list({ page: 1 });
    const featuredProducts = response.results.slice(0, 10);

    return (
      <div>
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-3xl font-bold">{t('featured')}</h2>
          <Button variant="outline" asChild>
            <Link href="/catalog">{t('viewAll')}</Link>
          </Button>
        </div>
        <ProductGrid products={featuredProducts} />
      </div>
    );
  } catch (error) {
    return (
      <div>
        <h2 className="text-3xl font-bold">{t('featured')}</h2>
        <p className="mt-4 text-muted-foreground">
          Erro ao carregar produtos em destaque.
        </p>
      </div>
    );
  }
}

export default async function HomePage() {
  const t = await getTranslations('home');

  return (
    <main id="main-content" className="flex-1">
      {/* Hero Section */}
      <section className="border-b bg-gradient-to-b from-muted/50 to-background py-20 lg:py-32">
        <Container>
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              {t('title')}
            </h1>
            <p className="mt-6 text-lg text-muted-foreground">
              {t('subtitle')}
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Button asChild size="lg">
                <Link href="/catalog">{t('cta')}</Link>
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* Featured Products Section */}
      <section className="py-16 lg:py-24">
        <Container>
          <Suspense fallback={<ProductGridSkeleton count={10} />}>
            <FeaturedProducts />
          </Suspense>
        </Container>
      </section>
    </main>
  );
}
