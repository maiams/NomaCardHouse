import { getTranslations } from 'next-intl/server';
import { Container } from '@/components/common/Container';
import { CatalogClient } from './CatalogClient';
import api from '@/lib/api/client';

export default async function CatalogPage() {
  const t = await getTranslations('catalog');

  try {
    const response = await api.products.list();
    const products = response.results;

    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <div className="mb-8">
            <h1 className="text-4xl font-bold">{t('title')}</h1>
          </div>

          <CatalogClient initialProducts={products} />
        </Container>
      </main>
    );
  } catch (error) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <div className="mb-8">
            <h1 className="text-4xl font-bold">{t('title')}</h1>
          </div>
          <p className="text-muted-foreground">
            Erro ao carregar produtos. Tente novamente mais tarde.
          </p>
        </Container>
      </main>
    );
  }
}
