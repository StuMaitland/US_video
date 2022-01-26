import cv2
import csv
import datetime
import sys
import getopt

needle_pos_x = []
needle_pos_y = []
times = []
iX = 0
iY = 0
mouseX = 0
mouseY = 0
drawing = False

rect_coords = []


def main(argv):
    inputfile = False
    outputfile = False
    mode = 'needle'
    help_str = 'video_seeker.py -i <inputfile> -o <outputfile>'

    try:
        opts, args = getopt.getopt(argv, 'hai:o:', ['ifile=', 'ofile='])
    except getopt.GetoptError:
        print(help_str)
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print(help_str)
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg
        elif opt in ('-n', '--needle'):
            mode = 'needle'
        elif opt in ('-a', '--alternation'):
            mode = 'alternation'

    if inputfile:
        cap = cv2.VideoCapture(inputfile)
    else:
        raise FileNotFoundError(help_str)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    font = cv2.FONT_HERSHEY_SIMPLEX

    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = length / fps

    wait = 12
    ind = 0

    def on_change(trackbar_value):
        cap.set(cv2.CAP_PROP_POS_FRAMES, trackbar_value)
        err, img = cap.read()
        cv2.imshow("mywindow", img)
        pass

    def draw_circle(event, x, y, flags, param):
        global mouseX, mouseY, needle_pos_x, needle_pos_y
        if event == cv2.EVENT_LBUTTONDOWN:
            mouseX, mouseY = x, y
            needle_pos_x.append(x)
            needle_pos_y.append(y)
            times.append(cap.get(cv2.CAP_PROP_POS_MSEC))

    def draw_rectangle(event, x, y, flags, param):
        global mouseX, mouseY, iX, iY, drawing, mode, rect_coords

        if event == cv2.EVENT_LBUTTONDOWN:
            if drawing:
                rect_coords.append([iX, iY, mouseX, mouseY])
            else:
                iX, iY = x, y
            drawing = not (drawing)

        elif event == cv2.EVENT_MOUSEMOVE:
            mouseX, mouseY = x, y

    def progress_string(cap):
        frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        t_now = frame / fps
        t_str = str(datetime.timedelta(seconds=t_now)).split('.')[0]

        d_str = str(datetime.timedelta(seconds=duration)).split('.')[0]

        return t_str + ' : ' + d_str

    def draw_shapes(img):
        if mode == 'needle':
            img = cv2.circle(img, (mouseX, mouseY), 15, (255, 0, 0), 5)  # Draw the selected position onscreen
        elif mode == 'alternation':
            for row in rect_coords:
                img = cv2.rectangle(img, (row[0], row[1]), (row[2], row[3]), (0, 255, 0), 5)
            if drawing:
                img = cv2.rectangle(img, (iX, iY), (mouseX, mouseY), (0, 255, 0), 5)
        return img

    cv2.namedWindow('mywindow')
    cv2.createTrackbar('start', 'mywindow', 0, length, on_change)

    if mode == 'needle':
        cv2.setMouseCallback('mywindow', draw_circle)
    elif mode == 'alternation':
        cv2.setMouseCallback('mywindow', draw_rectangle)

    on_change(0)
    dur_str = ''

    start = cv2.getTrackbarPos('start', 'mywindow')

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    while cap.isOpened():

        err, img = cap.read()

        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= length:
            break

        frame = draw_shapes(img)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) % fps == 0:  # Update the time every second
            dur_str = progress_string(cap)

        cv2.putText(frame, dur_str, (50, 100), font, 1, (0, 255, 255), 2, cv2.LINE_4)
        cv2.imshow("mywindow", frame)
        k = cv2.waitKey(wait)
        if k & 0xff == 27:
            break
        elif k & 0xff == 8:  # Delete key
            if mode == 'needle':
                needle_pos_x.pop()
                needle_pos_y.pop()
            elif mode == 'alternation':
                rect_coords.pop()
        elif k & 0xff == 32:  # Pause playback
            i = 0
            while i != 32:
                i = cv2.waitKey(1)
        elif k == ord('f'):  # skip forward
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + int(fps * 5))
        elif k == ord('a'):  # skip backward
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) - int(fps * 5))
        elif k == ord('d'):  # increase video speed
            wait = max(wait - 1, 1)
        elif k == ord('s'):  # reduce video speed
            wait += 1
    cap.release()
    cv2.destroyAllWindows()

    with open(outputfile, mode='w') as csv_file:
        writer = csv.writer(csv_file)
        if mode == 'needle':
            for k, v in enumerate(times):
                writer.writerow([times[k], needle_pos_x[k], needle_pos_y[k]])
        elif mode == 'alternation':
            for item in rect_coords:
                writer.writerow(item)


if __name__ == '__main__':
    main(sys.argv[1:])
