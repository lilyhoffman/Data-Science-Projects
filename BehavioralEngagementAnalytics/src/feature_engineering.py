import math
import os
import csv
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import numpy as np


# FaceMesh landmark indices for EAR (standard/common)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Useful points for pose proxies (FaceMesh)
NOSE_TIP = 1        # common nose tip-ish
LEFT_EYE_CORNER = 33
RIGHT_EYE_CORNER = 263


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_mean(x: np.ndarray) -> float:
    return float(np.nanmean(x)) if np.any(~np.isnan(x)) else float("nan")


def safe_std(x: np.ndarray) -> float:
    return float(np.nanstd(x)) if np.any(~np.isnan(x)) else float("nan")


def slope_over_time(t: np.ndarray, y: np.ndarray) -> float:
    """
    Returns slope of y vs t using a simple linear fit.
    Ignores NaNs.
    """
    mask = (~np.isnan(t)) & (~np.isnan(y))
    if mask.sum() < 2:
        return float("nan")
    tt = t[mask].astype(float)
    yy = y[mask].astype(float)
    # normalize time for stability
    tt = tt - tt.min()
    if np.allclose(tt.max(), 0):
        return float("nan")
    m, _b = np.polyfit(tt, yy, 1)
    return float(m)


def dist(p1, p2) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def ear_from_eye_points(points: List[tuple]) -> float:
    """
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    points order must be: [p1, p2, p3, p4, p5, p6]
    """
    p1, p2, p3, p4, p5, p6 = points
    denom = 2.0 * dist(p1, p4)
    if denom <= 1e-9:
        return float("nan")
    return (dist(p2, p6) + dist(p3, p5)) / denom


def lm_to_px(lm, w: int, h: int) -> tuple:
    # MediaPipe landmarks are usually normalized [0..1]
    return (lm.x * w, lm.y * h)


@dataclass
class BlinkState:
    in_blink: bool = False
    blink_start_ms: Optional[int] = None


