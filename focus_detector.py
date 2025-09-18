import threading, time, cv2, mediapipe as mp, numpy as np, math

# Shared state
_latest_state = 1            # 0 = focused, 1 = distracted
_latest_label = "Distracted"
_lock = threading.Lock()
_running = False
_thread = None

MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (0.0, -63.6, -12.5),
    (-43.3, 32.7, -26.0),
    (43.3, 32.7, -26.0),
    (-28.9, -28.9, -24.1),
    (28.9, -28.9, -24.1)
])
LANDMARK_IDS = [1, 152, 33, 263, 61, 291]
LEFT_IRIS_IDS = [468, 469, 470, 471]
RIGHT_IRIS_IDS = [473, 474, 475, 476]
LEFT_EYE_CORNER_IDS = [33, 133]
RIGHT_EYE_CORNER_IDS = [362, 263]

def _detect_loop(camera_index=0):
    global _latest_state, _latest_label, _running
    cap = cv2.VideoCapture(camera_index)
    mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )

    while _running:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        h, w = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_face_mesh.process(frame_rgb)

        state, label = 1, "Distracted"
        if results.multi_face_landmarks:
            try:
                lm = results.multi_face_landmarks[0].landmark
                image_points = np.array([(lm[i].x * w, lm[i].y * h) for i in LANDMARK_IDS], dtype="double")
                focal_length = w
                center = (w / 2, h / 2)
                camera_matrix = np.array(
                    [[focal_length, 0, center[0]],
                     [0, focal_length, center[1]],
                     [0, 0, 1]], dtype="double")
                dist_coeffs = np.zeros((4, 1))

                success, rvec, tvec = cv2.solvePnP(
                    MODEL_POINTS, image_points, camera_matrix,
                    dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
                )
                rmat, _ = cv2.Rodrigues(rvec)
                sy = math.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
                yaw = math.degrees(math.atan2(rmat[1, 0], rmat[0, 0]))
                pitch = math.degrees(math.atan2(-rmat[2, 0], sy))

                def iris_offset(iris_ids, corner_ids):
                    iris_x = np.mean([lm[i].x for i in iris_ids])
                    left_x = lm[corner_ids[0]].x
                    right_x = lm[corner_ids[1]].x
                    return 0.5 if right_x == left_x else (iris_x - left_x) / (right_x - left_x)

                left_ratio = iris_offset(LEFT_IRIS_IDS, LEFT_EYE_CORNER_IDS)
                right_ratio = iris_offset(RIGHT_IRIS_IDS, RIGHT_EYE_CORNER_IDS)
                gaze_ratio = (left_ratio + right_ratio) / 2  # 0=left, 0.5=center, 1=right

                if abs(yaw) < 20 and 0.3 < gaze_ratio < 0.7:
                    state = 0
                    label = f"Focused | Yaw:{yaw:.1f} Pitch:{pitch:.1f}"
                else:
                    label = f"Distracted | Yaw:{yaw:.1f} Pitch:{pitch:.1f}"
            except Exception:
                state, label = 1, "Distracted (error)"

        with _lock:
            _latest_state, _latest_label = state, label

        disp = frame.copy()
        cv2.putText(disp, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0) if state == 0 else (0, 0, 255), 2)
        cv2.imshow("Detector (ESC to stop)", disp)
        if cv2.waitKey(1) & 0xFF == 27:
            _running = False
            break

    mp_face_mesh.close()
    cap.release()
    cv2.destroyAllWindows()

def start_detector(camera_index=0):
    """Start background detection thread."""
    global _running, _thread
    if _running: return
    _running = True
    _thread = threading.Thread(target=_detect_loop, args=(camera_index,), daemon=True)
    _thread.start()
    time.sleep(0.5)  # warm-up

def get_latest_state():
    """Most recent 0/1 state."""
    with _lock:
        return _latest_state

def detector_running():
    """True while detector thread is alive."""
    return _running

def stop_detector():
    """Stop detector and release resources."""
    global _running, _thread
    _running = False
    if _thread:
        _thread.join(timeout=2)
