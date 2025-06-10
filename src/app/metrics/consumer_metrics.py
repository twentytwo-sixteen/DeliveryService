from prometheus_client import Counter

class ConsumerMetrics:
    def __init__(self):
        self.messages_processed = Counter(
            'consumer_messages_processed_total',
            'Total messages processed'
        )
        self.invalid_messages = Counter(
            'consumer_invalid_messages_total',
            'Total invalid messages'
        )
        self.processing_errors = Counter(
            'consumer_processing_errors_total',
            'Total processing errors'
        )

consumer_metrics = ConsumerMetrics()