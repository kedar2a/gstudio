from django.conf.urls import patterns, url


urlpatterns = patterns('gnowsys_ndf.ndf.views.observations_view',
					url(r'^$', 'all_observations', name='all_observations'),
					url(r'^/(?P<slug>[-\w]+)/(?P<app_set_id>[^/]+)$', 'observations_app', name='observations_app'),
					url(r'^/save_observation/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)', 'save_observation', name='save_observation'),
					url(r'^/delete_observation/(?P<app_set_id>[^/]+)/(?P<slug>[-\w]+)', 'delete_observation', name='delete_observation'),
			  )