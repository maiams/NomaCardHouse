'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { validateCPF, validateCEP } from '@/lib/utils';
import type { CheckoutRequest } from '@/lib/api/types';

interface CheckoutFormProps {
  onSubmit: (data: CheckoutRequest) => Promise<void>;
  isSubmitting: boolean;
}

interface FormErrors {
  [key: string]: string;
}

const BRAZILIAN_STATES = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO',
];

export function CheckoutForm({ onSubmit, isSubmitting }: CheckoutFormProps) {
  const t = useTranslations();
  const [formData, setFormData] = useState<CheckoutRequest>({
    customer: {
      full_name: '',
      email: '',
      phone: '',
      cpf: '',
    },
    shipping_address: {
      zip_code: '',
      street: '',
      number: '',
      complement: '',
      neighborhood: '',
      city: '',
      state: '',
    },
    payment_method: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.customer.full_name.trim()) {
      newErrors.full_name = t('checkout.form.required');
    }

    if (!formData.customer.email.trim()) {
      newErrors.email = t('checkout.form.required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.customer.email)) {
      newErrors.email = t('checkout.form.invalidEmail');
    }

    if (!formData.customer.phone.trim()) {
      newErrors.phone = t('checkout.form.required');
    }

    if (!formData.customer.cpf.trim()) {
      newErrors.cpf = t('checkout.form.required');
    } else if (!validateCPF(formData.customer.cpf)) {
      newErrors.cpf = t('checkout.form.invalidCPF');
    }

    if (!formData.shipping_address.zip_code.trim()) {
      newErrors.zip_code = t('checkout.form.required');
    } else if (!validateCEP(formData.shipping_address.zip_code)) {
      newErrors.zip_code = t('checkout.form.invalidZipCode');
    }

    if (!formData.shipping_address.street.trim()) {
      newErrors.street = t('checkout.form.required');
    }

    if (!formData.shipping_address.number.trim()) {
      newErrors.number = t('checkout.form.required');
    }

    if (!formData.shipping_address.neighborhood.trim()) {
      newErrors.neighborhood = t('checkout.form.required');
    }

    if (!formData.shipping_address.city.trim()) {
      newErrors.city = t('checkout.form.required');
    }

    if (!formData.shipping_address.state) {
      newErrors.state = t('checkout.form.required');
    }

    if (!formData.payment_method) {
      newErrors.payment_method = t('checkout.payment.selectMethod');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    await onSubmit(formData);
  };

  const updateCustomer = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      customer: { ...prev.customer, [field]: value },
    }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const updateAddress = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      shipping_address: { ...prev.shipping_address, [field]: value },
    }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const updatePaymentMethod = (value: string) => {
    setFormData((prev) => ({ ...prev, payment_method: value }));
    if (errors.payment_method) {
      setErrors((prev) => ({ ...prev, payment_method: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('checkout.shippingInfo')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Label htmlFor="full_name">{t('checkout.form.fullName')}</Label>
              <Input
                id="full_name"
                value={formData.customer.full_name}
                onChange={(e) => updateCustomer('full_name', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.full_name}
              />
              {errors.full_name && (
                <p className="mt-1 text-sm text-destructive">{errors.full_name}</p>
              )}
            </div>

            <div>
              <Label htmlFor="email">{t('checkout.form.email')}</Label>
              <Input
                id="email"
                type="email"
                value={formData.customer.email}
                onChange={(e) => updateCustomer('email', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.email}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-destructive">{errors.email}</p>
              )}
            </div>

            <div>
              <Label htmlFor="phone">{t('checkout.form.phone')}</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.customer.phone}
                onChange={(e) => updateCustomer('phone', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.phone}
              />
              {errors.phone && (
                <p className="mt-1 text-sm text-destructive">{errors.phone}</p>
              )}
            </div>

            <div>
              <Label htmlFor="cpf">{t('checkout.form.cpf')}</Label>
              <Input
                id="cpf"
                value={formData.customer.cpf}
                onChange={(e) => updateCustomer('cpf', e.target.value)}
                disabled={isSubmitting}
                placeholder="000.000.000-00"
                aria-invalid={!!errors.cpf}
              />
              {errors.cpf && (
                <p className="mt-1 text-sm text-destructive">{errors.cpf}</p>
              )}
            </div>

            <div>
              <Label htmlFor="zip_code">{t('checkout.form.zipCode')}</Label>
              <Input
                id="zip_code"
                value={formData.shipping_address.zip_code}
                onChange={(e) => updateAddress('zip_code', e.target.value)}
                disabled={isSubmitting}
                placeholder="00000-000"
                aria-invalid={!!errors.zip_code}
              />
              {errors.zip_code && (
                <p className="mt-1 text-sm text-destructive">{errors.zip_code}</p>
              )}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-4">
            <div className="sm:col-span-3">
              <Label htmlFor="street">{t('checkout.form.street')}</Label>
              <Input
                id="street"
                value={formData.shipping_address.street}
                onChange={(e) => updateAddress('street', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.street}
              />
              {errors.street && (
                <p className="mt-1 text-sm text-destructive">{errors.street}</p>
              )}
            </div>

            <div>
              <Label htmlFor="number">{t('checkout.form.number')}</Label>
              <Input
                id="number"
                value={formData.shipping_address.number}
                onChange={(e) => updateAddress('number', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.number}
              />
              {errors.number && (
                <p className="mt-1 text-sm text-destructive">{errors.number}</p>
              )}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="complement">{t('checkout.form.complement')}</Label>
              <Input
                id="complement"
                value={formData.shipping_address.complement}
                onChange={(e) => updateAddress('complement', e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <Label htmlFor="neighborhood">{t('checkout.form.neighborhood')}</Label>
              <Input
                id="neighborhood"
                value={formData.shipping_address.neighborhood}
                onChange={(e) => updateAddress('neighborhood', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.neighborhood}
              />
              {errors.neighborhood && (
                <p className="mt-1 text-sm text-destructive">{errors.neighborhood}</p>
              )}
            </div>

            <div>
              <Label htmlFor="city">{t('checkout.form.city')}</Label>
              <Input
                id="city"
                value={formData.shipping_address.city}
                onChange={(e) => updateAddress('city', e.target.value)}
                disabled={isSubmitting}
                aria-invalid={!!errors.city}
              />
              {errors.city && (
                <p className="mt-1 text-sm text-destructive">{errors.city}</p>
              )}
            </div>

            <div>
              <Label htmlFor="state">{t('checkout.form.state')}</Label>
              <Select
                value={formData.shipping_address.state}
                onValueChange={(value) => updateAddress('state', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger id="state" aria-invalid={!!errors.state}>
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  {BRAZILIAN_STATES.map((state) => (
                    <SelectItem key={state} value={state}>
                      {state}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.state && (
                <p className="mt-1 text-sm text-destructive">{errors.state}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('checkout.paymentMethod')}</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            value={formData.payment_method}
            onValueChange={updatePaymentMethod}
            disabled={isSubmitting}
          >
            <SelectTrigger aria-invalid={!!errors.payment_method}>
              <SelectValue placeholder={t('checkout.payment.selectMethod')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="PIX">{t('checkout.payment.pix')}</SelectItem>
              <SelectItem value="BOLETO">{t('checkout.payment.boleto')}</SelectItem>
            </SelectContent>
          </Select>
          {errors.payment_method && (
            <p className="mt-2 text-sm text-destructive">{errors.payment_method}</p>
          )}
        </CardContent>
      </Card>

      <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? t('checkout.processing') : t('checkout.placeOrder')}
      </Button>
    </form>
  );
}
