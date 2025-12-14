'use client'

import Link from 'next/link'
import { Card } from '@/components/ui/Card'
import { Package, ShoppingCart, Tags, Upload } from 'lucide-react'

export default function AdminDashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Painel Administrativo</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/admin/products">
          <Card hover className="p-6 cursor-pointer">
            <Package className="w-12 h-12 text-primary-600 mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Produtos</h2>
            <p className="text-gray-600">Gerenciar produtos e estoque</p>
          </Card>
        </Link>

        <Link href="/admin/categories">
          <Card hover className="p-6 cursor-pointer">
            <Tags className="w-12 h-12 text-primary-600 mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Categorias</h2>
            <p className="text-gray-600">Gerenciar categorias</p>
          </Card>
        </Link>

        <Link href="/admin/orders">
          <Card hover className="p-6 cursor-pointer">
            <ShoppingCart className="w-12 h-12 text-primary-600 mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Pedidos</h2>
            <p className="text-gray-600">Visualizar e gerenciar pedidos</p>
          </Card>
        </Link>

        <Link href="/admin/products/new">
          <Card hover className="p-6 cursor-pointer">
            <Upload className="w-12 h-12 text-primary-600 mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Novo Produto</h2>
            <p className="text-gray-600">Cadastrar novo produto</p>
          </Card>
        </Link>
      </div>
    </div>
  )
}
