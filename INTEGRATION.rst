brabeion integration to CheckiO

base.py changes:
- Badge object:
    - slug is None by default
    - multiple is False by default
    
- BadgeDetail object:
    - added difficulty
    - added logo_own_little
    - added logo_own_middle
    - added logo_own_big
    - added logo_competitor_little
    - added logo_competitor_middle
    - added logo_competitor_big
    - added logo_both_little
    - added logo_both_middle
    - added logo_both_big
    - added logo_disabled_little
    - added logo_disabled_middle
    - added logo_disabled_big

- actually_possibly_award method changes:
    - user for awarding chosen from badge award method, not from signal
    - use of get_or_create when creating badge (IntegrityError fix)
    - badge awarding goes all lower levels of same badge as well

models.py changes:
- BadgeAward model:
    - added property logo_normal
    - added method get_absolute_url

urls.py changes:
- removed badge_list

views.py changes:
- badge_detail view:
    - raise 404 if badge doesn't exist
