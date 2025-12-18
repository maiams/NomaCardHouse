import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Price } from '@/components/common/Price';
import { Link } from '@/lib/i18n/routing';
import type { Product } from '@/lib/api/types';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const hasStock = product.is_in_stock;
  const lowestPrice = product.min_price_brl;

  return (
    <Link href={`/product/${product.slug}`}>
      <Card className="group h-full overflow-hidden transition-all hover:shadow-lg">
        <div className="relative aspect-[3/4] overflow-hidden bg-muted">
          <div className="flex h-full items-center justify-center bg-muted">
            <span className="text-4xl font-bold text-muted-foreground">
              {product.name.charAt(0)}
            </span>
          </div>

          {product.rarity && (
            <Badge
              className="absolute right-2 top-2"
              variant={getRarityVariant(product.rarity)}
            >
              {product.rarity}
            </Badge>
          )}

          {!hasStock && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60">
              <Badge variant="destructive">Fora de Estoque</Badge>
            </div>
          )}
        </div>

        <CardContent className="p-4">
          <h3 className="line-clamp-2 font-semibold leading-tight group-hover:text-primary">
            {product.name}
          </h3>

          {product.set_name && (
            <p className="mt-1 text-xs text-muted-foreground">
              {product.set_name}
            </p>
          )}
        </CardContent>

        <CardFooter className="p-4 pt-0">
          <div className="flex w-full items-center justify-between">
            {lowestPrice !== null && hasStock ? (
              <div>
                <p className="text-xs text-muted-foreground">A partir de</p>
                <Price
                  value={lowestPrice}
                  className="text-lg font-bold text-primary"
                />
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                Indisponível
              </div>
            )}
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}

function getRarityVariant(rarity: string): 'default' | 'secondary' | 'warning' {
  const rarityLower = rarity.toLowerCase();

  if (rarityLower.includes('mythic') || rarityLower.includes('secret')) {
    return 'warning';
  }

  if (rarityLower.includes('rare')) {
    return 'default';
  }

  return 'secondary';
}
