'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ArrowLeft, ShoppingCart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Price } from '@/components/common/Price';
import { QuantityStepper } from '@/components/cart/QuantityStepper';
import api from '@/lib/api/client';
import type { ProductDetail, SKU } from '@/lib/api/types';

interface ProductDetailClientProps {
  product: ProductDetail;
}

export function ProductDetailClient({ product }: ProductDetailClientProps) {
  const t = useTranslations();
  const router = useRouter();

  const [selectedCondition, setSelectedCondition] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [selectedFoil, setSelectedFoil] = useState<string>('');
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);

  const availableConditions = [
    ...new Set(product.skus.map((sku) => sku.condition)),
  ];

  const availableLanguages = selectedCondition
    ? [
        ...new Set(
          product.skus
            .filter((sku) => sku.condition === selectedCondition)
            .map((sku) => sku.language)
        ),
      ]
    : [];

  const availableFoilOptions = selectedCondition && selectedLanguage
    ? [
        ...new Set(
          product.skus
            .filter(
              (sku) =>
                sku.condition === selectedCondition &&
                sku.language === selectedLanguage
            )
            .map((sku) => String(sku.is_foil))
        ),
      ]
    : [];

  const selectedSku: SKU | undefined =
    selectedCondition && selectedLanguage && selectedFoil
      ? product.skus.find(
          (sku) =>
            sku.condition === selectedCondition &&
            sku.language === selectedLanguage &&
            String(sku.is_foil) === selectedFoil
        )
      : undefined;

  const maxQuantity = selectedSku?.inventory?.quantity_available || 0;

  const handleAddToCart = async () => {
    if (!selectedSku) return;

    setIsAdding(true);
    setAddedToCart(false);

    try {
      await api.cart.addItem(selectedSku.id, quantity);
      setAddedToCart(true);
      setTimeout(() => setAddedToCart(false), 3000);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setIsAdding(false);
    }
  };

  const canAddToCart = selectedSku && maxQuantity > 0;

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => router.back()}
        className="gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        {t('common.back')}
      </Button>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Product Image */}
        <div className="relative aspect-[3/4] overflow-hidden rounded-lg bg-muted">
          {product.image_url ? (
            <Image
              src={product.image_url}
              alt={product.name}
              fill
              className="object-cover"
              priority
              sizes="(max-width: 1024px) 100vw, 50vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <span className="text-6xl font-bold text-muted-foreground">
                {product.name.charAt(0)}
              </span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">{product.name}</h1>

            {product.set_name && (
              <p className="mt-2 text-lg text-muted-foreground">
                {product.set_name}
              </p>
            )}

            {product.rarity && (
              <Badge variant="secondary" className="mt-2">
                {product.rarity}
              </Badge>
            )}
          </div>

          {product.description && (
            <div>
              <h2 className="font-semibold">{t('product.description')}</h2>
              <p className="mt-2 text-muted-foreground">{product.description}</p>
            </div>
          )}

          <Card>
            <CardContent className="space-y-4 p-6">
              <h2 className="font-semibold">{t('product.selectSKU')}</h2>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="condition">{t('product.condition')}</Label>
                  <Select
                    value={selectedCondition}
                    onValueChange={(value) => {
                      setSelectedCondition(value);
                      setSelectedLanguage('');
                      setSelectedFoil('');
                    }}
                  >
                    <SelectTrigger id="condition">
                      <SelectValue
                        placeholder={t('product.selectOption')}
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {availableConditions.map((condition) => (
                        <SelectItem key={condition} value={condition}>
                          {t(`product.conditions.${condition}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {selectedCondition && (
                  <div>
                    <Label htmlFor="language">{t('product.language')}</Label>
                    <Select
                      value={selectedLanguage}
                      onValueChange={(value) => {
                        setSelectedLanguage(value);
                        setSelectedFoil('');
                      }}
                    >
                      <SelectTrigger id="language">
                        <SelectValue
                          placeholder={t('product.selectOption')}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        {availableLanguages.map((language) => (
                          <SelectItem key={language} value={language}>
                            {t(`product.languages.${language}`)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {selectedCondition && selectedLanguage && (
                  <div>
                    <Label htmlFor="foil">{t('product.foil')}</Label>
                    <Select value={selectedFoil} onValueChange={setSelectedFoil}>
                      <SelectTrigger id="foil">
                        <SelectValue
                          placeholder={t('product.selectOption')}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        {availableFoilOptions.map((foil) => (
                          <SelectItem key={foil} value={foil}>
                            {t(`product.foilOptions.${foil}`)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {selectedSku && (
                  <div className="space-y-4 border-t pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {t('common.price')}:
                      </span>
                      <Price
                        value={selectedSku.price}
                        className="text-2xl font-bold text-primary"
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {t('product.availability')}:
                      </span>
                      <span
                        className={
                          maxQuantity > 0
                            ? 'text-sm font-medium text-green-600'
                            : 'text-sm font-medium text-destructive'
                        }
                      >
                        {maxQuantity > 0
                          ? t('common.limitedStock', { count: maxQuantity })
                          : t('common.outOfStock')}
                      </span>
                    </div>

                    {maxQuantity > 0 && (
                      <div>
                        <Label>{t('common.quantity')}</Label>
                        <div className="mt-2">
                          <QuantityStepper
                            value={quantity}
                            max={maxQuantity}
                            onChange={setQuantity}
                            disabled={isAdding}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <Button
                onClick={handleAddToCart}
                disabled={!canAddToCart || isAdding}
                className="w-full gap-2"
                size="lg"
              >
                <ShoppingCart className="h-5 w-5" />
                {isAdding
                  ? t('product.addingToCart')
                  : addedToCart
                  ? t('common.addedToCart')
                  : t('common.addToCart')}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
