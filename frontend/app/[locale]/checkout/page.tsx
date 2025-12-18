'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Container } from '@/components/common/Container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Price } from '@/components/common/Price';
import { CheckoutForm } from '@/components/checkout/CheckoutForm';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api/client';
import type { Cart, CheckoutRequest } from '@/lib/api/types';

export default function CheckoutPage() {
  const t = useTranslations();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCart = async () => {
      setIsLoading(true);
      try {
        const response = await api.cart.get();
        setCart(response.data);

        if (response.data.items.length === 0) {
          router.push('/cart');
        }
      } catch (err) {
        setError(t('cart.errorLoading'));
      } finally {
        setIsLoading(false);
      }
    };

    loadCart();
  }, [router, t]);

  const handleSubmit = async (data: CheckoutRequest) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await api.orders.checkout(data);
      const order = response.data;

      router.push(`/order/${order.order_number}`);
    } catch (err) {
      setError(t('checkout.errors.submissionFailed'));
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <h1 className="mb-8 text-3xl font-bold">{t('checkout.title')}</h1>
          <p className="text-muted-foreground">{t('common.loading')}</p>
        </Container>
      </main>
    );
  }

  if (!cart || cart.items.length === 0) {
    return null;
  }

  const subtotal = cart.subtotal_brl;

  return (
    <main id="main-content" className="flex-1 py-8">
      <Container>
        <h1 className="mb-8 text-3xl font-bold">{t('checkout.title')}</h1>

        {error && (
          <Card className="mb-6 border-destructive">
            <CardContent className="p-4">
              <p className="text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Checkout Form */}
          <div className="lg:col-span-2">
            <CheckoutForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle>{t('checkout.orderSummary')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  {cart.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <div className="flex-1">
                        <p className="font-medium">{item.sku.product?.name || item.sku.sku_code}</p>
                        <div className="flex gap-1 text-xs text-muted-foreground">
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
                        <p className="text-xs text-muted-foreground">Qtd: {item.quantity}</p>
                      </div>
                      <Price
                        value={item.line_total_brl}
                        className="text-sm"
                      />
                    </div>
                  ))}
                </div>

                <Separator />

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {t('common.subtotal')}
                    </span>
                    <Price value={subtotal} />
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {t('cart.shipping')}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {t('cart.shippingCalculated')}
                    </span>
                  </div>
                </div>

                <Separator />

                <div className="flex items-center justify-between text-lg font-bold">
                  <span>{t('common.total')}</span>
                  <Price value={subtotal} />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </Container>
    </main>
  );
}
