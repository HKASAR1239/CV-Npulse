#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-reactive ArUco object selection by pointer (2D).
• Ruler: ID 10
• Objects: IDs 1-4 (here but can extends to n)
• iPhone Continuity → AVFoundation backend
"""

import cv2, numpy as np, math, time

# ────────── CONFIG ──────────
POINTER_ID       = 10
OBJ_IDS          = [1, 2, 3, 4] #can extends to n
CONE_DEG         = 12        # Half-angle of the cone
HOLD_FRAMES      = 2         # Number of frames to confirm a new candidate
DIR_THR_DEG      = 4         # Ruler angle change > 4° ⇒ immediate switch
DEBUG            = False
# ────────────────────────────

# UI
FONT, FSCALE, THICK = cv2.FONT_HERSHEY_DUPLEX, 1.1, 3
BANNER_H            = 50
CLR_OBJ, CLR_SEL    = (255,0,0), (0,255,0)
CLR_RAY, CLR_RAY_B  = (0,255,255), (0,128,128)

DICT  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
DETP  = cv2.aruco.DetectorParameters()

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    raise SystemExit("Camera inaccessible")

tan_cone  = math.tan(math.radians(CONE_DEG))
cos_dir   = math.cos(math.radians(DIR_THR_DEG))
bary      = lambda p: p.mean(axis=0)
log       = print if DEBUG else lambda *a, **k: None

# State
cur_id, cand_id, cand_cnt = None, None, 0
prev_dir = None           # Last direction (unit vector)

while True:
    ok, frame = cap.read()
    if not ok: break
    H, W = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, DICT, parameters=DETP)

    cand_now = None
    if ids is not None:
        ids = ids.flatten()
        ctrs = {i: bary(c[0]) for i,c in zip(ids, corners)}

        # ───── Ruler ─────
        if POINTER_ID in ctrs:
            pc = corners[list(ids).index(POINTER_ID)][0]
            O  = ctrs[POINTER_ID]
            u  = ( (pc[1]+pc[2])/2 - (pc[0]+pc[3])/2 )
            n  = np.linalg.norm(u)
            if n > 5:
                u /= n
                # Direction change?
                if prev_dir is not None:
                    if np.dot(u, prev_dir) < cos_dir:     # > DIR_THR_DEG
                        cand_cnt = HOLD_FRAMES            # Force immediate switch
                prev_dir = u.copy()

                ray_len = int(np.hypot(H,W))
                for s,c,w in ((+1,CLR_RAY,2),(-1,CLR_RAY_B,1)):
                    tip = np.clip((O+s*u*ray_len).astype(int), (0,0), (W-1,H-1))
                    cv2.line(frame,O.astype(int),tip,c,w,cv2.LINE_AA)

                # ───── First object in the cone ─────
                best_proj, best_id = 1e9, None
                for oid in OBJ_IDS:
                    if oid not in ctrs: continue
                    v = ctrs[oid] - O
                    proj = np.dot(u, v)
                    if proj <= 0: continue
                    d_perp = np.linalg.norm(v - proj*u)
                    if d_perp / proj < tan_cone and proj < best_proj:
                        best_proj, best_id = proj, oid
                cand_now = best_id

        # Drawing
        if ids is not None:
            for i,c in zip(ids,corners):
                clr = CLR_SEL if i==cur_id else CLR_OBJ
                cv2.polylines(frame,[c.astype(int)],True,clr,2,cv2.LINE_AA)
                cx,cy = ctrs[i].astype(int)
                cv2.putText(frame,str(i),(cx-10,cy+10),FONT,0.7,clr,2,cv2.LINE_AA)

    # ───── Ultra-short hysteresis ─────
    if cand_now is None or cand_now==cur_id:
        cand_id, cand_cnt = None, 0
    else:
        if cand_now == cand_id:
            cand_cnt += 1
            if cand_cnt >= HOLD_FRAMES:
                cur_id = cand_id
                cand_id, cand_cnt = None, 0
        else:
            cand_id, cand_cnt = cand_now, 1

    # ───── Banner ─────
    cv2.rectangle(frame,(0,0),(W,BANNER_H),(0,0,0),-1)
    label = f"Object selected  →  {cur_id if cur_id else '---'}"
    size,_ = cv2.getTextSize(label,FONT,FSCALE,THICK)
    cv2.putText(frame,label,((W-size[0])//2,(BANNER_H+size[1])//2),
                FONT,FSCALE,CLR_SEL if cur_id else (0,0,255),THICK,cv2.LINE_AA)

    cv2.imshow("ArUco Select (reactive)", frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
