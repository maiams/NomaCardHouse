import { notFound } from 'next/navigation';
import { getTranslations } from 'next-intl/server';
import { Container } from '@/components/common/Container';
import { ProductDetailClient } from './ProductDetailClient';
import api from '@/lib/api/client';

interface ProductPageProps {
  params: {
    slug: string;
  };
}

export default async function ProductPage({ params }: ProductPageProps) {
  const t = await getTranslations('product');

  try {
    const response = await api.products.get(params.slug);
    const product = response.data;

    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <ProductDetailClient product={product} />
        </Container>
      </main>
    );
  } catch (error) {
    notFound();
  }
}
