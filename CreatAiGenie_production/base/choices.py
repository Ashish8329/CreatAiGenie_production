from enum import Enum

class ChoiceEnum(Enum):
    @classmethod
    def get_value(cls, member):
        return cls[member].value[0]
    
    @classmethod
    def choices(cls):
        return [(member.value[0], member.value[1]) for member in cls]

class Status(ChoiceEnum):
    PENDING = ("pending", "Pending")
    COMPLETED = ("completed", "Completed")
    REJECTED = ("rejected", "Rejected")


class PaymentStatus(ChoiceEnum):
    CREATED = ("created", "Created")
    PAID = ("paid", "Paid")
    FAILED = ("failed", "Failed")