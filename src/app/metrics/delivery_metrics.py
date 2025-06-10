from prometheus_client import Counter, Gauge, Histogram

class DeliveryMetrics:
    def __init__(self):
        self.processed_packages = Counter(
            'delivery_processed_packages_total',
            'Total processed packages'
        )
        self.failed_packages = Counter(
            'delivery_failed_packages_total',
            'Total failed packages'
        )
        self.usd_rate = Gauge(
            'delivery_usd_rate',
            'Current USD to RUB rate'
        )
        self.rate_fetch_errors = Counter(
            'delivery_rate_fetch_errors_total',
            'USD rate fetch errors'
        )

delivery_metrics = DeliveryMetrics()
