import { defineRouting } from 'next-intl/routing';
import { createSharedPathnamesNavigation } from 'next-intl/navigation';

export const routing = defineRouting({
  locales: ['pt-BR'],
  defaultLocale: 'pt-BR',
  localePrefix: 'always',
});

export const { Link, redirect, usePathname, useRouter } =
  createSharedPathnamesNavigation(routing);
