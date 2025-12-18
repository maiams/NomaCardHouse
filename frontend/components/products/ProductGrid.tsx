import { ProductCard } from './ProductCard';
import type { Product } from '@/lib/api/types';

interface ProductGridProps {
  products: Product[];
  emptyMessage?: string;
}

export function ProductGrid({ products, emptyMessage }: ProductGridProps) {
  if (products.length === 0 && emptyMessage) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-muted-foreground">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
