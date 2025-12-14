'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { generateSlug } from '@/lib/utils'

interface Category {
  id: string
  name: string
}

export default function NewProductPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])

  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    price: '',
    stockQty: '',
    categoryId: '',
    isSealed: false,
    isSingle: false,
    cardNumber: '',
    rarity: '',
    condition: '',
    featured: false,
  })

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const res = await fetch('/api/categories')
      const data = await res.json()
      setCategories(data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          slug: formData.slug || generateSlug(formData.name),
        }),
      })

      if (!res.ok) throw new Error('Failed to create product')

      router.push('/admin/products')
    } catch (error) {
      console.error('Error creating product:', error)
      alert('Erro ao criar produto')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Novo Produto</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Nome do Produto"
            type="text"
            required
            value={formData.name}
            onChange={(e) => {
              setFormData({
                ...formData,
                name: e.target.value,
                slug: generateSlug(e.target.value),
              })
            }}
          />

          <Input
            label="Slug (URL amigável)"
            type="text"
            required
            value={formData.slug}
            onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Descrição
          </label>
          <textarea
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            rows={4}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Input
            label="Preço (R$)"
            type="number"
            step="0.01"
            required
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
          />

          <Input
            label="Quantidade em Estoque"
            type="number"
            required
            value={formData.stockQty}
            onChange={(e) => setFormData({ ...formData, stockQty: e.target.value })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoria
            </label>
            <select
              required
              value={formData.categoryId}
              onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Selecione...</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Input
            label="Número do Card (opcional)"
            type="text"
            value={formData.cardNumber}
            onChange={(e) => setFormData({ ...formData, cardNumber: e.target.value })}
          />

          <Input
            label="Raridade (opcional)"
            type="text"
            placeholder="Ex: Comum, Rara, Mítica"
            value={formData.rarity}
            onChange={(e) => setFormData({ ...formData, rarity: e.target.value })}
          />

          <Input
            label="Condição (opcional)"
            type="text"
            placeholder="Ex: NM, SP, MP"
            value={formData.condition}
            onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
          />
        </div>

        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.isSealed}
              onChange={(e) => setFormData({ ...formData, isSealed: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Produto Selado</span>
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.isSingle}
              onChange={(e) => setFormData({ ...formData, isSingle: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Card Avulso</span>
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.featured}
              onChange={(e) => setFormData({ ...formData, featured: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Produto em Destaque</span>
          </label>
        </div>

        <div className="flex gap-4">
          <Button type="submit" disabled={loading}>
            {loading ? 'Salvando...' : 'Criar Produto'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push('/admin/products')}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
