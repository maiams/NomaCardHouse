import { PrismaClient } from '@prisma/client'
import { hash } from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding database...')

  // Create admin user
  const admin = await prisma.user.upsert({
    where: { email: 'admin@nomacardhouse.com' },
    update: {},
    create: {
      email: 'admin@nomacardhouse.com',
      name: 'Admin',
      password: await hash('admin123', 10),
      role: 'admin',
    },
  })

  console.log('Created admin user:', admin.email)

  // Create categories
  const categories = await Promise.all([
    prisma.category.upsert({
      where: { slug: 'booster-packs' },
      update: {},
      create: {
        name: 'Booster Packs',
        slug: 'booster-packs',
        description: 'Pacotes de cartas lacrados',
      },
    }),
    prisma.category.upsert({
      where: { slug: 'single-cards' },
      update: {},
      create: {
        name: 'Cards Avulsos',
        slug: 'single-cards',
        description: 'Cartas individuais para colecionadores',
      },
    }),
    prisma.category.upsert({
      where: { slug: 'accessories' },
      update: {},
      create: {
        name: 'Acessórios',
        slug: 'accessories',
        description: 'Sleeves, deck boxes, playmats e mais',
      },
    }),
    prisma.category.upsert({
      where: { slug: 'sealed-products' },
      update: {},
      create: {
        name: 'Produtos Selados',
        slug: 'sealed-products',
        description: 'Caixas, displays e produtos lacrados',
      },
    }),
  ])

  console.log('Created categories:', categories.length)

  // Create sample products
  const products = await Promise.all([
    prisma.product.upsert({
      where: { slug: 'magic-the-gathering-booster-pack' },
      update: {},
      create: {
        name: 'Magic: The Gathering - Booster Pack',
        slug: 'magic-the-gathering-booster-pack',
        description: 'Pacote com 15 cartas de Magic: The Gathering',
        price: 29.90,
        stockQty: 50,
        categoryId: categories[0].id,
        isSealed: true,
        featured: true,
      },
    }),
    prisma.product.upsert({
      where: { slug: 'pokemon-tcg-booster-pack' },
      update: {},
      create: {
        name: 'Pokémon TCG - Booster Pack',
        slug: 'pokemon-tcg-booster-pack',
        description: 'Pacote com 10 cartas de Pokémon',
        price: 24.90,
        stockQty: 75,
        categoryId: categories[0].id,
        isSealed: true,
        featured: true,
      },
    }),
    prisma.product.upsert({
      where: { slug: 'ultra-pro-sleeves-100ct' },
      update: {},
      create: {
        name: 'Ultra Pro Sleeves (100 unidades)',
        slug: 'ultra-pro-sleeves-100ct',
        description: 'Protetor de cartas premium',
        price: 15.90,
        stockQty: 200,
        categoryId: categories[2].id,
        featured: false,
      },
    }),
    prisma.product.upsert({
      where: { slug: 'deck-box-ultimate-guard' },
      update: {},
      create: {
        name: 'Deck Box Ultimate Guard',
        slug: 'deck-box-ultimate-guard',
        description: 'Caixa para deck com capacidade para 100 cartas',
        price: 39.90,
        stockQty: 30,
        categoryId: categories[2].id,
        featured: false,
      },
    }),
    prisma.product.upsert({
      where: { slug: 'black-lotus-nm' },
      update: {},
      create: {
        name: 'Black Lotus',
        slug: 'black-lotus-nm',
        description: 'Carta rara de Magic: The Gathering',
        price: 45000.00,
        stockQty: 1,
        categoryId: categories[1].id,
        isSingle: true,
        cardNumber: 'LEA-232',
        rarity: 'Mítica',
        condition: 'NM',
        featured: true,
      },
    }),
    prisma.product.upsert({
      where: { slug: 'charizard-base-set' },
      update: {},
      create: {
        name: 'Charizard - Base Set',
        slug: 'charizard-base-set',
        description: 'Carta holográfica rara de Pokémon',
        price: 2500.00,
        stockQty: 2,
        categoryId: categories[1].id,
        isSingle: true,
        cardNumber: '4/102',
        rarity: 'Rara Holográfica',
        condition: 'SP',
        featured: true,
      },
    }),
  ])

  console.log('Created products:', products.length)

  console.log('Seeding completed!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
