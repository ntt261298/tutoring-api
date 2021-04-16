from datetime import datetime, timedelta

from main import errors, db
from main.enums import SubscriptionType, SubscriptionStatus
from main.engines import monetization
from main.models.user import UserModel
from main.models.transaction import TransactionModel
from main.models.user_subscription_package import UserSubscriptionPackageModel


class PaymentFlow:
    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.package_price = kwargs.get('amount')
        self.payment_method_nonce = kwargs.get('payment_method_nonce')
        self.package_name = kwargs.get('package_name')
        self.package_type = kwargs.get('package_type')
        self.number_of_questions = kwargs.get('number_of_questions')

        self.user = None
        self.set_user()

    def set_user(self):
        if self.user_id is None:
            raise Exception('User not found.')
        self.user = UserModel.query.get(self.user_id)
        if self.user is None:
            raise Exception('User not found.')

    def get_package_expired_in(self):
        expired_in = datetime.utcnow()
        if self.package_type == SubscriptionType.MONTHLY:
            expired_in = datetime.utcnow() + timedelta(days=30)
        elif self.package_type == SubscriptionType.YEARLY:
            expired_in = datetime.utcnow() + timedelta(days=365)
        return expired_in

    def handle_charge_money_successfully(self):
        transaction = TransactionModel(
            user_id=self.user_id,
            package_name=self.package_name,
            package_type=self.package_type,
            amount=self.package_price,
        )

        transaction.save_to_db()

        if self.package_type != SubscriptionType.BUNDLE:
            current_user_subscription_package = UserSubscriptionPackageModel.query \
                .filter(UserSubscriptionPackageModel.user_id == self.user_id) \
                .first()

            # Terminate current subscription
            if current_user_subscription_package:
                current_user_subscription_package.status = SubscriptionStatus.TERMINATED
                db.session.commit()

            # Create new subscription
            user_subscription_package = UserSubscriptionPackageModel(
                user_id=self.user_id,
                package_name=self.package_name,
                package_type=self.package_type,
                amount=self.package_price,
                expired_in=self.get_package_expired_in(),
                number_of_questions=self.number_of_questions,
                status=SubscriptionStatus.ACTIVE,
            )
            user_subscription_package.save_to_db()
        else:
            # Add questions for user
            user = UserModel.query.get(self.user_id)
            user.paid_credit_balance += self.number_of_questions
            db.session.commit()

    def process(self):
        """Process to get money from user and give him/her our products."""
        # Create customer on Braintree.
        customer = monetization.get_or_create_braintree_customer(self.user_id)
        try:
            charge_money_result = monetization.charge_customer_some_money(
                customer.id, self.package_price, self.payment_method_nonce
            )
        except Exception:
            raise errors.BraintreeError()

        if not charge_money_result.is_success:
            raise errors.BraintreeError()
        else:
            self.handle_charge_money_successfully()
