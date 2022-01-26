import csv
import easygui
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go
from scipy.fft import fft, ifft, fftfreq
from scipy import signal

# inputcsv = easygui.fileopenbox('Please select ROIs (csv)')
inputcsv = 'test.csv'

rois = []

start_t = 150

with open(inputcsv) as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        rois.append([int(x) for x in row])

# inputvid = easygui.fileopenbox('Please select video')
inputvid = '/Users/stuartbman/Google Drive/us_emg_shared/recordings- 2021.05.13/- - Recording 13.05.21 active - 2021-05-13 14-24-20.mp4'

color = np.random.randint(0, 255, (200, 3))
feature_params = dict(maxCorners=200,
                      qualityLevel=0.1,
                      minDistance=5,
                      blockSize=5)

for roi in rois:
    cap = cv2.VideoCapture(inputvid)

    Fs = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(Fs * start_t))
    old_frame = None
    ret, frame1 = cap.read()
    frame1 = frame1[roi[1]:roi[3], roi[0]:roi[2]]
    prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255

    mags = np.zeros_like(prvs)
    t_mag = []
    all_mags = []

    i = 0

    while i < 100000:
        i += 1
        ret, frame2 = cap.read()
        try:
            frame2 = frame2[roi[1]:roi[3], roi[0]:roi[2]]
        except:
            break
        next = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        dst = cv2.addWeighted(frame2, 0.5, rgb, 0.5, 0.0)

        mags = mags + mag
        all_mags.append(mag)
        t_mag.append(sum(sum(mag)))

        # cv2.imshow('mywindow', dst)
        k = cv2.waitKey(12) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('opticalfb.png', frame2)
            cv2.imwrite('opticalhsv.png', rgb)
        prvs = next

    cv2.destroyAllWindows()
    cap.release()
    t = list(range(0, len(t_mag)))
    t = [x/60 for x in t]
    fig = go.Figure([go.Scatter(x=t, y=t_mag)])
    fig.show()

    #f, Pxx_den = signal.periodogram(t_mag, Fs)
    #plt.semilogy(f, Pxx_den)
    #plt.xlabel('frequency [Hz]')
    #plt.ylabel('PSD [V**2/Hz]')
    #plt.xlim([0.1, 5])
    #plt.title('{}, {}'.format(roi[0], roi[1]))
    #plt.show()


fig, ax = plt.subplots()

ax.imshow(frame2)
for roi in rois:
    rect = patches.Rectangle(
        (roi[0], roi[1]),
        roi[2] - roi[0],
        roi[3] - roi[1],
        linewidth=5,
        edgecolor='r',
        facecolor='none'
    )
    ax.add_patch(rect)

plt.show()
