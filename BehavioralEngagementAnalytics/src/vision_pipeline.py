import cv2
import mediapipe as mp
import time
from typing import Optional

from .face_presence_tracker import FacePresenceTracker
from .feature_engineering import (
    FrameLogger, WindowAggregator,
    BlinkState, compute_pose_proxies, compute_ear, update_blink
)


def run_webcam_feature_pipeline(
    face_detector_model_path: str,
    face_landmarker_model_path: Optional[str] = None,  
    camera_index: int = 0,
    score_threshold: float = 0.5,
    ear_threshold: float = 0.23,
):
    # MediaPipe Task Aliases
    BaseOptions = mp.tasks.BaseOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions

    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

    # Configure face detector (BlazeFace)
    det_options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=face_detector_model_path),
        running_mode=VisionRunningMode.VIDEO,
        min_detection_confidence=score_threshold,
    )

    # Configure face landmarker
    landmarker = None
    if face_landmarker_model_path:
        lm_options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=face_landmarker_model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1,
        )
        landmarker = FaceLandmarker.create_from_options(lm_options)

    # Presence tracker & blink state
    presence = FacePresenceTracker(found_after=3, lost_after=10, score_threshold=score_threshold)
    blink_state = BlinkState()
    last_seen_ms: Optional[int] = None

    # Logging
    frames_logger = FrameLogger(out_path="data/frames.csv")
    aggregator = WindowAggregator(window_sizes_s=(5, 30))

    # Open camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not access the camera.")

    print("Press 'q' to quit.")
    start_time = time.time()

    with FaceDetector.create_from_options(det_options) as detector:
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                print("Error: Failed to read from camera.")
                break

            frame_bgr = cv2.flip(frame_bgr, 1)
            h, w = frame_bgr.shape[:2]

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

            # Detect faces (boxes + confidence)
            det_result = detector.detect_for_video(mp_image, timestamp_ms)
            detections = det_result.detections

            # face_present & face_confidence
            face_present = 0
            face_confidence = 0.0
            if detections:
                # take the best detection score
                best = 0.0
                for d in detections:
                    if d.categories:
                        best = max(best, float(d.categories[0].score))
                face_confidence = best
                if best >= score_threshold:
                    face_present = 1

            # update last_seen
            if face_present == 1:
                last_seen_ms = timestamp_ms

            if last_seen_ms is None:
                time_since_seen_ms = float("nan")
            else:
                time_since_seen_ms = float(max(0, timestamp_ms - last_seen_ms))

            # Draw detections (boxes + score)
            if detections:
                for det in detections:
                    bbox = det.bounding_box
                    x1 = max(0, bbox.origin_x)
                    y1 = max(0, bbox.origin_y)
                    x2 = min(w, x1 + bbox.width)
                    y2 = min(h, y1 + bbox.height)
                    cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    if det.categories:
                        score = det.categories[0].score
                        cv2.putText(
                            frame_bgr,
                            f"{score:.2f}",
                            (x1, max(0, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2,
                        )

            # Presence events (FOUND/LOST) 
            events = presence.update(detections, timestamp_ms)
            for e in events:
                if e.event == "FOUND":
                    print(f"[{e.timestamp_ms} ms] FACE FOUND")
                elif e.event == "LOST":
                    if e.duration_ms is not None:
                        print(f"[{e.timestamp_ms} ms] FACE LOST (session: {e.duration_ms/1000.0:.2f}s)")
                    else:
                        print(f"[{e.timestamp_ms} ms] FACE LOST")

            # Landmark-based features
            roll_proxy = float("nan")
            yaw_proxy = float("nan")
            pitch_proxy = float("nan")
            ear_left = float("nan")
            ear_right = float("nan")
            ear_mean = float("nan")
            blink = 0
            blink_duration_ms = float("nan")

            if landmarker is not None and face_present == 1:
                lm_result = landmarker.detect_for_video(mp_image, timestamp_ms)

                if lm_result.face_landmarks and len(lm_result.face_landmarks) > 0:
                    lms = lm_result.face_landmarks[0]  # one face

                    pose = compute_pose_proxies(lms, w, h)
                    roll_proxy = pose["roll_proxy_deg"]
                    yaw_proxy = pose["yaw_proxy"]
                    pitch_proxy = pose["pitch_proxy"]

                    ear_vals = compute_ear(lms, w, h)
                    ear_left = ear_vals["ear_left"]
                    ear_right = ear_vals["ear_right"]
                    ear_mean = ear_vals["ear_mean"]

                    blink_info = update_blink(
                        ear_value=ear_mean,
                        timestamp_ms=timestamp_ms,
                        state=blink_state,
                        ear_threshold=ear_threshold,
                    )
                    blink = blink_info["blink"]
                    blink_duration_ms = blink_info["blink_duration_ms"]

            # Log per-frame row
            frames_logger.add({
                "timestamp_ms": timestamp_ms,
                "face_present": int(face_present),
                "face_confidence": float(face_confidence),
                "time_since_face_seen_ms": float(time_since_seen_ms),

                "roll_proxy_deg": float(roll_proxy),
                "yaw_proxy": float(yaw_proxy),
                "pitch_proxy": float(pitch_proxy),

                "ear_left": float(ear_left),
                "ear_right": float(ear_right),
                "ear_mean": float(ear_mean),

                "blink": int(blink),
                "blink_duration_ms": float(blink_duration_ms),
            })

            # Show frame
            cv2.imshow("Vision Pipeline", frame_bgr)
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break

    # cleanup
    cap.release()
    cv2.destroyAllWindows()

    if landmarker is not None:
        landmarker.close()

    # write CSVs
    frames_logger.write()
    window_rows = aggregator.aggregate(frames_logger.rows)
    aggregator.write("data/features.csv", window_rows)

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f}s")
    print("Wrote: data/frames.csv")
    print("Wrote: data/features.csv")


def main():
    # BlazeFace face detector model
    face_detector_model_path = "models/blaze_face_short_range.tflite"

    # Face Landmarker model (enables EAR/blink/head pose proxies)
    face_landmarker_model_path = "models/face_landmarker.task"  # set None if you don't have it

    run_webcam_feature_pipeline(
        face_detector_model_path=face_detector_model_path,
        face_landmarker_model_path=face_landmarker_model_path,
        camera_index=0,
        score_threshold=0.5,
        ear_threshold=0.23,
    )


if __name__ == "__main__":
    main()
