'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ShoppingBag } from 'lucide-react';
import { Container } from '@/components/common/Container';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Price } from '@/components/common/Price';
import { CartLineItem } from '@/components/cart/CartLineItem';
import { Link } from '@/lib/i18n/routing';
import api from '@/lib/api/client';
import type { Cart } from '@/lib/api/types';

export default function CartPage() {
  const t = useTranslations();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCart = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.cart.get();
      setCart(response.data);
    } catch (err) {
      setError(t('cart.errorLoading'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const handleUpdateQuantity = async (itemId: string, quantity: number) => {
    try {
      const response = await api.cart.updateItem(itemId, quantity);
      setCart(response.data);
    } catch (err) {
      setError(t('cart.errorUpdating'));
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      const response = await api.cart.removeItem(itemId);
      setCart(response.data);
    } catch (err) {
      setError(t('cart.errorRemoving'));
    }
  };

  const handleCheckout = () => {
    router.push('/checkout');
  };

  if (isLoading) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <h1 className="mb-8 text-3xl font-bold">{t('cart.title')}</h1>
          <p className="text-muted-foreground">{t('common.loading')}</p>
        </Container>
      </main>
    );
  }

  if (error) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <h1 className="mb-8 text-3xl font-bold">{t('cart.title')}</h1>
          <Card>
            <CardContent className="p-6">
              <p className="text-destructive">{error}</p>
              <Button onClick={loadCart} className="mt-4">
                {t('common.tryAgain')}
              </Button>
            </CardContent>
          </Card>
        </Container>
      </main>
    );
  }

  const isEmpty = !cart || cart.items.length === 0;
  const subtotal = cart?.subtotal ? parseFloat(cart.subtotal) : 0;

  return (
    <main id="main-content" className="flex-1 py-8">
      <Container>
        <h1 className="mb-8 text-3xl font-bold">{t('cart.title')}</h1>

        {isEmpty ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <ShoppingBag className="mb-4 h-16 w-16 text-muted-foreground" />
              <h2 className="mb-2 text-xl font-semibold">{t('cart.empty')}</h2>
              <p className="mb-6 text-muted-foreground">
                {t('cart.emptyDescription')}
              </p>
              <Button asChild>
                <Link href="/catalog">{t('common.continueShopping')}</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>
                    {cart.items.length}{' '}
                    {cart.items.length === 1 ? 'item' : 'itens'}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {cart.items.map((item) => (
                    <CartLineItem
                      key={item.id}
                      item={item}
                      onUpdateQuantity={handleUpdateQuantity}
                      onRemove={handleRemoveItem}
                    />
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle>{t('cart.subtotal')}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">
                      {t('cart.subtotal')}
                    </span>
                    <Price value={subtotal} />
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">
                      {t('cart.shipping')}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {t('cart.shippingCalculated')}
                    </span>
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between text-lg font-bold">
                    <span>{t('common.total')}</span>
                    <Price value={subtotal} />
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-2">
                  <Button
                    onClick={handleCheckout}
                    size="lg"
                    className="w-full"
                  >
                    {t('cart.checkout')}
                  </Button>
                  <Button variant="outline" size="lg" className="w-full" asChild>
                    <Link href="/catalog">{t('common.continueShopping')}</Link>
                  </Button>
                </CardFooter>
              </Card>
            </div>
          </div>
        )}
      </Container>
    </main>
  );
}
