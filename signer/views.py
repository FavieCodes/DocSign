import json
import base64
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from .models import Document


def landing_page(request):
    """Render the landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'signer/landing.html')


@login_required(login_url='login')
def api_docs(request):
    """Render the custom interactive API documentation."""
    return render(request, 'signer/docs.html')


@login_required(login_url='login')
def index(request):
    """Render the main app template (requires login)."""
    return render(request, 'signer/index.html')


@require_http_methods(["GET"])
def list_documents(request):
    """Return all documents belonging to the authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    docs = Document.objects.filter(user=request.user)
    return JsonResponse({'documents': [d.to_dict() for d in docs]})


@require_http_methods(["POST"])
def upload_document(request):
    """Upload an original file, creating a Document record for the logged-in user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
    if file.content_type not in allowed_types:
        return JsonResponse({'error': 'Unsupported file type. Use PDF, PNG, or JPG.'}, status=400)

    doc = Document.objects.create(
        name=file.name,
        original_file=file,
        user=request.user
    )
    return JsonResponse({'document': doc.to_dict()}, status=201)


@require_http_methods(["POST"])
def save_signed(request, doc_id):
    """Save the signed version of a document (restricted to document owner)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    doc = get_object_or_404(Document, id=doc_id, user=request.user)

    try:
        body = json.loads(request.body)
        image_data = body.get('image', '')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    if not image_data.startswith('data:image/png;base64,'):
        return JsonResponse({'error': 'Invalid image data'}, status=400)

    # Decode base64 → bytes
    header, b64 = image_data.split(',', 1)
    image_bytes = base64.b64decode(b64)

    filename = f"{doc.id}_signed.png"

    # Replace old signed file if it exists
    if doc.signed_file:
        doc.signed_file.delete(save=False)

    doc.signed_file.save(filename, ContentFile(image_bytes), save=True)
    return JsonResponse({'document': doc.to_dict()})


@require_http_methods(["DELETE"])
def delete_document(request, doc_id):
    """Delete a document and its files (restricted to document owner)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    doc = get_object_or_404(Document, id=doc_id, user=request.user)

    # Remove files from storage
    for field in [doc.original_file, doc.signed_file]:
        if field:
            try:
                field.delete(save=False)
            except Exception:
                pass

    doc.delete()
    return JsonResponse({'success': True})
