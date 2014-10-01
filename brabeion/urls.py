from django.conf.urls import url, patterns


urlpatterns = patterns(
    "",
    url(r"^(\w+)/(\d+)/$", "brabeion.views.badge_detail", name="badge_detail"),
)
