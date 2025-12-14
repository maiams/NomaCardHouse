'use client'

import Link from 'next/link'
import { useCartStore } from '@/store/cart'
import { ShoppingCart, Menu, Search } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const totalItems = useCartStore((state) => state.getTotalItems())

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center">
            <h1 className="text-2xl font-bold text-primary-600">
              Noma Card House
            </h1>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            <Link href="/products" className="text-gray-700 hover:text-primary-600 transition">
              Produtos
            </Link>
            <Link href="/categories" className="text-gray-700 hover:text-primary-600 transition">
              Categorias
            </Link>
            <Link href="/about" className="text-gray-700 hover:text-primary-600 transition">
              Sobre
            </Link>
            <Link href="/contact" className="text-gray-700 hover:text-primary-600 transition">
              Contato
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-700 hover:text-primary-600 transition">
              <Search className="w-5 h-5" />
            </button>

            <Link href="/cart" className="relative p-2 text-gray-700 hover:text-primary-600 transition">
              <ShoppingCart className="w-6 h-6" />
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {totalItems}
                </span>
              )}
            </Link>

            <button
              className="md:hidden p-2 text-gray-700"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="flex flex-col space-y-4">
              <Link href="/products" className="text-gray-700 hover:text-primary-600 transition">
                Produtos
              </Link>
              <Link href="/categories" className="text-gray-700 hover:text-primary-600 transition">
                Categorias
              </Link>
              <Link href="/about" className="text-gray-700 hover:text-primary-600 transition">
                Sobre
              </Link>
              <Link href="/contact" className="text-gray-700 hover:text-primary-600 transition">
                Contato
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}
