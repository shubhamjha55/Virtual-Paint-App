import cv2
import mediapipe as mp
import time
import Arduino

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

board = Arduino("9600", port="COM5")  
board.pinMode(9, "OUTPUT")
cap = cv2.VideoCapture(0)

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image_hight, image_width, _ = image.shape
    
    if results.multi_hand_landmarks:

      #print(results.multi_handedness) # esquerda ou direita
      for hand_landmarks in results.multi_hand_landmarks:
      # Coordenadas do indicador e do polegar
          indicador_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width
          indicador_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_hight

          polegar_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * image_width
          polegar_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * image_hight

          fade = (abs(indicador_x - polegar_x), abs(indicador_y - polegar_y))
          print(fade[0])
          x = _map(fade[0], 30, 210, 0, 255)
          board.analogWrite(9, x)


      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()