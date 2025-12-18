import { formatPrice } from '@/lib/utils';

interface PriceProps {
  value: number | string;
  className?: string;
  showCurrency?: boolean;
}

export function Price({ value, className, showCurrency = true }: PriceProps) {
  const numericValue = typeof value === 'string' ? parseFloat(value) : value;
  const formatted = formatPrice(numericValue);

  return <span className={className}>{formatted}</span>;
}
