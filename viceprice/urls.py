from django.conf.urls import patterns, include, url
from django.contrib import admin
from vp.views import BlogProxyView
admin.autodiscover()

import vp.views

urlpatterns = patterns('',
    url(r'^$', vp.views.index, name='index'),

    # Authentication
    url(r'^login/$', vp.views.login_view, name='login'),
    url(r'^logout/$', vp.views.logout_user, name='logout'),
    url(r'^register/$', vp.views.register_view, name='register'),
    url(r'^authenticate_user/$', vp.views.authenticate_user, name='authenticate_user'),

    # Data
    url(r'^enter_happy_hour/$', vp.views.enter_happy_hour_view, name='enter_happy_hour'),
    url(r'^get_location_that_needs_happy_hour/$', vp.views.get_location_that_needs_happy_hour, name='get_location_that_needs_happy_hour'),
    url(r'^submit_happy_hour_data/$', vp.views.submit_happy_hour_data, name='submit_happy_hour_data'),
    url(r'^upload_data/$', vp.views.upload_data_view, name='upload_data'),
    url(r'^submit_locations_to_upload/$', vp.views.submit_locations_to_upload, name='submit_locations_to_upload'),
    url(r'^skip_location/$', vp.views.flag_location_as_skipped, name='flag_location_as_skipped'),
    url(r'^get_deal_that_needs_confirmation/$', vp.views.get_deal_that_needs_confirmation, name='get_deal_that_needs_confirmation'),

    # Map
    url(r'^get_locations_within_bounds/$', vp.views.get_locations_within_bounds, name='get_locations_within_bounds'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data_entry/$', vp.views.data_entry, name='data_entry'),
    url(r'^confirm_drink_name/$', vp.views.confirm_drink_name, name='confirm_drink_name'),

    # Other Data
    url(r'^fetch/$', vp.views.fetch_locations, name = 'fetch'),
    url(r'^sandbox/$', vp.views.sandbox, name = 'sandbox'),
    url(r'^home/$', vp.views.home, name = 'home'),
    url(r'^yelpReviews/$', vp.views.yelp_reviews, name = 'yelpReviews'),

    #Blog site
    url(r'^blog/(?P<path>.*)$', BlogProxyView.as_view())
)
