from ast import While

import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:

    _, load = cap.read()
    load = cv2.resize(load, (200, 200), interpolation=cv2.INTER_AREA)
    # kernelSize = 5
    # filtro = cv2.medianBlur(load, kernelSize)

    (R, G, B) = cv2.split(load)
    # R = load.copy()
    # G = load.copy()
    # B = load.copy()

    # R[:, :, 0] = 0
    # R[:, :, 1] = 0

    # G[:, :, 0] = 0
    # G[:, :, 2] = 0

    # B[:, :, 1] = 0
    # B[:, :, 2] = 0

    # R = cv2.cvtColor(R, cv2.COLOR_BGR2GRAY)
    # G = cv2.cvtColor(G, cv2.COLOR_BGR2GRAY)
    # B = cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)

    Hori = np.concatenate((R, G, B), axis=1)
    cv2.imshow("bandas", Hori)

    ret, thresh = cv2.threshold(B, 80, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("Original", load)
    cv2.imshow("B", closing)

    key = cv2.waitKey(1)
    if key == 27:  # Esc, 종료
        break

cap.release()
cv2.destroyAllWindows()
