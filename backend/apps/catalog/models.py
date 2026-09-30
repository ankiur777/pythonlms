from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from apps.core.models import UUIDTimeStampedModel


class Category(UUIDTimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:90]
        return super().save(*args, **kwargs)


class CourseQuerySet(models.QuerySet):
    def published(self) -> models.QuerySet:
        return self.filter(status=Course.Status.PUBLISHED)


class Course(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "Review"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Tone(models.TextChoices):
        VIOLET = "violet", "Violet"
        CYAN = "cyan", "Cyan"
        ORANGE = "orange", "Orange"
        GREEN = "green", "Green"

    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=140)
    subtitle = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True, help_text="Short marketing copy for cards.")
    description = models.TextField(blank=True, help_text="Long-form course landing copy.")
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    tone = models.CharField(max_length=10, choices=Tone.choices, default=Tone.VIOLET)
    emoji = models.CharField(max_length=8, blank=True, default="</>")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    language = models.CharField(max_length=10, default="en")
    price_minor = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    categories = models.ManyToManyField(Category, related_name="courses", blank=True)
    instructor_name = models.CharField(max_length=120, blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="authored_courses",
        on_delete=models.SET_NULL,
    )
    what_you_learn = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=list, blank=True)

    objects = CourseQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["status", "level"])]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:120]
        return super().save(*args, **kwargs)

    @property
    def price_decimal(self) -> float:
        return round(self.price_minor / 100, 2)

    @property
    def is_free(self) -> bool:
        return self.price_minor == 0

    @property
    def lesson_count(self) -> int:
        return sum(module.lessons.count() for module in self.modules.all())

    @property
    def duration_minutes(self) -> int:
        return sum(
            lesson.estimated_minutes
            for module in self.modules.all()
            for lesson in module.lessons.all()
        )

    @property
    def enrolled_count(self) -> int:
        return self.enrollments.count()

    @property
    def rating_average(self) -> float:
        reviews = self.reviews.filter(status="published")
        if not reviews.exists():
            return 0.0
        return round(sum(review.rating for review in reviews) / reviews.count(), 2)

    @property
    def rating_count(self) -> int:
        return self.reviews.filter(status="published").count()


class Module(UUIDTimeStampedModel):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    summary = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["course", "position"], name="unique_module_position")
        ]

    def __str__(self) -> str:
        return f"{self.course.title} · {self.title}"


class Lesson(UUIDTimeStampedModel):
    class Type(models.TextChoices):
        TEXT = "text", "Text"
        VIDEO = "video", "Video"
        CODE = "code", "Code"
        QUIZ = "quiz", "Quiz"

    module = models.ForeignKey(Module, related_name="lessons", on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.TEXT)
    title = models.CharField(max_length=160)
    position = models.PositiveIntegerField(default=1)
    estimated_minutes = models.PositiveIntegerField(default=10)
    is_preview = models.BooleanField(default=False)
    body = models.TextField(blank=True, help_text="Markdown-ish lesson copy.")
    starter_code = models.TextField(blank=True)
    solution_code = models.TextField(blank=True)
    video_url = models.URLField(blank=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["module", "position"], name="unique_lesson_position")
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def course(self) -> Course:
        return self.module.course
