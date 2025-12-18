'use client';

import { useTranslations } from 'next-intl';
import { ShoppingCart, User, Menu } from 'lucide-react';
import { Container } from '@/components/common/Container';
import { Logo } from '@/components/common/Logo';
import { Button } from '@/components/ui/button';
import { Link } from '@/lib/i18n/routing';
import { useState } from 'react';

export function Header() {
  const t = useTranslations('nav');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { href: '/', label: t('home') },
    { href: '/catalog', label: t('catalog') },
  ];

  return (
    <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <Container>
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Logo />

          {/* Desktop Navigation */}
          <nav className="hidden md:flex md:items-center md:gap-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              aria-label={t('cart')}
              asChild
            >
              <Link href="/cart">
                <ShoppingCart className="h-5 w-5" />
              </Link>
            </Button>

            <Button
              variant="ghost"
              size="icon"
              aria-label={t('account')}
              asChild
            >
              <Link href="/account">
                <User className="h-5 w-5" />
              </Link>
            </Button>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Menu"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="border-t py-4 md:hidden">
            <div className="flex flex-col gap-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>
        )}
      </Container>
    </header>
  );
}
