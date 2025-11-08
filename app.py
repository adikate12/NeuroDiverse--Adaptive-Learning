from flask import Flask, render_template, Response, jsonify
import cv2
import time
from rl_agent import RLAgent, DrowsinessDetector
from scrape_lessons import fetch_lessons

app = Flask(__name__)

# Initialize camera and RL agent
camera = cv2.VideoCapture(0)
agent = RLAgent()
last_popup_time = 0
popup_cooldown = 10  # seconds

# Load Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Lessons for home page
lessons = fetch_lessons()

def generate_frames():
    """Generate webcam frames with focus/distracted state."""
    global last_popup_time
    distraction_counter = 0
    focus_threshold = 20  # Number of frames before considered distracted

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        state = "focused"

        if len(faces) == 0:
            distraction_counter += 1
            state = "distracted"
        else:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)

                # Draw rectangles for face and eyes
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

                # Update focus state based on eye detection
                if len(eyes) < 1:
                    distraction_counter += 1
                    state = "distracted"
                else:
                    distraction_counter = 0
                    state = "focused"

        # RL agent action (optional logic)
        _ = agent.choose_action(state)

        # Display state text on frame
        color = (0, 255, 0) if state == "focused" else (0, 0, 255)
        cv2.putText(frame, f"State: {state.upper()}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # Encode frame for browser streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    lessons = fetch_lessons()
    main_video = lessons[0] if lessons else {
        "title": "8th Grade Science",
        "url": "https://www.youtube.com/watch?v=ur0hCdne2Ew",
        "description": "Learn about exciting science concepts for Class 8."
    }
    return render_template('index.html', lessons=lessons, main_video=main_video)


@app.route('/video_feed')
def video_feed():
    """Live webcam video stream."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/check_distraction')
def check_distraction():
    """Simple API endpoint for popup trigger."""
    global last_popup_time
    if (time.time() - last_popup_time) < 10:
        return jsonify({"distracted": True})
    return jsonify({"distracted": False})


if __name__ == '__main__':
    app.run(debug=True)

