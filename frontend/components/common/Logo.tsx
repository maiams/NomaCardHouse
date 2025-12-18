import { Link } from '@/lib/i18n/routing';

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-2 font-bold transition-opacity hover:opacity-80 ${className}`}
    >
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <span className="text-lg">N</span>
      </div>
      <span className="text-xl">Noma Card House</span>
    </Link>
  );
}
