from abc import ABC, abstractmethod
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

channels = {
    "email": EmailChannel(),
    "sms": SMSChannel(),
    "push": PushChannel()
}

class Notification:

    def __init__(self, recipient, message, priority):
        self.recipient = recipient
        self.message = message
        self.priority = priority

class NotificationChannel(ABC):

    @abstractmethod
    def send(self, notification):
        pass

class EmailChannel(NotificationChannel):

    def send(self,notification):
        print(f"Sending EMAIL to {notification.recipient}: {notification.message}")


class SMSChannel(NotificationChannel):

    def send(self, notification):
        print(f"Sending SMS to {notification.recipient}: {notification.message}")

class RetryHandler:

    def __init__(self, max_retries):
        self.max_retries = max_retries

    def execute(self, channel, notification):
        try:
            channel.send(notification)
            return True
        except Exception:
            print("there was an exception, retrying...")
            for i in range(self.max_retries):
                try:
                    channel.send(notification)
                    return True
                except Exception:
                    print(f"Retry {i + 1} failed")

        print("Failed after maximum retries")     
        return False

class NotificationService:
    def __init__(self,channels, router,rhandler):
        self.channels=channels
        self.router=router
        self.rhandler=rhandler

    def send(self,notification):
        channels=self.router.get_channels(notification)
        hm={}
        for channel in channels:
            hm[channel] = self.rhandler.execute(self.channels[channel],notification)
        return hm
class UnstableEmailChannel(NotificationChannel):

    def __init__(self):
        self.attempts = 0

    def send(self, notification):
        self.attempts += 1

        if self.attempts < 3:
            raise Exception("Temporary email server failure")

        print(f"Email sent to {notification.recipient}")

class NotificationRouter:

    def __init__(self):
        self.routes = {
            Priority.LOW: ["email"],
            Priority.MEDIUM: ["email", "push"],
            Priority.HIGH: ["sms", "push"]
        }

    def get_channels(self, notification):
        return self.routes[notification.priority]

notification = Notification(
    "user@example.com",
    "Your order is confirmed",
    Priority.HIGH
)

channel = UnstableEmailChannel()
retry_handler = RetryHandler(max_retries=3)

service = NotificationService(channel, retry_handler)

result = service.send(notification)

print("Delivery status:", result)
print("Total attempts:", channel.attempts)