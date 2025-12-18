'use client';

import { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Input } from '@/components/ui/input';
import { ProductGrid } from '@/components/products/ProductGrid';
import type { Product } from '@/lib/api/types';

interface CatalogClientProps {
  initialProducts: Product[];
}

export function CatalogClient({ initialProducts }: CatalogClientProps) {
  const t = useTranslations();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredProducts = useMemo(() => {
    if (!searchQuery.trim()) {
      return initialProducts;
    }

    const query = searchQuery.toLowerCase();

    return initialProducts.filter((product) => {
      const nameMatch = product.name.toLowerCase().includes(query);
      const setMatch = product.set_name?.toLowerCase().includes(query);
      const brandMatch = product.brand?.toLowerCase().includes(query);

      return nameMatch || setMatch || brandMatch;
    });
  }, [initialProducts, searchQuery]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t('catalog.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
            aria-label={t('catalog.search')}
          />
        </div>
      </div>

      {searchQuery && (
        <div className="text-sm text-muted-foreground">
          {t('catalog.showingResults', { count: filteredProducts.length })}
        </div>
      )}

      <ProductGrid
        products={filteredProducts}
        emptyMessage={
          searchQuery
            ? t('catalog.noResults')
            : 'Nenhum produto disponível'
        }
      />
    </div>
  );
}
