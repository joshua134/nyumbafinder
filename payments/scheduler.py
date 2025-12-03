import datetime
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone as pytz_timezone
from payments.models import Payment


def expire_old_payments():
    """ Expire payments older than 1.5 years. """
    cutoff_date = timezone.now() - datetime.timedelta(days=547) # 1.5 years
    expired_payments = Payment.objects.filter(is_verified = True, payment_date__lte=cutoff_date)


    for payment in expired_payments:
        payment.status = 'unpaid'
        payment.is_verified = False
        if payment.house:
            payment.house.is_active = False
            payment.house.payment_status = 'unpaid'
            payment.house.save()
        payment.save()
        print(f"Expired payment {payment.id} for user {payment.user.username}")

def start():
    scheduler = BackgroundScheduler()
    # run daily at midnight
    scheduler.add_job(expire_old_payments, 'cron', hour=0,minute=0, timezone=pytz_timezone('Africa/Nairobi'))
    # scheduler.add_job(expire_old_payments, 'interval', minutes=0.5, timezone=pytz_timezone('Africa/Nairobi'))
    scheduler.start()

