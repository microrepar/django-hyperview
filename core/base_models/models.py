from uuid import uuid4
from django.db import models
from .mixins import TimestampMixin, SoftDeleteMixin


class BaseModel(TimestampMixin, SoftDeleteMixin, models.Model):
    """Modelo base abstrato com todos os mixins."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            self.save()

    @staticmethod
    def get_columns():
        return []
