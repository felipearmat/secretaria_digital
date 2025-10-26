"""
Models for the appointments app.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Service(models.Model):
    """Model to represent an offered service."""
    
    name = models.CharField(max_length=255, verbose_name='Service Name')
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Description'
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name='Duration (minutes)'
    )
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Base Price'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name='Company'
    )
    actor = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name='Actor/Provider'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Service'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.actor.get_full_name()}"

    def clean(self):
        """Validates if the actor belongs to the company."""
        if self.actor and self.company:
            if self.actor.company != self.company:
                raise ValidationError(
                    "The actor must belong to the same company as the service."
                )


class Appointment(models.Model):
    """Model to represent an appointment."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )

    client = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="appointments_as_client",
        verbose_name='Client'
    )
    actor = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="appointments_as_actor",
        verbose_name='Actor/Provider'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name='Service'
    )
    start_time = models.DateTimeField(verbose_name='Start Date/Time')
    end_time = models.DateTimeField(verbose_name='End Date/Time')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Final Price'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.service} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Validates the appointment."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "The start date/time must be before the end date/time."
                )
            
            # Check for conflicts with other appointments
            conflicts = Appointment.objects.filter(
                actor=self.actor,
                status__in=['pending', 'confirmed'],
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(id=self.id)
            
            if conflicts.exists():
                raise ValidationError(
                    "There is already an appointment at this time for this actor."
                )

    def save(self, *args, **kwargs):
        """Saves the appointment with validations."""
        self.clean()
        
        # Calculate final price if not set
        if not self.final_price:
            self.final_price = self.service.base_price
            
        super().save(*args, **kwargs)


class Recurrence(models.Model):
    """Model to represent time recurrences."""
    
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    WEEKDAYS_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    actor = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="recurrences",
        verbose_name='Actor/Provider'
    )
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name='Frequency'
    )
    weekday = models.IntegerField(
        choices=WEEKDAYS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Day of Week'
    )
    day_of_month = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Day of Month'
    )
    start_date = models.DateField(
        verbose_name='Start Date'
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='End Date'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Recurrence'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Recurrence'
        verbose_name_plural = 'Recurrences'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} - {self.get_frequency_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        """Validates the recurrence."""
        if self.frequency == 'weekly' and self.weekday is None:
            raise ValidationError(
                "Day of week is required for weekly recurrence."
            )
        
        if self.frequency == 'monthly' and self.day_of_month is None:
            raise ValidationError(
                "Day of month is required for monthly recurrence."
            )


class Block(models.Model):
    """Model to represent time blocks."""
    
    TYPE_CHOICES = (
        ('vacation', 'Vacation'),
        ('holiday', 'Holiday'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    )

    actor = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="blocks",
        verbose_name='Actor/Provider'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Block Title'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    block_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='other',
        verbose_name='Block Type'
    )
    start_time = models.DateTimeField(verbose_name='Start Date/Time')
    end_time = models.DateTimeField(verbose_name='End Date/Time')
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Block'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Validates the block."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "The start date/time must be before the end date/time."
                )
