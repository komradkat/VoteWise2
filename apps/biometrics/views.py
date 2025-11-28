from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
import json
import base64
import io
import os
import tempfile
from PIL import Image

try:
    from deepface import DeepFace
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    DeepFace = None
    np = None

from .models import UserBiometric

@csrf_exempt
@login_required
def enroll_face(request):
    """
    Enroll a user's face for biometric authentication using DeepFace.
    Expects a POST request with a base64 encoded image.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not FACE_RECOGNITION_AVAILABLE:
        return JsonResponse({'error': 'Face recognition library not installed'}, status=500)

    temp_file = None
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)
            
        # Decode base64 image
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
            
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save to temporary file for DeepFace
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        # Extract face embedding using DeepFace
        try:
            embedding_objs = DeepFace.represent(
                img_path=temp_file.name,
                model_name='Facenet',  # Fast and accurate
                enforce_detection=True
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                return JsonResponse({'error': 'No face detected. Please try again.'}, status=400)
            
            if len(embedding_objs) > 1:
                return JsonResponse({'error': 'Multiple faces detected. Please ensure only you are in the frame.'}, status=400)
            
            # Get the embedding vector
            embedding = embedding_objs[0]['embedding']
            embedding_array = np.array(embedding, dtype=np.float32)
            embedding_bytes = embedding_array.tobytes()
            
            # Save to database
            UserBiometric.objects.update_or_create(
                user=request.user,
                defaults={
                    'face_encoding': embedding_bytes,
                    'is_active': True
                }
            )
            
            return JsonResponse({'success': True, 'message': 'Face enrolled successfully'})
            
        except ValueError as e:
            # DeepFace raises ValueError when no face is detected
            return JsonResponse({'error': 'No face detected. Please try again.'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

def face_login_view(request):
    """Render the dedicated Face ID login page."""
    return render(request, 'biometrics/face_login.html')

@csrf_exempt
def verify_face(request):
    """
    Verify a user's face for login using DeepFace (1:1 Verification).
    Expects a POST request with 'username' and base64 encoded 'image'.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if not FACE_RECOGNITION_AVAILABLE:
        return JsonResponse({'error': 'Face recognition library not installed'}, status=500)
    
    temp_file = None
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        username = data.get('username')
        
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)
            
        if not username:
            print(f"[FACE VERIFY] ERROR: No username provided")
            return JsonResponse({'error': 'Please enter your username first'}, status=400)
            
        print(f"[FACE VERIFY] Attempting to verify user: {username}")
        
        # 1. Find the user first (1:1 Verification)
        try:
            user = User.objects.get(username=username)
            print(f"[FACE VERIFY] User found: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"[FACE VERIFY] ERROR: User '{username}' does not exist")
            return JsonResponse({'error': 'Authentication failed'}, status=401)
            
        try:
            user_biometric = UserBiometric.objects.get(user=user, is_active=True)
            print(f"[FACE VERIFY] Face ID found for user {username}")
        except UserBiometric.DoesNotExist:
            print(f"[FACE VERIFY] ERROR: Face ID not enrolled for user '{username}'")
            return JsonResponse({'error': 'Face ID not enabled for this user'}, status=400)

        # Decode base64 image
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
            
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save to temporary file for DeepFace
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        # Extract face embedding
        try:
            embedding_objs = DeepFace.represent(
                img_path=temp_file.name,
                model_name='Facenet',
                enforce_detection=True
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                return JsonResponse({'error': 'No face detected'}, status=400)
            
            unknown_embedding = np.array(embedding_objs[0]['embedding'], dtype=np.float32)
            
        except ValueError:
            return JsonResponse({'error': 'No face detected'}, status=400)
        
        # 2. Compare ONLY with this user's stored embedding
        stored_embedding = np.frombuffer(user_biometric.face_encoding, dtype=np.float32)
        
        # Calculate Cosine Distance
        dot_product = np.dot(unknown_embedding, stored_embedding)
        norm_a = np.linalg.norm(unknown_embedding)
        norm_b = np.linalg.norm(stored_embedding)
        
        if norm_a == 0 or norm_b == 0:
            distance = 1.0
        else:
            distance = 1 - (dot_product / (norm_a * norm_b))
        
        print(f"Verifying user {username}: Cosine distance={distance}")
        
        # Threshold for Facenet Cosine Distance (0.6 is more forgiving for webcams)
        if distance < 0.6:
            # Match found! Login the user
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/auth/profile/'})
        
        return JsonResponse({'error': 'Face not recognized'}, status=401)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
