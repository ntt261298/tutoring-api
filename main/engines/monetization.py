import braintree

from config import config

# Configure Braintree SDK
braintree.Configuration.configure(environment=config.BRAINTREE_ENVIRONMENT,
                                  merchant_id=config.BRAINTREE_MERCHANT_ID,
                                  public_key=config.BRAINTREE_PUBLIC_KEY,
                                  private_key=config.BRAINTREE_PRIVATE_KEY)


# Get Braintree customer ID
def get_customer_id(user_id):
    return str(user_id)


# Get a Braintree customer by user ID
def get_braintree_customer(user_id):
    customer_id = get_customer_id(user_id)
    return get_braintree_customer_by_id(customer_id)


def get_braintree_customer_by_id(customer_id):
    try:
        customer = braintree.Customer.find(customer_id)
    except Exception:  # pragma: no cover
        customer = None
    return customer


# Create a Braintree customer by customer ID
def create_braintree_customer(customer_id, payment_method_nonce=None):
    payload = {
        'id': customer_id
    }
    if payment_method_nonce:
        payload['payment_method_nonce'] = payment_method_nonce

    try:
        result = braintree.Customer.create(payload)
        if result.is_success:
            return result.customer
    except Exception:  # pragma: no cover
        return None


def get_or_create_braintree_customer(asker_id, payment_method_nonce=None):
    customer = get_braintree_customer(asker_id)
    # If braintree customer did not exist, create new one
    if not customer:
        customer_id = get_customer_id(asker_id)
        customer = create_braintree_customer(customer_id, payment_method_nonce)
    return customer


def create_braintree_customer_payment_method(customer_id, payment_method_nonce):
    braintree.PaymentMethod.create({
        'customer_id': customer_id,
        'payment_method_nonce': payment_method_nonce,
        'options': {
            'make_default': True
        }
    })


def charge_money(nonce=None, amount=0, store_in_vault=False):
    # Payment method nonce or token must be provided
    if nonce is None:
        raise Exception('Payment method nonce must be provided')
    # Amount of money cannot be less than or equal to zero
    if amount <= 0:
        raise Exception('Amount must be greater than zero')
    # Payload to be sent to Braintree. We must type cast amount to string or else it's not gonna work. We set
    # submit_for_settlement to true to indicate that we wanna charge the payment method immediately.
    payload = {
        'amount': '%.2f' % round(amount, 2),  # Braintree only accept amount with 2 numbers after the point
        'options': {
            'submit_for_settlement': True
        },
        'customer': {
            'email': config.BRAINTREE_EMAIL_SUPPORT
        }
    }
    if nonce is not None:
        payload['payment_method_nonce'] = nonce
    # Store the payment method in vault so we can use it to charge the customer later
    if store_in_vault is True:
        payload['options']['store_in_vault'] = True
    # Ask Braintree to charge the payment method. Please note that the following line of code simply means we
    # successfully sent the request to Braintree. You need to check the result returned by this method to know if the
    # charge is successful or failed
    result = braintree.Transaction.sale(payload)
    return result


def charge_customer_some_money(customer_id, amount, payment_method_nonce=None):
    customer = get_braintree_customer_by_id(customer_id)
    if customer is None:
        raise Exception('Cannot find Braintree customer')

    result = charge_money(nonce=payment_method_nonce, amount=amount, store_in_vault=True)
    return result
