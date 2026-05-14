import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .utils import resource_path

class HandTracker:
    def __init__(
        self,
        model_path=None,
        max_hands=2,
        detection_confidence=0.7,
        presence_confidence=0.6,
        tracking_confidence=0.6,
    ):
        if model_path is None:
            model_path = resource_path("assets/models/hand_landmarker.task")
            
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=presence_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        # Memória das mãos para estabilidade de lado
        self.prev_hands = {"left": None, "right": None}

    def find_hands(self, frame, draw=True):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        timestamp_ms = int(time.time() * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        h, w, _ = frame.shape
        detected_hands = []

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                hand_center = self._get_hand_center(hand_landmarks)
                detected_hands.append(hand_center)
                if draw:
                    self._draw_landmarks(frame, hand_landmarks, w, h)

        assigned_hands = self._assign_sides_with_memory(detected_hands)
        return frame, assigned_hands

    def _get_hand_center(self, landmarks):
        return {
            "x": sum([lm.x for lm in landmarks]) / len(landmarks),
            "y": sum([lm.y for lm in landmarks]) / len(landmarks)
        }

    def _assign_sides_with_memory(self, detected_hands):
        """Lógica inteligente para manter consistência de qual mão é qual."""
        current_hands = {"left": None, "right": None}
        
        if not detected_hands:
            return current_hands

        # Se detectou duas mãos, a da esquerda (menor X) é left, a outra é right
        if len(detected_hands) >= 2:
            detected_hands.sort(key=lambda h: h["x"])
            current_hands["left"] = detected_hands[0]
            current_hands["right"] = detected_hands[1]
        
        # Se detectou apenas uma mão, usa memória ou posição relativa
        elif len(detected_hands) == 1:
            hand = detected_hands[0]
            
            # Se tínhamos mãos no frame anterior, associa pela proximidade
            dist_left = abs(hand["x"] - self.prev_hands["left"]["x"]) if self.prev_hands["left"] else 1.0
            dist_right = abs(hand["x"] - self.prev_hands["right"]["x"]) if self.prev_hands["right"] else 1.0
            
            if dist_left < dist_right and dist_left < 0.3:
                current_hands["left"] = hand
            elif dist_right < dist_left and dist_right < 0.3:
                current_hands["right"] = hand
            else:
                # Fallback para posição absoluta se a memória falhar
                if hand["x"] < 0.5: current_hands["left"] = hand
                else: current_hands["right"] = hand

        # Atualiza memória (apenas se detectado)
        if current_hands["left"]: self.prev_hands["left"] = current_hands["left"]
        if current_hands["right"]: self.prev_hands["right"] = current_hands["right"]
        
        return current_hands

    def _draw_landmarks(self, frame, landmarks, w, h):
        for lm in landmarks:
            px, py = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (px, py), 2, (0, 255, 0), -1)

    def close(self):
        self.landmarker.close()
