from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.appointments.models import Appointment
from apps.authentication.models import User

User = get_user_model()


class GoogleCalendarIntegration(models.Model):
    """
    Model to store Google Calendar integration settings
    for each user/actor.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='google_calendar_integration',
        verbose_name='User'
    )
    
    # OAuth credentials
    access_token = models.TextField(
        verbose_name='Access Token',
        help_text='Google OAuth access token'
    )
    refresh_token = models.TextField(
        verbose_name='Refresh Token',
        help_text='Google OAuth refresh token'
    )
    token_expires_at = models.DateTimeField(
        verbose_name='Token Expires At',
        help_text='Token expiration date and time'
    )
    
    # Synchronization settings
    calendar_id = models.CharField(
        max_length=255,
        verbose_name='Calendar ID',
        help_text='Google Calendar calendar ID',
        default='primary'
    )
    sync_enabled = models.BooleanField(
        default=True,
        verbose_name='Sync Enabled',
        help_text='Whether Google Calendar synchronization is active'
    )
    sync_direction = models.CharField(
        max_length=20,
        choices=[
            ('bidirectional', 'Bidirectional'),
            ('to_google', 'To Google'),
            ('from_google', 'From Google'),
        ],
        default='bidirectional',
        verbose_name='Sync Direction',
        help_text='Event synchronization direction'
    )
    
    # Notification settings
    notify_on_create = models.BooleanField(
        default=True,
        verbose_name='Notify on Create',
        help_text='Send notification when creating event in Google Calendar'
    )
    notify_on_update = models.BooleanField(
        default=True,
        verbose_name='Notify on Update',
        help_text='Send notification when updating event in Google Calendar'
    )
    notify_on_delete = models.BooleanField(
        default=True,
        verbose_name='Notify on Delete',
        help_text='Send notification when deleting event in Google Calendar'
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Sync At',
        help_text='Date and time of last synchronization'
    )
    
    class Meta:
        verbose_name = 'Google Calendar Integration'
        verbose_name_plural = 'Google Calendar Integrations'
        db_table = 'google_calendar_integration'
    
    def __str__(self):
        return f"Google Calendar - {self.user.username}"
    
    @property
    def is_token_expired(self):
        """Checks if the access token has expired."""
        if not self.token_expires_at:
            return True
        return timezone.now() >= self.token_expires_at
    
    def needs_refresh(self):
        """Checks if the token needs to be renewed."""
        if not self.token_expires_at:
            return True
        # Renew if expires in less than 5 minutes
        return timezone.now() >= (self.token_expires_at - timezone.timedelta(minutes=5))


class GoogleCalendarEvent(models.Model):
    """
    Model to store the mapping between appointments and Google Calendar events.
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='google_calendar_event',
        verbose_name='Appointment'
    )
    
    # Google Calendar IDs
    google_event_id = models.CharField(
        max_length=255,
        verbose_name='Google Event ID',
        help_text='Event ID in Google Calendar'
    )
    google_calendar_id = models.CharField(
        max_length=255,
        verbose_name='Google Calendar ID',
        help_text='Calendar ID where the event was created'
    )
    
    # Synchronization status
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('synced', 'Synced'),
            ('pending', 'Pending'),
            ('error', 'Error'),
            ('conflict', 'Conflict'),
        ],
        default='synced',
        verbose_name='Sync Status'
    )
    sync_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Sync Error',
        help_text='Error message in case of synchronization failure'
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )
    last_sync_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Sync At'
    )
    
    class Meta:
        verbose_name = 'Google Calendar Event'
        verbose_name_plural = 'Google Calendar Events'
        db_table = 'google_calendar_event'
        unique_together = ['google_event_id', 'google_calendar_id']
    
    def __str__(self):
        return f"Google Event {self.google_event_id} - {self.appointment}"


class GoogleCalendarSyncLog(models.Model):
    """
    Model to store Google Calendar synchronization logs.
    """
    integration = models.ForeignKey(
        GoogleCalendarIntegration,
        on_delete=models.CASCADE,
        related_name='sync_logs',
        verbose_name='Integration'
    )
    
    # Synchronization details
    sync_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Synchronization'),
            ('incremental', 'Incremental Synchronization'),
            ('manual', 'Manual Synchronization'),
            ('automatic', 'Automatic Synchronization'),
        ],
        verbose_name='Sync Type'
    )
    
    # Results
    events_created = models.PositiveIntegerField(
        default=0,
        verbose_name='Events Created'
    )
    events_updated = models.PositiveIntegerField(
        default=0,
        verbose_name='Events Updated'
    )
    events_deleted = models.PositiveIntegerField(
        default=0,
        verbose_name='Events Deleted'
    )
    events_conflicted = models.PositiveIntegerField(
        default=0,
        verbose_name='Events in Conflict'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('error', 'Error'),
            ('partial', 'Partial'),
        ],
        verbose_name='Status'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Error Message'
    )
    
    # Metadata
    started_at = models.DateTimeField(
        verbose_name='Started at'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Completed at'
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duration (seconds)'
    )
    
    class Meta:
        verbose_name = 'Google Calendar Sync Log'
        verbose_name_plural = 'Google Calendar Sync Logs'
        db_table = 'google_calendar_sync_log'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Sync Log {self.id} - {self.integration.user.username}"
    
    def save(self, *args, **kwargs):
        if self.completed_at and self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)

