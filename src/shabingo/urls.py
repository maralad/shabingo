#!/usr/bin/env python
__author__ = 'Donagh Corcoran'

from django.conf.urls import patterns, include, url
#from django.contrib.comments.models import FreeComment
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import ListView, DetailView
from main.models import Post
#from main import views
from django.contrib import admin
admin.autodiscover()
##Admin Page
########################Home Page
urlpatterns = patterns('',url(r'^admin/', include(admin.site.urls)), 
  #password reset shit.. 
    url(r'^reset/password_reset/$', 'django.contrib.auth.views.password_reset', name='reset_password_reset1'),
    url(r'^reset/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
        ##SocialAuth
     url('', include('social.apps.django_app.urls', namespace='social')),
     url('', include('django.contrib.auth.urls', namespace='auth')),
     
     url(r'^comments/', include('django.contrib.comments.urls')),
     url(r'^blog', ListView.as_view(
			    queryset=Post.objects.all().order_by("-created")[:1],
			    template_name="blog.html")),
     url(r'^(?P<pk>\d+)$', DetailView.as_view(
			    model = Post,
			    template_name="post.html")),
      url(r'^archives', ListView.as_view(
			    queryset=Post.objects.all().order_by("-created"),
			    template_name="archives.html")),
      ##Favicon
      
    # Pages
    url(r'^$', 'main.views.home', name='home'),
    url(r'^reg/$', 'main.views.reg', name='reg'),
   
 url(r'^signup2/$', 'main.views.signup2', name='signup2'),   
 url(r'^thank-you/$', 'main.views.thankyou', name='thankyou'),
 url(r'^about-us/$', 'main.views.aboutus', name='aboutus'),
 url(r'^myprofile/$', 'main.views.myprofile', name='myprofile'),
 url(r'^loggedin2/$', 'main.views.loggedin2', name='loggedin2'),
  url(r'^sitemap/$', 'main.views.sitemap', name='sitemap'),
 ##url(r'^sitemap/$', 'main.views.sitemap', name='sitemap'),
 url(r'^contact-us/$', 'main.views.contactus', name='contactus'),
 url(r'^the-best-place-to-sell-your-video-content-online/$', 'main.views.sellvidsblog', name='sellvidsblog'),
 url(r'^purevideos/$', 'main.views.purevideos', name='purevideos'),
 url(r'^privacypolicy/$', 'main.views.privacypolicy', name='privacypolicy'),
 url(r'^charts/$', 'main.views.charts', name='charts'),
 url(r'^list/$', 'main.views.list', name='list'),
 url(r'^item_list/$', 'main.views.item_list', name='item_list'),
 #url(r'^show_me_the_money/$', 'main.views.show_me_the_money'),
 #url(r'^show-me-the-money-again/$', 'main.views.show_me_the_money'),
 url(r'^show_me_the_money/', include('paypal.standard.ipn.urls')),
 url(r'^videos/$', 'main.views.videos', name='videos'),
 url(r'^video2/(?P<document_id>\d+)/$', 'main.views.video2', name='video2'),
 url(r'^shabingoadult$', 'main.views.shabingoadult', name='shabingoadult'),

 #url(r'^vid/$', 'main.views.vid', name='vid'),
 url(r'^approve/$', 'main.views.approve', name='approve'),
 #url(r'^(?P<pk>[\d]+)/myvideo/$', views.myvideo.as_view(), name='myvideo'),
 url(r'^video/(?P<document_id>\d+)/$', 'main.views.video', name='video'),
 url(r'^myvideo/(?P<document_id>\d+)/$', 'main.views.myvideo', name='myvideo'),
 url(r'^myvideos/$', 'main.views.myvideos', name='myvideos'),
 url(r'^edit_preview/(?P<document_id>\d+)/$', 'main.views.edit_preview', name='edit_preview'),
 url(r'^delete_record/(?P<document_id>\d+)/$', 'main.views.delete_record', name='delete_record'),
 url(r'^loginsocial/$', 'main.views.loginsocial', name='loginsocial'),
 url(r'^stripe_pay/$', 'main.views.stripe_pay', name='stripe_pay'),
 url(r'^terms/$', 'main.views.terms', name='terms'),

 url(r'^upload/$', 'main.views.upload', name='upload'),
 url(r'^upload2/$', 'main.views.upload2', name='upload2'),
 url(r'^stripe_auth/$', 'main.views.stripe_auth', name='stripe_auth'),
 url(r'^stripe_callback/$', 'main.views.stripe_callback', name='stripe_callback'),
 url(r'^contact/$', 'main.views.contact', name='contact'),
 url(r'^accounts/login/(?P<document_id>\d+)/$', 'main.views.login', name='login'),
 url(r'^accounts/auth/$', 'main.views.auth_view'),
 url(r'^accounts/logout/$', 'main.views.logout', name='logout'),
 url(r'^accounts/loggedin2/$', 'main.views.loggedin2', name='loggedin2'),
 url(r'^accounts/invalid/$', 'main.views.invalid_login', name='invalid'),
  

    
 # THIS IS THE POLL VIEWS
 ##url(r'^polls/$',views.index, name='index'), 
 ##url(r'^polls/(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
 ##url(r'^polls/(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
 ##url(r'^polls/(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
 
 ##url(r'^admin/', include(admin.site.urls)),
 
)

if  settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)









