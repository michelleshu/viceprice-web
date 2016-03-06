from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

import vp.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gettingstarted.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', vp.views.index, name='index'),

    # Authentication
    url(r'^login/$', vp.views.login_view, name='login'),
    url(r'^logout/$', vp.views.logout_user, name='logout'),
    url(r'^register/$', vp.views.register_view, name='register'),
    url(r'^authenticate_user/$', vp.views.authenticate_user, name='authenticate_user'),
    
    # Data
    url(r'^upload_data/$', vp.views.upload_data_view, name='upload_data'),
    url(r'^submit_locations_to_upload/$', vp.views.submit_locations_to_upload, name='submit_locations_to_upload'),

    # Map
    url(r'^get_locations_within_bounds/$', vp.views.get_locations_within_bounds, name='get_locations_within_bounds'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    
    # Other Data
    url(r'^fetch/$', vp.views.fetch_locations, name = 'fetch')
)
