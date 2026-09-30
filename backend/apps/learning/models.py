import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.catalog.models import Course, Lesson
from apps.core.models import UUIDTimeStampedModel


def new_verification_code() -> str:
    return f"LMS-{secrets.token_hex(8).upper()}"


class Enrollment(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    source = models.CharField(max_length=12, default="web")
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_enrollment_per_learner"
            )
        ]
        indexes = [models.Index(fields=["user", "status"])]

    def __str__(self) -> str:
        return f"{self.user} → {self.course.title}"

    @property
    def total_lessons(self) -> int:
        return Lesson.objects.filter(module__course=self.course).count()

    @property
    def completed_lessons(self) -> int:
        return self.progress.filter(status=LessonProgress.Status.COMPLETED).count()

    @property
    def progress_percent(self) -> int:
        total = self.total_lessons
        if not total:
            return 0
        return round(self.completed_lessons / total * 100)

    def recalculate_completion(self) -> int:
        """Server-side completion boundary; issues a certificate at 100%."""
        percent = self.progress_percent
        if percent >= 100 and self.status != Enrollment.Status.COMPLETED:
            self.status = Enrollment.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=["status", "completed_at", "updated_at"])
            Certificate.objects.get_or_create(
                enrollment=self, defaults={"verification_code": new_verification_code()}
            )
        return percent


class LessonProgress(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    enrollment = models.ForeignKey(
        Enrollment, related_name="progress", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(Lesson, related_name="progress_records", on_delete=models.CASCADE)
    status = models.CharField(max_length=14, choices=Status.choices, default=Status.IN_PROGRESS)
    progress_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    last_position_seconds = models.PositiveIntegerField(default=0)
    last_code = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"], name="unique_progress_per_lesson"
            )
        ]
        indexes = [models.Index(fields=["enrollment", "status"])]
