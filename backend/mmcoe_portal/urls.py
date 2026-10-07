from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/interx/', include('interx.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/', include('comments.urls')),
    path('', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='home-portal'),
    path('register/', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='register-portal'),
    path('create-account/', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='create-account-portal'),
    path('login/', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='login-portal'),

    # Navigator entry and deep routes (SPA fallback)
    path('navigator/', TemplateView.as_view(template_name='navigator/index.html'), name='navigator-portal'),
    re_path(r'^navigator/assets/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIR / 'navigator' / 'assets'}),
    re_path(r'^navigator/(?P<path>(favicon\.ico|robots\.txt))$', serve, {'document_root': settings.FRONTEND_DIR / 'navigator'}),
    re_path(r'^navigator/.*$', TemplateView.as_view(template_name='navigator/index.html')),

    # InterX Career Hub entry and deep routes (SPA fallback)
    path('interx/', TemplateView.as_view(template_name='interx/index.html'), name='interx-portal'),
    re_path(r'^interx/assets/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIR / 'interx' / 'assets'}),
    re_path(r'^interx/(?P<path>(favicon\.ico|robots\.txt|.*\.png|.*\.svg))$', serve, {'document_root': settings.FRONTEND_DIR / 'interx'}),
    re_path(r'^interx/.*$', TemplateView.as_view(template_name='interx/index.html')),

    # Student Community entry and deep routes (SPA fallback)
    path('community/', TemplateView.as_view(template_name='community/index.html'), name='community-portal'),
    re_path(r'^community/assets/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIR / 'community' / 'assets'}),
    re_path(r'^community/(?P<path>(favicon\.ico|robots\.txt|.*\.png|.*\.svg))$', serve, {'document_root': settings.FRONTEND_DIR / 'community'}),
    re_path(r'^community/.*$', TemplateView.as_view(template_name='community/index.html')),

    # Media file serving
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Direct static file serving for root assets and /static/ to eliminate 404s
    re_path(r'^(?P<path>(style\.css|script\.js|js/.*))$', serve, {'document_root': settings.FRONTEND_DIR}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIR}),
]
