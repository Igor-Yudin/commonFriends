from django.conf.urls import url
from friends import views


urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^check_user_id_ajax/$', views.check_user_id_ajax, name='check_user_id_ajax'),
	url(r'^get_list_ajax/$', views.get_list_ajax, name='get_list_ajax'),
]