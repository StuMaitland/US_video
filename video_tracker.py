import cv2
import easygui

#v_file = easygui.fileopenbox('Please select video file')

cap = cv2.VideoCapture('/Users/stuartbman/Google Drive/us_emg_shared/recordings- 2021.05.13/- - Recording 13.05.21 active - 2021-05-13 14-24-20.mp4')
wait = 16


while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)

    key = cv2.waitKey(wait)
    if key == ord('q'):
        break
    elif key == ord('d'):  # increase playback speed
        wait = max(wait-1, 1)
    elif key == ord('s'):  # decrease playback speed
        wait = wait+1


cap.release()
cv2.destroyAllWindows()

