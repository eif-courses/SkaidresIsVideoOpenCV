#!/usr/bin/python3

import cv2
import sys

STATIC_THRESHOLD_MSECS = 3000
UI = False
cap = cv2.VideoCapture(sys.argv[1])

if len(sys.argv) > 5:
    if len(sys.argv) > 6:
        STATIC_THRESHOLD_MSECS = int(sys.argv[6])
    (x, y, w, h) = map(int, sys.argv[2:6])

    def crop(frame):
        global x, y, w, h
        # from https://stackoverflow.com/a/40296783
        return frame[y:y+h, x:x+w]
else:
    def crop(frame):
        return frame

frame = None
gray = None
anchor_frame = None
anchor_gray = None
anchor_frame_num = None
anchor_time = None


def msec_to_human_readable(time):
    sec = time / 1000
    return '%d:%02d' % (sec / 60, sec % 60)


while(True):
    ret, frame = cap.read()
    if frame is None:
        break
    frame = crop(frame)

    if UI:
        cv2.imshow('window', frame)
    elif (cap.get(cv2.CAP_PROP_POS_FRAMES) % 2000) == 0:
        time_str = msec_to_human_readable(cap.get(cv2.CAP_PROP_POS_MSEC))
        print("Current time: %s" % time_str)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    def set_anchor():
        global anchor_frame, anchor_gray, anchor_frame_num, anchor_time
        anchor_frame = frame
        anchor_gray = gray
        anchor_frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
        anchor_time = cap.get(cv2.CAP_PROP_POS_MSEC)
        if UI:
            cv2.imshow('anchor', frame)

    if anchor_frame is None:
        set_anchor()

    deltaframe = cv2.absdiff(anchor_gray, gray)
    if UI:
        cv2.imshow('delta', deltaframe)
    threshold = cv2.threshold(deltaframe, 10, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None)
    if UI:
        cv2.imshow('threshold', threshold)

    if threshold.any():
        time = cap.get(cv2.CAP_PROP_POS_MSEC)
        if time - anchor_time > STATIC_THRESHOLD_MSECS:
            time_str = msec_to_human_readable(anchor_time)
            print("Static frame at time %s for %f seconds"
                  % (time_str, (time-anchor_time) / 1000.0))
            if UI:
                cv2.imshow('static', anchor_frame)
            cv2.imwrite('kadras_at_%s.jpg' % time_str.replace(":", ""), anchor_frame)
        set_anchor()

    if UI:
        key = cv2.waitKey(20)
        if key == ord('q'):
            break
        # Move in video
        elif key == ord('z'):
            cap.set(cv2.CAP_PROP_POS_FRAMES,
                    cap.get(cv2.CAP_PROP_POS_FRAMES) - 100)
            anchor_frame = None
        elif key == ord('x'):
            cap.set(cv2.CAP_PROP_POS_FRAMES,
                    cap.get(cv2.CAP_PROP_POS_FRAMES) + 100)
            anchor_frame = None
        # Adjust crop
        elif key == ord('w'):
            y -= 10
            print('y=%d' % y)
        elif key == ord('W'):
            y -= 1
            print('y=%d' % y)
        elif key == ord('a'):
            x -= 10
            print('x=%d' % x)
        elif key == ord('A'):
            x -= 1
            print('x=%d' % x)
        elif key == ord('s'):
            y += 10
            print('y=%d' % y)
        elif key == ord('S'):
            y += 1
            print('y=%d' % y)
        elif key == ord('d'):
            x += 10
            print('x=%d' % x)
        elif key == ord('D'):
            x += 1
            print('x=%d' % x)
        elif key == ord('i'):
            h -= 10
            print('h=%d' % h)
        elif key == ord('I'):
            h -= 1
            print('h=%d' % h)
        elif key == ord('j'):
            w -= 10
            print('w=%d' % w)
        elif key == ord('J'):
            w -= 1
            print('w=%d' % w)
        elif key == ord('k'):
            h += 10
            print('h=%d' % h)
        elif key == ord('K'):
            h += 1
            print('h=%d' % h)
        elif key == ord('l'):
            w += 10
            print('w=%d' % w)
        elif key == ord('L'):
            w += 1
            print('w=%d' % w)
cap.release()
cv2.destroyAllWindows()
