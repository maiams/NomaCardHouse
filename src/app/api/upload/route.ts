import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'
import { prisma } from '@/lib/prisma'
import { existsSync } from 'fs'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const productId = formData.get('productId') as string
    const isPrimary = formData.get('isPrimary') === 'true'

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    const uploadsDir = join(process.cwd(), 'public', 'uploads')
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true })
    }

    const filename = `${Date.now()}-${file.name.replace(/\s/g, '-')}`
    const filepath = join(uploadsDir, filename)

    await writeFile(filepath, buffer)

    const imageUrl = `/uploads/${filename}`

    if (productId) {
      if (isPrimary) {
        await prisma.image.updateMany({
          where: { productId },
          data: { isPrimary: false },
        })
      }

      await prisma.image.create({
        data: {
          url: imageUrl,
          alt: file.name,
          isPrimary,
          productId,
        },
      })
    }

    return NextResponse.json({ url: imageUrl })
  } catch (error) {
    console.error('Error uploading file:', error)
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    )
  }
}
