#!/usr/bin/env python3
import argparse, sys, time, random
import cv2, numpy as np, mediapipe as mp, PySimpleGUI as sg

# ------------- CLI
cli = argparse.ArgumentParser()
cli.add_argument("--camera", type=int, default=0)
cli.add_argument("--width",  type=int, default=1280)
cli.add_argument("--height", type=int, default=720)
args = cli.parse_args();  W, H = args.width, args.height

# ------------- Camera
cap = cv2.VideoCapture(args.camera)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  W); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
if not cap.isOpened(): sys.exit("Cannot open camera")
grab = lambda: cap.read()[1]

# ------------- MediaPipe
mp_hands, mp_draw = mp.solutions.hands, mp.solutions.drawing_utils
hands = mp_hands.Hands(False, 1, 0, 0.6, 0.5)
def fingers_up(lm):
    p = lm.landmark
    n = int(abs(p[4].x - p[2].x) > .04)
    n += sum(p[t].y < p[q].y for t,q in zip([8,12,16,20],[6,10,14,18]))
    return n
LABELS = {0:"ROCK", 2:"SCISSORS", 5:"PAPER"}

# ------------- Markov 1 amélioré
idx={"ROCK":0,"PAPER":1,"SCISSORS":2}; beats={0:1,1:2,2:0}
count = np.ones((3,3), int)
last = None
def recommend(cur):
    global last, count
    if cur in idx and last in idx:
        count[idx[last], idx[cur]] += 1
    last = cur if cur in idx else last
    if last is None:                     # pas encore assez d’infos
        return random.choice(["ROCK","PAPER","SCISSORS"])
    row = count[idx[last]]
    max_val = row.max()
    best_cols = np.flatnonzero(row == max_val)
    nxt = int(random.choice(best_cols))  # tie‑break aléatoire
    return ["ROCK","PAPER","SCISSORS"][beats[nxt]]

# ------------- GUI
sg.theme("DarkBlue3")
layout=[[sg.Image(key="-IMG-", size=(W,H))],
        [sg.Text("State:"), sg.Text("", key="-STATE-"),
         sg.Text("   Coach:"), sg.Text("", key="-AI-", text_color="yellow")],
        [sg.Button("Quit", button_color=("white","firebrick3"))]]
win = sg.Window("RPS Auto Coach", layout, finalize=True, resizable=True)
win.maximize()

# ------------- FSM
COUNT, SHOW = range(2)
state, t0   = COUNT, time.time()
COUNT_STR   = ["3","2","1"]
label, ai   = "NO HAND", "..."
prev, fps   = time.time(), 0.0

try:
    while True:
        frame = cv2.flip(grab(), 1)
        now   = time.time()

        if state == COUNT:
            n = int(now - t0)
            if n < 3:
                cv2.putText(frame, COUNT_STR[n], (W//2-40, H//2),
                            cv2.FONT_HERSHEY_DUPLEX, 4, (0,215,255), 6)
            else:
                res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if res.multi_hand_landmarks:
                    lm = res.multi_hand_landmarks[0]
                    label = LABELS.get(fingers_up(lm), "UNKNOWN")
                    mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                ai   = recommend(label)
                state, t0 = SHOW, now

        elif state == SHOW:
            cv2.putText(frame, f"Play: {ai}", (W//2-160, H//2),
                        cv2.FONT_HERSHEY_DUPLEX, 2.5, (0,255,0), 5)
            if now - t0 > 2:
                state, t0 = COUNT, now
                label, ai = "NO HAND", "..."

        fps = 0.9*fps + 0.1*(1/(now-prev)); prev = now
        cv2.putText(frame, f"{label}  {fps:4.1f} FPS", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        win["-IMG-"].update(data=cv2.imencode(".png", frame)[1].tobytes())
        win["-STATE-"].update("COUNT" if state==COUNT else "SHOW")
        win["-AI-"].update(ai)

        if win.read(timeout=1)[0] in (sg.WIN_CLOSED, "Quit"):
            break
finally:
    win.close(); hands.close(); cap.release()
