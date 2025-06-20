import cv2
import numpy as np
import mediapipe as mp
import base64
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from core.config import settings

logger = logging.getLogger(__name__)

class MediaPipeService:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = None
        self.is_ready_flag = False
        
        # Yoga poses reference angles (simplified)
        self.pose_references = {
            "mountain": {"left_elbow": 180, "right_elbow": 180, "left_knee": 180, "right_knee": 180},
            "warrior_1": {"left_knee": 90, "right_knee": 180, "left_elbow": 180, "right_elbow": 180},
            "downward_dog": {"left_elbow": 180, "right_elbow": 180, "left_knee": 180, "right_knee": 180},
            "tree": {"left_knee": 90, "right_knee": 180, "left_elbow": 180, "right_elbow": 180},
            "plank": {"left_elbow": 180, "right_elbow": 180, "left_knee": 180, "right_knee": 180}
        }

    async def initialize(self):
        """Initialize MediaPipe Pose"""
        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=settings.MEDIAPIPE_MODEL_COMPLEXITY,
                enable_segmentation=False,
                min_detection_confidence=settings.MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=settings.MEDIAPIPE_MIN_TRACKING_CONFIDENCE
            )
            self.is_ready_flag = True
            logger.info("MediaPipe Pose initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe: {e}")
            raise

    def is_ready(self) -> bool:
        return self.is_ready_flag

    async def process_frame(self, frame_data: str) -> Dict:
        """Process video frame for pose detection"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(frame_data.split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Invalid image data"}
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                # Extract landmarks
                landmarks = self._extract_landmarks(results.pose_landmarks)
                
                # Calculate joint angles
                joint_angles = self._calculate_joint_angles(landmarks)
                
                # Detect pose type
                detected_pose = self._classify_pose(joint_angles)
                
                # Generate corrections
                corrections = self._generate_corrections(joint_angles, detected_pose)
                
                # Calculate pose quality score
                quality_score = self._calculate_pose_quality(joint_angles, detected_pose)
                
                return {
                    "pose_detected": True,
                    "landmarks": landmarks,
                    "joint_angles": joint_angles,
                    "detected_pose": detected_pose,
                    "corrections": corrections,
                    "quality_score": quality_score,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                return {
                    "pose_detected": False,
                    "message": "No pose detected. Please ensure you're visible in the camera."
                }
                
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return {"error": f"Processing failed: {str(e)}"}

    def _extract_landmarks(self, pose_landmarks) -> List[Dict]:
        """Extract pose landmarks as list of dictionaries"""
        landmarks = []
        for idx, landmark in enumerate(pose_landmarks.landmark):
            landmarks.append({
                "id": idx,
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            })
        return landmarks

    def _calculate_joint_angles(self, landmarks: List[Dict]) -> Dict:
        """Calculate key joint angles"""
        try:
            angles = {}
            
            # Left elbow angle
            if len(landmarks) > 15:
                left_shoulder = np.array([landmarks[11]['x'], landmarks[11]['y']])
                left_elbow = np.array([landmarks[13]['x'], landmarks[13]['y']])
                left_wrist = np.array([landmarks[15]['x'], landmarks[15]['y']])
                angles['left_elbow'] = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
            
            # Right elbow angle
            if len(landmarks) > 16:
                right_shoulder = np.array([landmarks[12]['x'], landmarks[12]['y']])
                right_elbow = np.array([landmarks[14]['x'], landmarks[14]['y']])
                right_wrist = np.array([landmarks[16]['x'], landmarks[16]['y']])
                angles['right_elbow'] = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # Left knee angle
            if len(landmarks) > 27:
                left_hip = np.array([landmarks[23]['x'], landmarks[23]['y']])
                left_knee = np.array([landmarks[25]['x'], landmarks[25]['y']])
                left_ankle = np.array([landmarks[27]['x'], landmarks[27]['y']])
                angles['left_knee'] = self._calculate_angle(left_hip, left_knee, left_ankle)
            
            # Right knee angle
            if len(landmarks) > 28:
                right_hip = np.array([landmarks[24]['x'], landmarks[24]['y']])
                right_knee = np.array([landmarks[26]['x'], landmarks[26]['y']])
                right_ankle = np.array([landmarks[28]['x'], landmarks[28]['y']])
                angles['right_knee'] = self._calculate_angle(right_hip, right_knee, right_ankle)
            
            return angles
            
        except Exception as e:
            logger.error(f"Angle calculation error: {e}")
            return {}

    def _calculate_angle(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        """Calculate angle between three points"""
        try:
            ba = a - b
            bc = c - b
            
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
            angle = np.arccos(cosine_angle)
            
            return np.degrees(angle)
        except:
            return 0.0

    def _classify_pose(self, joint_angles: Dict) -> str:
        """Classify the detected pose"""
        if not joint_angles:
            return "unknown"
        
        # Simple pose classification based on joint angles
        left_knee = joint_angles.get('left_knee', 180)
        right_knee = joint_angles.get('right_knee', 180)
        left_elbow = joint_angles.get('left_elbow', 180)
        right_elbow = joint_angles.get('right_elbow', 180)
        
        # Basic pose detection logic
        if abs(left_knee - 90) < 20 and abs(right_knee - 180) < 20:
            return "warrior_1"
        elif abs(left_knee - 90) < 30 and abs(right_knee - 180) < 20:
            return "tree"
        elif abs(left_elbow - 180) < 20 and abs(right_elbow - 180) < 20:
            if abs(left_knee - 180) < 20 and abs(right_knee - 180) < 20:
                return "mountain"
        
        return "general_pose"

    def _generate_corrections(self, joint_angles: Dict, pose_type: str) -> List[str]:
        """Generate pose corrections"""
        corrections = []
        
        if pose_type in self.pose_references:
            reference = self.pose_references[pose_type]
            
            for joint, current_angle in joint_angles.items():
                if joint in reference:
                    target_angle = reference[joint]
                    difference = abs(current_angle - target_angle)
                    
                    if difference > 15:  # Threshold for correction
                        if current_angle > target_angle:
                            corrections.append(f"Decrease {joint.replace('_', ' ')} angle by {difference:.1f} degrees")
                        else:
                            corrections.append(f"Increase {joint.replace('_', ' ')} angle by {difference:.1f} degrees")
        
        if not corrections:
            corrections.append("Great form! Keep holding the pose.")
        
        return corrections

    def _calculate_pose_quality(self, joint_angles: Dict, pose_type: str) -> float:
        """Calculate pose quality score (0-100)"""
        if pose_type not in self.pose_references or not joint_angles:
            return 50.0
        
        reference = self.pose_references[pose_type]
        total_error = 0
        joint_count = 0
        
        for joint, current_angle in joint_angles.items():
            if joint in reference:
                target_angle = reference[joint]
                error = abs(current_angle - target_angle) / 180.0  # Normalize to 0-1
                total_error += error
                joint_count += 1
        
        if joint_count == 0:
            return 50.0
        
        average_error = total_error / joint_count
        quality_score = max(0, 100 - (average_error * 100))
        
        return round(quality_score, 1)
