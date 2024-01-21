from django.db import models

class Curator(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)


class Concept(models.Model):
    title = models.CharField(max_length=150)
    curator = models.ForeignKey('Curator', models.SET_NULL, null=True)
    description = models.CharField(max_length=500)

    slug = models.SlugField(max_length=75, null=True)
    poster = models.URLField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)


class Application(models.Model):
    artist = models.ForeignKey('artist.Artist', models.SET_NULL, null=True)
    concept = models.ForeignKey('Concept', models.SET_NULL, null=True)

    PENDING = 0
    AVAILABLE = 1
    UNAVAILABLE = 2
    STATUS = (
        (PENDING, "Pending"),
        (AVAILABLE, "Available"),
        (UNAVAILABLE, "Unavailable")
    )
    status = models.PositiveSmallIntegerField(choices=STATUS)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    @property
    def application_date(self):
        return self.created_at


class Shuffle(models.Model):
    concept = models.ForeignKey('Concept', models.SET_NULL, null=True)

    last_shuffle = models.DateTimeField()
    next_shuffle = models.DateTimeField()

    STATUS = (
        (0, "Started"),
        (1, "In Progress"),
        (2, "Complete")
    )
    status = models.PositiveSmallIntegerField(choices=STATUS)

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)