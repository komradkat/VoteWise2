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

# Force TensorFlow to use CPU only to avoid CUDA configuration issues
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging

try:
    from deepface import DeepFace
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    DeepFace = None
    np = None

from .models import UserBiometric
from apps.core.logging import logger


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
            # ENHANCED MULTI-LAYER ANTI-SPOOFING
            # Single liveness check is not enough - shampoo bottles can fool it
            # We need multiple verification layers
            
            try:
                face_objs = DeepFace.extract_faces(
                    img_path=temp_file.name,
                    enforce_detection=True,
                    anti_spoofing=True
                )
                
                if not face_objs:
                    return JsonResponse({'error': 'No face detected. Please try again.'}, status=400)
                
                # CRITICAL: Default to False for security - assume fake unless proven real
                primary_face = face_objs[0]
                is_real = primary_face.get('is_real', False)
                antispoof_score = primary_face.get('antispoof_score', 0)
                
                logger.face_enroll(f"Liveness Check: Real={is_real}, Score={antispoof_score}", user=request.user.username)
                
                # Layer 1: Basic liveness check
                if not is_real:
                    return JsonResponse({'error': 'Liveness check failed. Fake face detected. Please use a live camera.'}, status=400)
                
                # Layer 2: VERY STRICT confidence threshold (0.95 = 95%+ confidence)
                if antispoof_score < 0.95:
                    logger.security(f"REJECTED: Insufficient confidence {antispoof_score} (need >= 0.95)", user=request.user.username, category="FACE ENROLL")
                    return JsonResponse({'error': f'Liveness confidence too low ({antispoof_score:.2f}). Please ensure optimal lighting and look directly at camera.'}, status=400)
                
                # Layer 3: Face quality check - reject low quality images
                face_confidence = primary_face.get('confidence', 0)
                if face_confidence < 0.90:  # Relaxed from 0.95 to 0.90 for usability
                    logger.security(f"REJECTED: Low face detection confidence {face_confidence}", user=request.user.username, category="FACE ENROLL")
                    return JsonResponse({'error': 'Face quality too low. Please ensure good lighting and clear view.'}, status=400)
                
                # Layer 4: Check facial region size and proportions
                facial_area = primary_face.get('facial_area', {})
                if facial_area:
                    width = facial_area.get('w', 0)
                    height = facial_area.get('h', 0)
                    if width < 80 or height < 80:
                        logger.security(f"REJECTED: Face too small {width}x{height} (min 80x80)", user=request.user.username, category="FACE ENROLL")
                        return JsonResponse({'error': 'Face appears too small. Move closer to camera.'}, status=400)
                    aspect_ratio = width / height if height > 0 else 0
                    # Relaxed from 0.7-1.4 to 0.6-1.5 for different face shapes and angles
                    if aspect_ratio < 0.6 or aspect_ratio > 1.5:
                        logger.security(f"REJECTED: Unusual aspect ratio {aspect_ratio}", user=request.user.username, category="FACE ENROLL")
                        return JsonResponse({'error': 'Face proportions unusual. Please face camera directly.'}, status=400)
                
                # Layer 5: Ensure the liveness model actually ran
                if 'is_real' not in primary_face:
                    logger.error("Liveness detection did not run properly!", user=request.user.username, category="FACE ENROLL")
                    return JsonResponse({'error': 'Security check failed. Anti-spoofing not available.'}, status=500)
                
                logger.face_enroll("All security layers passed - proceeding to enrollment", user=request.user.username)
                    
            except TypeError as e:
                # anti_spoofing parameter not supported - FAIL SECURE
                logger.error(f"Anti-spoofing not supported: {str(e)}", user=request.user.username, category="FACE ENROLL")
                return JsonResponse({'error': 'Security feature not available. Cannot enroll without anti-spoofing.'}, status=500)
            except ValueError as e:
                # No face detected by extract_faces
                logger.warning(f"No face detected: {str(e)}", user=request.user.username, category="FACE ENROLL")
                return JsonResponse({'error': 'No face detected. Please try again.'}, status=400)

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
            logger.warning("No username provided", category="FACE VERIFY")
            return JsonResponse({'error': 'Please enter your username first'}, status=400)
            
        logger.face_verify(f"Attempting to verify user: {username}", user=username)
        
        # 1. Find the user first (1:1 Verification)
        try:
            user = User.objects.get(username=username)
            logger.face_verify(f"User found: {user.username} (ID: {user.id})", user=username)
        except User.DoesNotExist:
            logger.warning(f"User '{username}' does not exist", category="FACE VERIFY")
            return JsonResponse({'error': 'Authentication failed'}, status=401)
            
        try:
            user_biometric = UserBiometric.objects.get(user=user, is_active=True)
            logger.face_verify(f"Face ID found for user {username}", user=username)
        except UserBiometric.DoesNotExist:
            logger.warning(f"Face ID not enrolled for user '{username}'", user=username, category="FACE VERIFY")
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
            # ENHANCED MULTI-LAYER ANTI-SPOOFING
            # Single liveness check is not enough - shampoo bottles can fool it
            # We need multiple verification layers
            
            try:
                face_objs = DeepFace.extract_faces(
                    img_path=temp_file.name,
                    enforce_detection=True,
                    anti_spoofing=True
                )
                
                if not face_objs:
                     logger.warning("No face detected during liveness check.", user=username, category="FACE VERIFY")
                     return JsonResponse({'error': 'No face detected. Please ensure your face is clearly visible.'}, status=400)

                # CRITICAL: Default to False for security - assume fake unless proven real
                primary_face = face_objs[0]
                is_real = primary_face.get('is_real', False)
                antispoof_score = primary_face.get('antispoof_score', 0)
                
                logger.face_verify(f"Liveness Check: Real={is_real}, Score={antispoof_score}", user=username)

                # Layer 1: Basic liveness check
                if not is_real:
                     logger.security(f"REJECTED: Fake face detected (Score: {antispoof_score})", user=username, category="FACE VERIFY")
                     return JsonResponse({'error': 'Liveness check failed. Please use a real camera feed.'}, status=401)
                
                # Layer 2: VERY STRICT confidence threshold (0.95 = 95%+ confidence)
                # Lowered from 0.8 because 0.9 was still allowing shampoo bottles through
                if antispoof_score < 0.95:
                    logger.security(f"REJECTED: Insufficient confidence {antispoof_score} (need >= 0.95)", user=username, category="FACE VERIFY")
                    return JsonResponse({'error': 'Liveness confidence insufficient. Please ensure optimal lighting and look directly at camera.'}, status=401)
                
                # Layer 3: Face quality check - reject low quality images (often from photos/prints)
                face_confidence = primary_face.get('confidence', 0)
                if face_confidence < 0.90:  # Relaxed from 0.95 to 0.90 for usability
                    logger.security(f"REJECTED: Low face detection confidence {face_confidence}", user=username, category="FACE VERIFY")
                    return JsonResponse({'error': 'Face quality too low. Please ensure good lighting and clear view.'}, status=401)
                
                # Layer 4: Check facial region size - photos often have different proportions
                facial_area = primary_face.get('facial_area', {})
                if facial_area:
                    width = facial_area.get('w', 0)
                    height = facial_area.get('h', 0)
                    # Reject if face is too small (likely a photo of a photo)
                    if width < 80 or height < 80:
                        logger.security(f"REJECTED: Face too small {width}x{height} (min 80x80)", user=username, category="FACE VERIFY")
                        return JsonResponse({'error': 'Face appears too small. Move closer to camera.'}, status=401)
                    # Relaxed from 0.7-1.4 to 0.6-1.5 for different face shapes and angles
                    aspect_ratio = width / height if height > 0 else 0
                    if aspect_ratio < 0.6 or aspect_ratio > 1.5:
                        logger.security(f"REJECTED: Unusual aspect ratio {aspect_ratio}", user=username, category="FACE VERIFY")
                        return JsonResponse({'error': 'Face proportions unusual. Please face camera directly.'}, status=401)
                
                # Layer 5: Ensure the liveness model actually ran
                if 'is_real' not in primary_face:
                    logger.error("Liveness detection did not run properly!", user=username, category="FACE VERIFY")
                    return JsonResponse({'error': 'Security check failed. Anti-spoofing not available.'}, status=500)
                
                logger.face_verify("All security layers passed - proceeding to face matching", user=username)

            except TypeError as e:
                # anti_spoofing parameter not supported - FAIL SECURE
                logger.error(f"Anti-spoofing not supported: {str(e)}", user=username, category="FACE VERIFY")
                return JsonResponse({'error': 'Security feature not available. Cannot verify without anti-spoofing.'}, status=500)
            except ValueError as e:
                # DeepFace.extract_faces raises ValueError if no face is found when enforce_detection=True
                logger.warning(f"Liveness check error: {str(e)}", user=username, category="FACE VERIFY")
                return JsonResponse({'error': 'No face detected. Please ensure your face is clearly visible.'}, status=400)
            except Exception as e:
                # Fail secure on any unexpected error
                logger.error(f"Unexpected liveness check error: {str(e)}", user=username, category="FACE VERIFY")
                return JsonResponse({'error': 'Security check failed. Please try again.'}, status=500)

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
        
        logger.face_verify(f"Verifying user {username}: Cosine distance={distance}", user=username)
        
        # Threshold for Facenet Cosine Distance (Default is 0.40)
        # 0.6 was too loose and allowed spoofing. 0.4 is stricter.
        if distance < 0.4:
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
