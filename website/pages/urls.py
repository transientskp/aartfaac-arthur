from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="pages/index.html"), name='index'),
    url(r'^about/$', TemplateView.as_view(template_name="pages/about.html"), name='about'),
    url(r'^live/$', TemplateView.as_view(template_name="pages/live.html"), name='live'),
    url(r'^team/$', TemplateView.as_view(template_name="pages/team.html"), name='team'),
    url(r'^jobs/$', TemplateView.as_view(template_name="pages/jobs.html"), name='jobs'),
    url(r'^collab/$', TemplateView.as_view(template_name="pages/collab.html"), name='collab'),
    url(r'^related/$', TemplateView.as_view(template_name="pages/related.html"), name='related'),
    url(r'^contact/$', TemplateView.as_view(template_name="pages/contact.html"), name='contact'),
    url(r'^publications/$', TemplateView.as_view(template_name="pages/publications.html"), name='publications'),
]