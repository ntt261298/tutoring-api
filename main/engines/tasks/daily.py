from datetime import datetime

from celery.utils.log import get_task_logger

from main import celery, db
from main.enums import SubscriptionStatus, EarningStatus
from main.models.user_subscription_package import UserSubscriptionPackageModel
from main.models.expert_earning import ExpertEarningModel

logger = get_task_logger(__name__)

TERMINATE_SUBSCRIPTION_PERIOD = 60 * 15
PAY_FOR_EXPERTS_PERIOD = 60 * 15


@celery.task()
def terminate_subscription():
    active_packages = UserSubscriptionPackageModel.query. \
        filter_by(status=SubscriptionStatus.ACTIVE). \
        all()

    for package in active_packages:
        if package.expired_in < datetime.now():
            package.status = SubscriptionStatus.TERMINATED
            db.session.add(package)
            db.session.commit()

    terminate_subscription.s().apply_async(countdown=TERMINATE_SUBSCRIPTION_PERIOD)


@celery.task()
def pay_for_experts():
    expert_earnings = ExpertEarningModel.query. \
        filter_by(status=EarningStatus.UNPAID). \
        all()

    for earning in expert_earnings:
        # Todo: Handle transactions here
        earning.status = EarningStatus.PAID
        db.session.add(earning)
        db.session.commit()

    pay_for_experts.s().apply_async(countdown=PAY_FOR_EXPERTS_PERIOD)
