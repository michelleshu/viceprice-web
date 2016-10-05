from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
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
    url(r'^locations/(\w*)$', vp.views.location_list_view, name='location_list'),
    url(r'^enter_happy_hour/(\d+)$', vp.views.enter_happy_hour_view, name='enter_happy_hour'),
    url(r'^get_location_that_needs_happy_hour/$', vp.views.get_location_that_needs_happy_hour, name='get_location_that_needs_happy_hour'),
    url(r'^add_deal/$', vp.views.add_deal, name='add_deal'),
    url(r'^mark_location_updated/$', vp.views.mark_location_updated, name='mark_location_updated'),
    url(r'^submit_drink_names/$', vp.views.submit_drink_names, name='submit_drink_names'),
    url(r'^upload_data/$', vp.views.upload_data_view, name='upload_data'),
    url(r'^submit_locations_to_upload/$', vp.views.submit_locations_to_upload, name='submit_locations_to_upload'),
    url(r'^skip_location/$', vp.views.flag_location_as_skipped, name='flag_location_as_skipped'),
    url(r'^get_deal_that_needs_confirmation/$', vp.views.get_deal_that_needs_confirmation, name='get_deal_that_needs_confirmation'),
    url(r'^delete_deal/$', vp.views.delete_deal, name='delete_deal'),
    url(r'^delete_deal_detail/$', vp.views.delete_deal_detail, name='delete_deal_detail'),
    url(r'^reject_deal/$', vp.views.reject_deals, name='reject_deal'),

    # Map
    url(r'^get_locations_within_bounds/$', vp.views.get_locations_within_bounds, name='get_locations_within_bounds'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^data_entry/$', vp.views.data_entry, name='data_entry'),
    url(r'^confirm_drink_name/$', vp.views.confirm_drink_name, name='confirm_drink_name'),

    # Other Data
    url(r'^fetch_filtered_deals/$', vp.views.fetch_filtered_deals, name = 'fetch_filtered_deals'),
    url(r'^fetch_location_counts_by_neighborhood/$', vp.views.fetch_location_counts_by_neighborhood, name = 'fetch_location_counts_by_neighborhood'),
    url(r'^sandbox/$', vp.views.sandbox, name = 'sandbox'),
    url(r'^about/$', vp.views.about, name = 'about'),
    url(r'^yelpReviews/$', vp.views.yelp_reviews, name = 'yelpReviews'),
    url(r'^TOS/$', vp.views.TOS, name = 'TOS'),
    url(r'^home/$', vp.views.home, name = 'home'),

    #Blog site
    url(r'^blog/(?P<path>.*)$', BlogProxyView.as_view()),
                       
    #Robot
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt'), name="robots.txt"))

