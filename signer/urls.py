from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.index, name='index'),
    path('docs/', views.api_docs, name='api_docs'),

    # Document API
    path('api/documents/', views.list_documents, name='list_documents'),
    path('api/documents/upload/', views.upload_document, name='upload_document'),
    path('api/documents/<uuid:doc_id>/save/', views.save_signed, name='save_signed'),
    path('api/documents/<uuid:doc_id>/delete/', views.delete_document, name='delete_document'),
]
