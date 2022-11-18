import serial
from serial.tools import list_ports
import time
from PIL import ImageGrab
import numpy as np
from skimage import transform
from sklearn.cluster import KMeans
import threading
import sys
import win32gui, win32process
import wmi

CLUSTERS = 6
DOWNSCALE = 70
FPS_TARGET = 30
FADE_SPEED = 0.05
CLUSTER_RATIO_THRESHOLD = 0.9
WHITEBALANCE_WEIGHTS = np.array([1.0, 0.6, 0.5])  # determined by eye


current_color = np.array([0.0, 0.0, 0.0])
target_color = np.array([0.0, 0.0, 0.0])
resume = True

the_wmi = wmi.WMI()

def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in the_wmi.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe

def get_screen_color():
    global target_color, resume
    while (resume):
        screen = np.array(ImageGrab.grab())
        screen = transform.downscale_local_mean(screen, (DOWNSCALE, DOWNSCALE, 1))
        screen_flat = np.reshape(screen, (screen.shape[0] * screen.shape[1], screen.shape[2]))
        kmeans = KMeans(n_clusters=CLUSTERS).fit(screen_flat)
        cluster_sizes = [sum(kmeans.labels_ == i) for i in range(kmeans.n_clusters)]
        largest = np.argmax(cluster_sizes)
        second_largest = np.argmax(np.delete(cluster_sizes, largest))
        # if cluster_sizes[second_largest] / cluster_sizes[largest] < CLUSTER_RATIO_THRESHOLD:
        #     target_color = kmeans.cluster_centers_[largest, :]
        # else:
            #first and second largest cluster have very similar size; we thus average them
        target_color = (kmeans.cluster_centers_[largest, :] * cluster_sizes[largest] +
                        kmeans.cluster_centers_[second_largest, :] * cluster_sizes[second_largest]) \
                       / (cluster_sizes[largest] + cluster_sizes[second_largest])


def send_to_arduino():
    global current_color, target_color, resum
    ports = list_ports.comports()
    # ports = [p for p in ports if p.description.startswith('Arduino')]

    if len(ports) > 0:
        try:
            devicename = ports[0].device

            ser = serial.Serial(devicename, baudrate=9600, timeout=1)  # open serial port

            while(resume):
                d = (target_color-current_color) * FADE_SPEED
                current_color += d

                send_color = current_color * WHITEBALANCE_WEIGHTS
                send_color_int = [int(x) for x in send_color]
                ser.write(bytearray(send_color_int))
                time.sleep(1/FPS_TARGET)

        finally:
            try:
                ser.write(bytearray([0, 0, 0]))
                ser.close()
                print('Closed port')
            except:
                print("Perhaps another application is connected to the Arduino right now.")

    else:
        print('No Arduino connected. Exiting.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'screen':
            print('Hello, your LEDs are now controlled by the screen content.')
            grab_thread = threading.Thread(target=get_screen_color)
            grab_thread.start()
            send_thread = threading.Thread(target=send_to_arduino)
            send_thread.start()
            input('Press enter to quit.')
            resume = False
        elif sys.argv[1] == 'app':
            print('Hello, your LEDs are now controlled by the currently active app.')
            send_thread = threading.Thread(target=send_to_arduino)
            send_thread.start()
            while True:
                w = win32gui.GetForegroundWindow()
                a = get_app_name(w)
                if a is not None:
                    a = a.lower()
                if 'firefox' in a:
                    c = [255, 150, 0]
                elif 'pycharm' in a:
                    c = [0, 255, 0]
                elif 'zoom' in a:
                    c = [255, 0, 0]
                elif 'zotero' in a or 'acrobat' in a:
                    c = [0, 0, 255]
                elif 'tex' in a :
                    c = [255, 0, 255]
                    # todo: continue
                else:
                    c = [100, 100, 100]
                print(a)
                target_color = np.array(c)
                time.sleep(0.5)
            # grab_thread = threading.Thread(target=get_app_color)
            # grab_thread.start()
            # input('Press enter to quit.')
            # resume = False
        exit(0)
    else:
        send_thread = threading.Thread(target=send_to_arduino)
        send_thread.start()
        while resume:
            colstr = input('enter color (or q to quit)')
            if colstr == 'q':
                resume = False
                exit(0)
            else:
                colors = colstr.split(' ')
                try: 
                    target_color = np.array([float(colors[0]),
                                                float(colors[1]), 
                                                float(colors[2])])
                except:
                    print('Syntax: e.g. "255 0 0" for red')
