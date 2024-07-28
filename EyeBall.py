import streamlit as st
import cv2
import dlib
import numpy as np
import time

# Initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

def get_eye_landmarks(landmarks, eye_points):
    return np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in eye_points], np.int32)

def get_eye_center(eye_landmarks):
    M = cv2.moments(eye_landmarks)
    if M["m00"] == 0:
        return (0, 0)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def determine_eye_position(eye_center, eye_box):
    x, y, w, h = eye_box
    left_bound = x + w // 4
    right_bound = x + 3 * w // 4
    if eye_center[0] < left_bound:
        return "left"
    elif eye_center[0] > right_bound:
        return "right"
    else:
        return "center"

def main():
    st.title("Eye Tracking Application")
    st.markdown("This application tracks your eye movements and gives warnings if you look away from the screen for more than 5 seconds.")

    run = st.checkbox('Run Eye Tracking')

    FRAME_WINDOW = st.image([])

    if run:
        cap = cv2.VideoCapture(0)

        eyes_on_screen_start_time = time.time()
        eyes_off_screen_start_time = None
        warning_issued = False

        while run:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            if faces:
                eyes_off_screen_start_time = None
                if warning_issued:
                    st.warning("Warning resolved. Eyes back on screen.")
                    warning_issued = False
                for face in faces:
                    landmarks = predictor(gray, face)

                    left_eye_points = [36, 37, 38, 39, 40, 41]
                    right_eye_points = [42, 43, 44, 45, 46, 47]

                    left_eye_landmarks = get_eye_landmarks(landmarks, left_eye_points)
                    right_eye_landmarks = get_eye_landmarks(landmarks, right_eye_points)

                    left_eye_center = get_eye_center(left_eye_landmarks)
                    right_eye_center = get_eye_center(right_eye_landmarks)

                    left_eye_box = cv2.boundingRect(left_eye_landmarks)
                    right_eye_box = cv2.boundingRect(right_eye_landmarks)

                    left_eye_position = determine_eye_position(left_eye_center, left_eye_box)
                    right_eye_position = determine_eye_position(right_eye_center, right_eye_box)

                    cv2.putText(frame, f"Left Eye: {left_eye_position}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Right Eye: {right_eye_position}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.polylines(frame, [left_eye_landmarks], True, (0, 255, 0), 1)
                    cv2.polylines(frame, [right_eye_landmarks], True, (0, 255, 0), 1)

                    cv2.circle(frame, left_eye_center, 2, (0, 0, 255), -1)
                    cv2.circle(frame, right_eye_center, 2, (0, 0, 255), -1)
            else:
                if eyes_off_screen_start_time is None:
                    eyes_off_screen_start_time = time.time()
                eyes_off_screen_duration = time.time() - eyes_off_screen_start_time
                if eyes_off_screen_duration > 5 and not warning_issued:
                    st.error("Warning: Eyes off screen for more than 5 seconds!")
                    warning_issued = True

            eyes_on_screen_duration = time.time() - eyes_on_screen_start_time

            cv2.putText(frame, f"Eyes On Screen: {int(eyes_on_screen_duration)}s", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            FRAME_WINDOW.image(frame, channels='BGR')

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
