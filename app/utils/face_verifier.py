import os
import urllib.request
import cv2
import numpy as np
from pathlib import Path

# Paths relative to the app folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RESOURCE_DIR = BASE_DIR / "app" / "resources"
YUNET_PATH = RESOURCE_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = RESOURCE_DIR / "face_recognition_sface_2021dec.onnx"

YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

_detector = None
_recognizer = None

def download_model(url, dest_path):
    print(f"Downloading pre-trained face model: {url} ...")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Simple downloader with headers to prevent HTTP 403 Forbidden
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
        out_file.write(response.read())
    print(f"Downloaded successfully to {dest_path}")

def init_models():
    global _detector, _recognizer
    if _detector is not None and _recognizer is not None:
        return True
        
    try:
        if not YUNET_PATH.exists():
            download_model(YUNET_URL, YUNET_PATH)
        if not SFACE_PATH.exists():
            download_model(SFACE_URL, SFACE_PATH)
            
        # YuNet detector requires dynamic width/height set later, but initialize it here
        # We set default input size to (320, 320)
        _detector = cv2.FaceDetectorYN.create(str(YUNET_PATH), "", (320, 320))
        _recognizer = cv2.FaceRecognizerSF.create(str(SFACE_PATH), "")
        return True
    except Exception as e:
        print(f"Error initializing Face Recognition models: {e}")
        return False

def resize_image_to_target_width(img, target_width=320):
    h, w = img.shape[:2]
    if w <= target_width:
        return img
    target_height = int(h * (target_width / w))
    return cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)

def detect_face_with_rotation_fallback(img):
    """
    Attempts to detect a face in img. If not detected, tries rotating the image
    90, 180, and 270 degrees clockwise to find a face.
    Returns (oriented_image, faces) or (img, None)
    """
    # 1. Original orientation (0 deg)
    h, w = img.shape[:2]
    _detector.setInputSize((w, h))
    _, faces = _detector.detect(img)
    if faces is not None and len(faces) > 0:
        return img, faces
        
    # 2. Try 90 degrees clockwise
    img_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h_90, w_90 = img_90.shape[:2]
    _detector.setInputSize((w_90, h_90))
    _, faces_90 = _detector.detect(img_90)
    if faces_90 is not None and len(faces_90) > 0:
        print("[AI Debug] Wajah terdeteksi setelah rotasi 90 derajat searah jarum jam.")
        return img_90, faces_90
        
    # 3. Try 180 degrees
    img_180 = cv2.rotate(img, cv2.ROTATE_180)
    h_180, w_180 = img_180.shape[:2]
    _detector.setInputSize((w_180, h_180))
    _, faces_180 = _detector.detect(img_180)
    if faces_180 is not None and len(faces_180) > 0:
        print("[AI Debug] Wajah terdeteksi setelah rotasi 180 derajat.")
        return img_180, faces_180
        
    # 4. Try 270 degrees (90 counter-clockwise)
    img_270 = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    h_270, w_270 = img_270.shape[:2]
    _detector.setInputSize((w_270, h_270))
    _, faces_270 = _detector.detect(img_270)
    if faces_270 is not None and len(faces_270) > 0:
        print("[AI Debug] Wajah terdeteksi setelah rotasi 270 derajat (berlawanan jarum jam).")
        return img_270, faces_270
        
    return img, None

def verify_faces(image_path_1, image_path_2, threshold=0.25):
    """
    Compares face in image_path_1 with face in image_path_2.
    Returns (is_match, similarity_score, error_message)
    """
    if not init_models():
        return False, 0.0, "Model pengenal wajah gagal dimuat"
        
    try:
        # Load images
        img1 = cv2.imread(str(image_path_1))
        img2 = cv2.imread(str(image_path_2))
        
        if img1 is None:
            print(f"[AI Debug] Gagal membaca gambar scan: {image_path_1}")
            return False, 0.0, f"Gagal membaca gambar di: {image_path_1}"
        if img2 is None:
            print(f"[AI Debug] Gagal membaca gambar terdaftar: {image_path_2}")
            return False, 0.0, f"Gagal membaca gambar di: {image_path_2}"
            
        # Print original sizes
        print(f"[AI Debug] Ukuran asli: Scan={img1.shape[:2]}, Terdaftar={img2.shape[:2]}")
        
        # Resize images to bring face dimensions into YuNet's optimal range (10x10 to 300x300)
        # This fixes detection failures on high-res photos and speeds up CPU processing
        img1 = resize_image_to_target_width(img1, 320)
        img2 = resize_image_to_target_width(img2, 320)
        
        # Detect faces with orientation correction
        img1, faces1 = detect_face_with_rotation_fallback(img1)
        img2, faces2 = detect_face_with_rotation_fallback(img2)
        
        if faces1 is None or len(faces1) == 0:
            print("[AI Debug] Wajah tidak terdeteksi pada gambar scan")
            return False, 0.0, "Tidak mendeteksi wajah pada gambar input scan."
        if faces2 is None or len(faces2) == 0:
            print("[AI Debug] Wajah tidak terdeteksi pada gambar terdaftar di database")
            return False, 0.0, "Tidak mendeteksi wajah pada gambar terdaftar (database)."
            
        print(f"[AI Debug] Wajah terdeteksi. Jumlah: Scan={len(faces1)}, Terdaftar={len(faces2)}")
            
        # Align and extract features
        aligned1 = _recognizer.alignCrop(img1, faces1[0])
        aligned2 = _recognizer.alignCrop(img2, faces2[0])
        
        feat1 = _recognizer.feature(aligned1).copy()
        feat2 = _recognizer.feature(aligned2).copy()
        
        # FR_COSINE returns value between -1 and 1
        score = _recognizer.match(feat1, feat2, cv2.FaceRecognizerSF_FR_COSINE)
        
        # Threshold for SFace is around 0.363 by default, lowered to 0.25 for leniency
        is_match = score >= threshold
        
        print(f"[AI Debug] Skor similarity Cosine: {score:.4f} (Threshold: {threshold}) -> Cocok: {is_match}")
        
        return is_match, float(score), None
    except Exception as e:
        print(f"[AI Debug] Terjadi kesalahan: {str(e)}")
        return False, 0.0, f"Error selama verifikasi wajah: {str(e)}"
