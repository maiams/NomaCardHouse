import { useTranslations } from 'next-intl';
import { Container } from '@/components/common/Container';
import { Logo } from '@/components/common/Logo';
import { Separator } from '@/components/ui/separator';
import { Link } from '@/lib/i18n/routing';

export function Footer() {
  const t = useTranslations('footer');
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    { href: '/about', label: t('about') },
    { href: '/contact', label: t('contact') },
    { href: '/terms', label: t('terms') },
    { href: '/privacy', label: t('privacy') },
  ];

  return (
    <footer className="border-t bg-muted/40">
      <Container>
        <div className="py-12 lg:py-16">
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Brand */}
            <div>
              <Logo />
              <p className="mt-4 text-sm text-muted-foreground">
                Sua loja premium de Trading Card Games no Brasil.
              </p>
            </div>

            {/* Links */}
            <div className="lg:col-span-2">
              <nav className="flex flex-wrap gap-6">
                {footerLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>

          <Separator className="my-8" />

          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-sm text-muted-foreground">
              © {currentYear} Noma Card House. {t('rights')}.
            </p>
            <div className="flex items-center gap-4">
              <span className="text-xs text-muted-foreground">
                Feito com tecnologia moderna
              </span>
            </div>
          </div>
        </div>
      </Container>
    </footer>
  );
}
