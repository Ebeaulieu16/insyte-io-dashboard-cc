# Setting Up Stripe Webhooks for Payment Tracking

This guide will help you set up Stripe webhooks to accurately track payments and link them to your application data.

## Why Use Metadata with Stripe?

Adding metadata to your Stripe payments allows you to:

1. **Track the source of payments** - Know which marketing campaign, link, or video generated the sale
2. **Maintain data continuity** - Connect payment data with your user journey tracking
3. **Improve analytics accuracy** - Get precise attribution for your revenue sources
4. **Prevent errors** - Ensure all payments are properly linked to their source

## Setting Up Your Webhook

### 1. Log in to your Stripe Dashboard

Go to [https://dashboard.stripe.com/](https://dashboard.stripe.com/) and log in to your account.

### 2. Configure a Webhook Endpoint

1. In the Stripe Dashboard, navigate to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. For the endpoint URL, enter your API URL with the `/webhook/stripe` path:
   ```
   https://your-api-domain.com/webhook/stripe
   ```
4. Under "Events to send", select at minimum:
   - `payment_intent.succeeded`

   You can add more events if you want to track other payment activities.

5. Click **Add endpoint** to create the webhook

### 3. Get Your Webhook Secret

1. After creating the webhook, click on it to view details
2. Click **Reveal** next to the "Signing secret" field
3. Copy this value and add it to your environment variables:
   ```
   STRIPE_WEBHOOK_SECRET=your_webhook_secret
   ```

### 4. Test the Webhook

1. In the Stripe Dashboard, go to your webhook details
2. Click the **Send test webhook** button
3. Select `payment_intent.succeeded` event type
4. Click **Send test webhook**
5. Check your application logs to confirm receipt

## Adding Metadata to Your Payments

### For Payment Intents (Server-side)

When creating a payment intent in your server code:

```javascript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,  // $20.00
  currency: 'usd',
  metadata: {
    slug: 'your-video-link-slug',
    email: 'customer@example.com'
  }
});
```

### For Checkout Sessions

When creating a checkout session:

```javascript
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price: 'price_12345',
    quantity: 1,
  }],
  mode: 'payment',
  success_url: 'https://your-site.com/success',
  cancel_url: 'https://your-site.com/cancel',
  payment_intent_data: {
    metadata: {
      slug: 'your-video-link-slug',
      email: '{{customer_email}}'  // Stripe will automatically populate the customer's email
    }
  }
});
```

### For Payment Links

1. Create a new payment link in the Stripe Dashboard
2. Click the **Additional options** dropdown
3. Under **Developer/Metadata**, add your slug and other tracking information

## Verifying the Setup

After setting up your webhook and adding metadata to your payments:

1. Make a test payment through your application
2. Check your application logs for webhook events
3. Verify the payment record in your database includes the correct metadata
4. Check your application's payment analytics to ensure the payment is attributed correctly

## Troubleshooting

If you're not seeing webhook events:

1. Ensure your application is publicly accessible (Stripe cannot send webhooks to localhost)
2. Verify the webhook URL is correct in the Stripe Dashboard
3. Check application logs for any webhook signature verification errors
4. Ensure the `STRIPE_WEBHOOK_SECRET` environment variable is correctly set

For metadata issues:

1. Double-check that metadata is being added in your payment creation code
2. Test with simple static values before using dynamic values
3. Review Stripe Dashboard logs for successful payment events and check if metadata appears 