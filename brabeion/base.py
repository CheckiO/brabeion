from django.conf import settings

from brabeion.models import BadgeAward
from brabeion.signals import badge_awarded


class BadgeAwarded(object):
    def __init__(self, level=None, user=None):
        self.level = level
        self.user = user


def url_to_badge(category, size, filename):
    # TODO: remove imgv3 from this app
    static_url = settings.STATIC_URL.rstrip('/')
    return '/'.join([static_url, 'imgv3', 'badges', category, str(size), filename])


class BadgeDetail(object):
    def __init__(self, name=None, description=None, badge_filename=None, difficulty=None):
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.logo_own_little = url_to_badge('user', 32, badge_filename)
        self.logo_own_middle = url_to_badge('user', 48, badge_filename)
        self.logo_own_big = url_to_badge('user', 64, badge_filename)
        self.logo_competitor_little = url_to_badge('competitor', 32, badge_filename)
        self.logo_competitor_middle = url_to_badge('competitor', 48, badge_filename)
        self.logo_competitor_big = url_to_badge('competitor', 64, badge_filename)
        self.logo_both_little = url_to_badge('both', 32, badge_filename)
        self.logo_both_middle = url_to_badge('both', 48, badge_filename)
        self.logo_both_big = url_to_badge('both', 64, badge_filename)
        self.logo_disabled_little = url_to_badge('disabled', 32, badge_filename)
        self.logo_disabled_middle = url_to_badge('disabled', 48, badge_filename)
        self.logo_disabled_big = url_to_badge('disabled', 64, badge_filename)


class Badge(object):
    async = False
    multiple = False
    slug = None
    groups = None

    def __init__(self):
        assert not (self.multiple and len(self.levels) > 1)
        for i, level in enumerate(self.levels):
            if not isinstance(level, BadgeDetail):
                self.levels[i] = BadgeDetail(level)

    def possibly_award(self, **state):
        """
        Will see if the user should be awarded a badge.  If this badge is
        asynchronous it just queues up the badge awarding.
        """
        assert "user" in state
        if self.async:
            from brabeion.tasks import AsyncBadgeAward
            state = self.freeze(**state)
            AsyncBadgeAward.delay(self, state)
            return
        self.actually_possibly_award(**state)

    def actually_possibly_award(self, **state):
        """
        Does the actual work of possibly awarding a badge.
        """
        awarded = self.award(**state)
        if awarded is None:
            return
        user = awarded.user
        if awarded.level is None:
            assert len(self.levels) == 1
            awarded.level = 1
        # awarded levels are 1 indexed, for conveineince
        awarded = awarded.level - 1
        assert awarded < len(self.levels)
        extra_kwargs = {}
        force_timestamp = state.pop("force_timestamp", None)
        if force_timestamp is not None:
            extra_kwargs["awarded_at"] = force_timestamp

        for level in range(awarded, -1, -1):
            created = True
            if self.multiple:
                badge = BadgeAward.objects.create(
                    user=user, slug=self.slug, level=level, **extra_kwargs)
            else:
                badge, created = BadgeAward.objects.get_or_create(
                    user=user, slug=self.slug, level=level, **extra_kwargs)
            if created:
                badge_awarded.send(sender=self, badge_award=badge)

    def freeze(self, **state):
        return state


def send_badge_messages(badge_award, **kwargs):
    """
    If the Badge class defines a message, send it to the user who was just
    awarded the badge.
    """
    user_message = getattr(badge_award.badge, "user_message", None)
    if callable(user_message):
        message = user_message(badge_award)
    else:
        message = user_message
    if message is not None:
        badge_award.user.message_set.create(message=message)
badge_awarded.connect(send_badge_messages)
