from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


class BadgeAward(models.Model):
    user = models.ForeignKey(User, related_name="badges_earned")
    awarded_at = models.DateTimeField(default=timezone.now)
    slug = models.CharField(max_length=255)
    level = models.IntegerField()

    def __getattr__(self, attr):
        return getattr(self._badge, attr)

    @property
    def badge(self):
        return self

    @property
    def _badge(self):
        from brabeion import badges
        return badges._registry[self.slug]

    @property
    def name(self):
        return self._badge.levels[self.level].name

    @property
    def description(self):
        return self._badge.levels[self.level].description

    @property
    def progress(self):
        return self._badge.progress(self.user, self.level)

    @property
    def logo_normal(self):
        return self._badge.levels[self.level].logo_own_middle

    def get_absolute_url(self):
        return reverse('brabeion:badge_detail', args=(self.slug, self.level+1))
