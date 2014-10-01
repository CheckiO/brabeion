from collections import defaultdict

from brabeion.base import Badge


class BadgeCache(object):
    """
    This is responsible for storing all badges that have been registered, as
    well as providing the pulic API for awarding badges.

    This class should not be instantiated multiple times, if you do it's your
    fault when things break, and you get to pick up all the pieces.
    """
    def __init__(self):
        self._event_registry = {}
        self._group_registry = defaultdict(list)
        self._registry = {}

    def register(self, badge):
        # We should probably duck-type this, but for now it's a decent sanity
        # check.
        assert issubclass(badge, Badge)
        badge = badge()
        self._registry[badge.slug] = badge
        for event in badge.events:
            self._event_registry.setdefault(event, []).append(badge)
            if not badge.groups:
                continue
            for group in badge.groups:
                self._group_registry[group].append(event)

    def possibly_award_badge(self, event, **state):
        if event in self._event_registry:
            for badge in self._event_registry[event]:
                badge.possibly_award(**state)

    def award_badges(self, group, state):
        [self.possibly_award_badge(event, **state) for event in badges._group_registry[group]]

badges = BadgeCache()
