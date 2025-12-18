'use client';

import { Minus, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface QuantityStepperProps {
  value: number;
  min?: number;
  max?: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function QuantityStepper({
  value,
  min = 1,
  max = 99,
  onChange,
  disabled = false,
}: QuantityStepperProps) {
  const handleIncrement = () => {
    if (value < max) {
      onChange(value + 1);
    }
  };

  const handleDecrement = () => {
    if (value > min) {
      onChange(value - 1);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);

    if (isNaN(newValue)) {
      onChange(min);
      return;
    }

    if (newValue < min) {
      onChange(min);
    } else if (newValue > max) {
      onChange(max);
    } else {
      onChange(newValue);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={handleDecrement}
        disabled={disabled || value <= min}
        aria-label="Diminuir quantidade"
      >
        <Minus className="h-4 w-4" />
      </Button>

      <Input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={handleInputChange}
        disabled={disabled}
        className="h-8 w-16 text-center"
        aria-label="Quantidade"
      />

      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={handleIncrement}
        disabled={disabled || value >= max}
        aria-label="Aumentar quantidade"
      >
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  );
}
