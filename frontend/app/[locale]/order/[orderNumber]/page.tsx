'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { CheckCircle2, Copy, Download } from 'lucide-react';
import { Container } from '@/components/common/Container';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Price } from '@/components/common/Price';
import { Link } from '@/lib/i18n/routing';
import api from '@/lib/api/client';

interface OrderPageProps {
  params: {
    orderNumber: string;
  };
}

export default function OrderPage({ params }: OrderPageProps) {
  const t = useTranslations();
  const [order, setOrder] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copiedPix, setCopiedPix] = useState(false);
  const [copiedBoleto, setCopiedBoleto] = useState(false);

  useEffect(() => {
    const loadOrder = async () => {
      try {
        const response = await api.orders.get(params.orderNumber);
        setOrder(response.data);
      } catch (error) {
        console.error('Failed to load order:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadOrder();
  }, [params.orderNumber]);

  const handleCopyPix = async () => {
    if (order?.payment_details?.pix_code) {
      await navigator.clipboard.writeText(order.payment_details.pix_code);
      setCopiedPix(true);
      setTimeout(() => setCopiedPix(false), 2000);
    }
  };

  const handleCopyBoleto = async () => {
    if (order?.payment_details?.boleto_barcode) {
      await navigator.clipboard.writeText(order.payment_details.boleto_barcode);
      setCopiedBoleto(true);
      setTimeout(() => setCopiedBoleto(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <p className="text-muted-foreground">{t('common.loading')}</p>
        </Container>
      </main>
    );
  }

  if (!order) {
    return (
      <main id="main-content" className="flex-1 py-8">
        <Container>
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground">Pedido não encontrado</p>
            </CardContent>
          </Card>
        </Container>
      </main>
    );
  }

  const isPix = order.payment_method === 'PIX';
  const isBoleto = order.payment_method === 'BOLETO';
  const totalAmount = order.total_brl;

  return (
    <main id="main-content" className="flex-1 py-8">
      <Container className="max-w-4xl">
        <div className="mb-8 text-center">
          <CheckCircle2 className="mx-auto mb-4 h-16 w-16 text-green-600" />
          <h1 className="mb-2 text-3xl font-bold">{t('order.confirmation')}</h1>
          <p className="text-muted-foreground">{t('order.thankYou')}</p>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Detalhes do Pedido</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">
                    {t('order.orderNumber')}
                  </p>
                  <p className="font-mono font-semibold">{order.order_number}</p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge variant="warning">{t(`order.status.${order.status}`)}</Badge>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Método de Pagamento
                  </p>
                  <p className="font-semibold">
                    {isPix ? t('checkout.payment.pix') : t('checkout.payment.boleto')}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">{t('order.total')}</p>
                  <Price value={totalAmount} className="text-lg font-bold" />
                </div>
              </div>
            </CardContent>
          </Card>

          {isPix && order.payment_details && (
            <Card>
              <CardHeader>
                <CardTitle>{t('order.pix.title')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {t('order.pix.instructions')}
                </p>

                {order.payment_details.pix_qr_code && (
                  <div className="flex justify-center">
                    <div className="rounded-lg border bg-white p-4">
                      <img
                        src={order.payment_details.pix_qr_code}
                        alt="QR Code Pix"
                        className="h-64 w-64"
                      />
                    </div>
                  </div>
                )}

                <Separator />

                <div>
                  <p className="mb-2 text-sm font-medium">Código Pix:</p>
                  <div className="flex gap-2">
                    <code className="flex-1 overflow-x-auto rounded-md bg-muted p-3 text-xs">
                      {order.payment_details.pix_code}
                    </code>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleCopyPix}
                      aria-label={t('order.pix.copyCode')}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  {copiedPix && (
                    <p className="mt-2 text-sm text-green-600">
                      {t('order.pix.codeCopied')}
                    </p>
                  )}
                </div>

                <p className="text-xs text-muted-foreground">
                  {t('order.pix.expiresIn')}
                </p>
              </CardContent>
            </Card>
          )}

          {isBoleto && order.payment_details && (
            <Card>
              <CardHeader>
                <CardTitle>{t('order.boleto.title')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {t('order.boleto.instructions')}
                </p>

                <div>
                  <p className="mb-2 text-sm font-medium">
                    {t('order.boleto.barcode')}:
                  </p>
                  <div className="flex gap-2">
                    <code className="flex-1 overflow-x-auto rounded-md bg-muted p-3 text-xs">
                      {order.payment_details.boleto_barcode}
                    </code>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleCopyBoleto}
                      aria-label={t('order.boleto.copyBarcode')}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  {copiedBoleto && (
                    <p className="mt-2 text-sm text-green-600">
                      {t('order.boleto.barcodeCopied')}
                    </p>
                  )}
                </div>

                {order.payment_details.boleto_url && (
                  <Button
                    variant="outline"
                    className="w-full gap-2"
                    asChild
                  >
                    <a
                      href={order.payment_details.boleto_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Download className="h-4 w-4" />
                      {t('order.boleto.downloadPDF')}
                    </a>
                  </Button>
                )}

                {order.payment_details.boleto_due_date && (
                  <p className="text-xs text-muted-foreground">
                    {t('order.boleto.dueDate')}:{' '}
                    {new Date(order.payment_details.boleto_due_date).toLocaleDateString('pt-BR')}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          <div className="flex justify-center">
            <Button variant="outline" asChild>
              <Link href="/">{t('order.backToHome')}</Link>
            </Button>
          </div>
        </div>
      </Container>
    </main>
  );
}
