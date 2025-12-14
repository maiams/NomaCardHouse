import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { prisma } from '@/lib/prisma'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
})

export async function POST(request: NextRequest) {
  try {
    const { orderId, paymentMethod } = await request.json()

    const order = await prisma.order.findUnique({
      where: { id: orderId },
      include: { items: { include: { product: true } } },
    })

    if (!order) {
      return NextResponse.json({ error: 'Order not found' }, { status: 404 })
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: paymentMethod === 'pix'
        ? ['card']
        : ['card'],
      mode: 'payment',
      success_url: `${process.env.NEXT_PUBLIC_APP_URL}/order/${order.orderNumber}?success=true`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout?canceled=true`,
      customer_email: order.customerEmail,
      line_items: order.items.map((item) => ({
        price_data: {
          currency: 'brl',
          product_data: {
            name: item.product.name,
          },
          unit_amount: Math.round(item.price * 100),
        },
        quantity: item.quantity,
      })),
      metadata: {
        orderId: order.id,
        orderNumber: order.orderNumber,
      },
    })

    await prisma.order.update({
      where: { id: orderId },
      data: { stripePaymentId: session.id },
    })

    return NextResponse.json({ url: session.url })
  } catch (error) {
    console.error('Error creating checkout session:', error)
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    )
  }
}
