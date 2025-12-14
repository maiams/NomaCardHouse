'use client'

import Image from 'next/image'
import Link from 'next/link'
import { Card } from './ui/Card'
import { Button } from './ui/Button'
import { formatPrice } from '@/lib/utils'
import { useCartStore } from '@/store/cart'
import { ShoppingCart } from 'lucide-react'

interface ProductCardProps {
  id: string
  name: string
  price: number
  image?: string
  stockQty: number
  slug: string
}

export function ProductCard({ id, name, price, image, stockQty, slug }: ProductCardProps) {
  const addItem = useCartStore((state) => state.addItem)

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault()
    addItem({ id, name, price, image })
  }

  const inStock = stockQty > 0

  return (
    <Link href={`/products/${slug}`}>
      <Card hover className="h-full flex flex-col">
        <div className="relative aspect-square bg-gray-100">
          {image ? (
            <Image
              src={image}
              alt={name}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              Sem imagem
            </div>
          )}
          {!inStock && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <span className="text-white font-bold text-lg">Esgotado</span>
            </div>
          )}
        </div>

        <div className="p-4 flex-1 flex flex-col">
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{name}</h3>

          <div className="mt-auto">
            <p className="text-2xl font-bold text-primary-600 mb-3">
              {formatPrice(price)}
            </p>

            <Button
              onClick={handleAddToCart}
              disabled={!inStock}
              className="w-full"
              size="sm"
            >
              <ShoppingCart className="w-4 h-4 mr-2" />
              Adicionar ao Carrinho
            </Button>
          </div>
        </div>
      </Card>
    </Link>
  )
}
