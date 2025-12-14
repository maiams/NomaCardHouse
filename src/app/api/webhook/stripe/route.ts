import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { prisma } from '@/lib/prisma'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
})

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (error) {
    console.error('Webhook signature verification failed:', error)
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      const orderId = session.metadata?.orderId

      if (orderId) {
        await prisma.order.update({
          where: { id: orderId },
          data: {
            paymentStatus: 'paid',
            status: 'processing',
          },
        })

        const order = await prisma.order.findUnique({
          where: { id: orderId },
          include: { items: true },
        })

        if (order) {
          for (const item of order.items) {
            await prisma.product.update({
              where: { id: item.productId },
              data: {
                stockQty: {
                  decrement: item.quantity,
                },
              },
            })
          }
        }
      }
      break
    }

    case 'checkout.session.expired':
    case 'payment_intent.payment_failed': {
      const session = event.data.object as Stripe.Checkout.Session
      const orderId = session.metadata?.orderId

      if (orderId) {
        await prisma.order.update({
          where: { id: orderId },
          data: {
            paymentStatus: 'failed',
            status: 'cancelled',
          },
        })
      }
      break
    }
  }

  return NextResponse.json({ received: true })
}
