'use client';

import { useState } from 'react';
import { Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Price } from '@/components/common/Price';
import { QuantityStepper } from './QuantityStepper';
import type { CartItem } from '@/lib/api/types';

interface CartLineItemProps {
  item: CartItem;
  onUpdateQuantity: (itemId: string, quantity: number) => Promise<void>;
  onRemove: (itemId: string) => Promise<void>;
}

export function CartLineItem({
  item,
  onUpdateQuantity,
  onRemove,
}: CartLineItemProps) {
  const t = useTranslations();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity === item.quantity) return;

    setIsUpdating(true);
    try {
      await onUpdateQuantity(item.id, newQuantity);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    setIsRemoving(true);
    try {
      await onRemove(item.id);
    } finally {
      setIsRemoving(false);
    }
  };

  const itemTotal = item.line_total_brl;
  const maxQuantity = Math.min(item.sku.quantity_available || 99, 99);

  return (
    <div className="flex gap-4 border-b pb-4">
      <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-md bg-muted">
        <div className="flex h-full items-center justify-center">
          <span className="text-2xl font-bold text-muted-foreground">
            {item.sku.product?.name?.charAt(0) || item.sku.sku_code.charAt(0)}
          </span>
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-between">
        <div>
          <h3 className="font-semibold">{item.sku.product?.name || item.sku.sku_code}</h3>

          <div className="mt-1 flex flex-wrap gap-2">
            <Badge variant="outline" className="text-xs">
              {t(`product.conditions.${item.sku.condition}`)}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {t(`product.languages.${item.sku.language}`)}
            </Badge>
            {item.sku.is_foil && (
              <Badge variant="outline" className="text-xs">
                Foil
              </Badge>
            )}
          </div>

          <div className="mt-2 flex items-center gap-4">
            <Price
              value={item.unit_price_brl}
              className="text-sm text-muted-foreground"
            />
            <span className="text-sm text-muted-foreground">×</span>
            <QuantityStepper
              value={item.quantity}
              max={maxQuantity}
              onChange={handleQuantityChange}
              disabled={isUpdating || isRemoving}
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Price value={itemTotal} className="text-lg font-bold" />

          <Button
            variant="ghost"
            size="sm"
            onClick={handleRemove}
            disabled={isRemoving || isUpdating}
            aria-label={t('cart.remove')}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
    </div>
  );
}