class FrameLogger:
    """
    Collects per-frame features and writes frames.csv.
    """
    def __init__(self, out_path: str):
        self.out_path = out_path
        self.rows: List[Dict[str, Any]] = []

    def add(self, row: Dict[str, Any]) -> None:
        self.rows.append(row)

    def write(self) -> None:
        if not self.rows:
            return
        ensure_dir(os.path.dirname(self.out_path))
        fieldnames = list(self.rows[0].keys())
        with open(self.out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(self.rows)


class WindowAggregator:
    """
    Builds features.csv with tumbling windows at 5s and 30s.
    """
    def __init__(self, window_sizes_s=(5, 30)):
        self.window_sizes_s = window_sizes_s

    def aggregate(self, frame_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not frame_rows:
            return []

        # Convert lists to arrays
        t = np.array([r["timestamp_ms"] for r in frame_rows], dtype=float)

        # helper to pull float arrays (missing -> nan)
        def col(name: str) -> np.ndarray:
            vals = []
            for r in frame_rows:
                v = r.get(name, float("nan"))
                if v is None:
                    v = float("nan")
                vals.append(v)
            return np.array(vals, dtype=float)

        face_present = col("face_present")
        face_conf = col("face_confidence")
        time_since_seen = col("time_since_face_seen_ms")
        roll = col("roll_proxy_deg")
        yaw = col("yaw_proxy")
        pitch = col("pitch_proxy")
        ear = col("ear_mean")
        blink = col("blink")
        blink_dur = col("blink_duration_ms")

        out: List[Dict[str, Any]] = []
        t0 = int(t.min())
        tmax = int(t.max())

        for ws in self.window_sizes_s:
            ws_ms = ws * 1000

            # tumbling windows [start, start+ws)
            start = (t0 // ws_ms) * ws_ms
            while start <= tmax:
                end = start + ws_ms
                mask = (t >= start) & (t < end)
                if mask.sum() > 0:
                    # metrics
                    fp = face_present[mask]
                    fc = face_conf[mask]
                    ts = time_since_seen[mask]
                    rr = roll[mask]
                    yy = yaw[mask]
                    pp = pitch[mask]
                    ee = ear[mask]
                    bb = blink[mask]
                    bd = blink_dur[mask]
                    tt = t[mask]

                    blink_count = int(np.nansum(bb)) if np.any(~np.isnan(bb)) else 0
                    blink_rate = blink_count / float(ws)  # blinks per second

                    row = {
                        "window_start_ms": int(start),
                        "window_end_ms": int(end),
                        "window_size_s": int(ws),

                        "face_present_pct": safe_mean(fp),
                        "face_conf_mean": safe_mean(fc),
                        "time_since_seen_max_ms": float(np.nanmax(ts)) if np.any(~np.isnan(ts)) else float("nan"),

                        "roll_mean_deg": safe_mean(rr),
                        "roll_std_deg": safe_std(rr),

                        "yaw_mean": safe_mean(yy),
                        "yaw_std": safe_std(yy),

                        "pitch_mean": safe_mean(pp),
                        "pitch_std": safe_std(pp),

                        "ear_mean": safe_mean(ee),
                        "ear_std": safe_std(ee),

                        "blink_count": blink_count,
                        "blink_rate_per_s": blink_rate,
                        "blink_duration_mean_ms": safe_mean(bd),
                    }

                    # trend features for 30s windows (or any window >= 30s)
                    if ws >= 30:
                        row["ear_slope_per_ms"] = slope_over_time(tt, ee)
                        row["blink_duration_slope_per_ms"] = slope_over_time(tt, bd)

                    out.append(row)

                start = end

        return out

    def write(self, out_path: str, window_rows: list[dict]) -> None:
        if not window_rows:
            return

        ensure_dir(os.path.dirname(out_path))

        # Collect ALL keys across all rows so header matches everything
        all_keys = set()
        for r in window_rows:
            all_keys.update(r.keys())

        # Stable order: put core columns first, then the rest alphabetically
        preferred = ["window_start_ms", "window_end_ms", "window_size_s"]
        fieldnames = preferred + sorted([k for k in all_keys if k not in preferred])

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(window_rows)



def compute_pose_proxies(landmarks, w: int, h: int) -> Dict[str, float]:
    """
    Simple proxies (not true degrees):
    - roll: angle between eye corners
    - yaw: nose x offset from eye midpoint / eye distance
    - pitch: nose y offset from eye midpoint / eye distance
    """
    le = lm_to_px(landmarks[LEFT_EYE_CORNER], w, h)
    re = lm_to_px(landmarks[RIGHT_EYE_CORNER], w, h)
    nose = lm_to_px(landmarks[NOSE_TIP], w, h)

    eye_mid = ((le[0] + re[0]) / 2.0, (le[1] + re[1]) / 2.0)
    eye_dist = dist(le, re)
    if eye_dist <= 1e-9:
        return {"roll_proxy_deg": float("nan"), "yaw_proxy": float("nan"), "pitch_proxy": float("nan")}

    # roll in degrees
    roll = math.degrees(math.atan2(re[1] - le[1], re[0] - le[0]))

    # normalized offsets (dimensionless)
    yaw = (nose[0] - eye_mid[0]) / eye_dist
    pitch = (nose[1] - eye_mid[1]) / eye_dist

    return {"roll_proxy_deg": float(roll), "yaw_proxy": float(yaw), "pitch_proxy": float(pitch)}


def compute_ear(landmarks, w: int, h: int) -> Dict[str, float]:
    def points(idxs):
        return [lm_to_px(landmarks[i], w, h) for i in idxs]

    left_pts = points(LEFT_EYE)
    right_pts = points(RIGHT_EYE)

    ear_l = ear_from_eye_points(left_pts)
    ear_r = ear_from_eye_points(right_pts)
    ear_m = np.nanmean([ear_l, ear_r]) if not (math.isnan(ear_l) and math.isnan(ear_r)) else float("nan")

    return {"ear_left": float(ear_l), "ear_right": float(ear_r), "ear_mean": float(ear_m)}


def update_blink(ear_value: float, timestamp_ms: int, state: BlinkState,
                 ear_threshold: float = 0.23, min_blink_ms: int = 60, max_blink_ms: int = 500) -> Dict[str, Any]:
    """
    Blink detection from EAR:
    - Enter blink when EAR < threshold
    - Complete blink when EAR rises back above threshold
    - Only count if duration within [min, max]
    """
    blink_event = 0
    blink_duration_ms = float("nan")

    if math.isnan(ear_value):
        # no update if no landmarks
        return {"blink": 0, "blink_duration_ms": float("nan"), "in_blink": state.in_blink}

    if (not state.in_blink) and (ear_value < ear_threshold):
        state.in_blink = True
        state.blink_start_ms = timestamp_ms

    elif state.in_blink and (ear_value >= ear_threshold):
        # blink ends
        state.in_blink = False
        if state.blink_start_ms is not None:
            dur = timestamp_ms - state.blink_start_ms
            if min_blink_ms <= dur <= max_blink_ms:
                blink_event = 1
                blink_duration_ms = float(dur)
        state.blink_start_ms = None

    return {"blink": blink_event, "blink_duration_ms": blink_duration_ms, "in_blink": state.in_blink}
