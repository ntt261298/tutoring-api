from flask import jsonify
import braintree
from marshmallow import fields

from main import app, auth, errors
from main.engines import monetization
from main.engines.payment_flow import PaymentFlow
from main.schemas.base import BaseSchema
from main.models.subscription_package import SubscriptionPackageModel
from main.libs.validate_args import validate_args


@app.route('/user/me/payments/braintree', methods=['GET'])
@auth.requires_token_auth('user')
def generate_braintree_client_token(user):
    """Generate a client token which is a signed data blob that includes configuration and authorization information
    required by the Braintree client SDK. These should not be reused; a new client token should be generated for each
    request that's sent to Braintree."""
    customer = monetization.get_or_create_braintree_customer(user.id)
    if not customer:
        raise errors.BraintreeError('Braintree exception')

    # Generate the client token
    try:
        client_token = braintree.ClientToken.generate({
            'customer_id': customer.id
        })
    except Exception as e:
        raise errors.BraintreeError()

    return jsonify({
        'client_token': client_token
    })


class CreditPurchaseSchema(BaseSchema):
    payment_method_nonce = fields.String(required=True)
    package_id = fields.Integer(required=True)


@app.route('/user/me/transactions', methods=['POST'])
@auth.requires_token_auth('user')
@validate_args(CreditPurchaseSchema())
def purchase_credits(user, args):
    """Purchase a package"""
    current_package = SubscriptionPackageModel.query.get(args['package_id'])

    try:
        payment_flow = PaymentFlow(
            user_id=user.id,
            payment_method_nonce=args.get('payment_method_nonce'),
            number_of_questions=current_package.number_of_questions,
            amount=current_package.price,
            package_name=current_package.name,
            package_type=current_package.type,
        )
        payment_flow.process()
    except Exception:
        raise errors.BadRequest(message='An error has occurred when processing your payment')

    return jsonify({})
