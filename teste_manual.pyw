import colorsys
import json
import logging
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter.font import Font
from tkinter.simpledialog import askstring

import cv2
import numpy as np
from PIL import Image, ImageTk

try:
    with open("parametros.conf", "r") as file:
        receitas = json.loads(file.read())
        atual = receitas["Atual"]
        receita = receitas[atual]
        receitaAtual = list(receitas.keys())
        receitaAtual.pop(0)
        # string_variable.set(atual)
except BaseException as error:
    logging.error(error)

try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
    medida = cap.read()[1]
    width, height = medida.shape[:2]
except BaseException as err:
    logging.error(err)
    raise

# print(height, width)
ROIDetected = None
resultado = {
    "dataHora": "",
    "area": None,
}
detect = None
dataHoraTeste = time.time()
drawing = False  # true if mouse is pressed
ix, iy = -1, -1
img_roi = ""
clone = ""
positions = {"LH": 0, "LS": 0, "LV": 0, "UH": 0, "US": 0, "UV": 0, "LF": 0, "UF": 0}
# receitas = {}
# receita = {
#     "LH": 13,
#     "LS": 0,
#     "LV": 0,
#     "LF": 0,
#     "UH": 180,
#     "US": 255,
#     "UV": 255,
#     "UF": 100000,
#     "RefPt": [[261, 147], [468, 395]],
#     "ROIRegion": [[[261, 147], [468, 395]]],
# }


def update_scale(ref, pos):
    global positions
    receita[ref] = int(pos)

    positions[ref] = pos


def color_pixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        (r, g, b) = frame[y, x]
        (r, g, b) = (r / 255, g / 255, b / 255)
        (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
        (h, s, v) = (round(179 * h), round(255 * s), round(255 * v))
        receita["LH"] = h
        receita["LS"] = s
        receita["LV"] = v
        s_lh.set(h)
        s_ls.set(s)
        s_lv.set(v)
        cv2.destroyAllWindows()


def color_select():
    cv2.namedWindow("Color_Select")
    cv2.setMouseCallback("Color_Select", color_pixel)
    _, img = cap.read()
    # kernell = np.ones((2, 2), np.uint8)
    # img = cv2.dilate(img, kernell, iterations=2)
    cv2.imshow("Color_Select", img)


def roi_select():

    global ix, iy, drawing, img_roi, clone, receita
    receita["ROIRegion"] = []
    receita["RefPt"] = []

    def draw_rectangle(event, x, y, flags, param):
        global ix, iy, drawing, img_roi, clone, receita

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
            receita["RefPt"] = [(x, y)]
            receita["ROIRegion"].append(receita["RefPt"])

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing is True:
                img_roi = clone.copy()
                cv2.rectangle(img_roi, (ix, iy), (x, y), (0, 255, 0), 3)
                a = x
                b = y
                if a != x | b != y:
                    cv2.rectangle(img_roi, (ix, iy), (x, y), (0, 0, 0), -1)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            receita["RefPt"].append((x, y))
            img_roi = clone.copy()
            cv2.rectangle(img_roi, (ix, iy), (x, y), (0, 255, 0), 2)
            clone = img_roi.copy()

    # load the image, clone it, and setup the mouse callback function
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    for _ in range(10):
        img_roi = cap.read()[1]

    img_roi = np.array(img_roi)
    clone = img_roi.copy()
    clone1 = img_roi.copy()

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", draw_rectangle)
    while True:
        cv2.imshow("image", img_roi)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("r"):
            receita["ROIRegion"] = []
            receita["RefPt"] = []
            img_roi = clone = clone1.copy()

        elif k == ord("q"):
            cv2.destroyAllWindows()
            break

    spinMask.config(to=len(receita["ROIRegion"]) - 1)

    if len(receita["ROIRegion"]) > 0:
        maskx1.set(receita["ROIRegion"][n_mask.get()][0][0])
        maskx2.set(receita["ROIRegion"][n_mask.get()][0][1])
        masky1.set(receita["ROIRegion"][n_mask.get()][1][0])
        masky2.set(receita["ROIRegion"][n_mask.get()][1][1])
    else:
        maskx1.set(0)
        maskx2.set(0)
        masky1.set(0)
        masky2.set(0)


def save_rec():
    global receita, receitas
    receita1 = receita.copy()
    receitas[comboExample.get()] = receita1
    with open("parametros.conf", "w+") as file:
        file.write(json.dumps(receitas))

    if comboExample.get() not in receitaAtual:

        receitaAtual.append(comboExample.get())

        receita = receitas[comboExample.get()]
        s_lh.set(receita["LH"])
        s_ls.set(receita["LS"])
        s_lv.set(receita["LV"])
        s_lf.set(receita["LF"])
        s_uh.set(receita["UH"])
        s_us.set(receita["US"])
        s_uv.set(receita["UV"])
        s_uf.set(receita["UF"])
        if len(receita["ROIRegion"]) > 0:
            maskx1.set(receita["ROIRegion"][n_mask.get()][0][0])
            maskx2.set(receita["ROIRegion"][n_mask.get()][0][1])
            masky1.set(receita["ROIRegion"][n_mask.get()][1][0])
            masky2.set(receita["ROIRegion"][n_mask.get()][1][1])
        else:
            maskx1.set(0)
            maskx2.set(0)
            masky1.set(0)
            masky2.set(0)


def default_rec():
    global receita, receitas
    with open("parametros.conf", "w+") as file:

        receitas["Atual"] = comboExample.get()

        file.write(json.dumps(receitas))


def select_receita():
    global receita, receitas
    receita = receitas[comboExample.get()]
    s_lh.set(receita["LH"])
    s_ls.set(receita["LS"])
    s_lv.set(receita["LV"])
    s_lf.set(receita["LF"])
    s_uh.set(receita["UH"])
    s_us.set(receita["US"])
    s_uv.set(receita["UV"])
    s_uf.set(receita["UF"])
    if len(receita["ROIRegion"]) > 0:
        maskx1.set(receita["ROIRegion"][n_mask.get()][0][0])
        maskx2.set(receita["ROIRegion"][n_mask.get()][0][1])
        masky1.set(receita["ROIRegion"][n_mask.get()][1][0])
        masky2.set(receita["ROIRegion"][n_mask.get()][1][1])
    else:
        maskx1.set(0)
        maskx2.set(0)
        masky1.set(0)
        masky2.set(0)


def novo_rec():
    global receita, receitas
    newReceita = askstring("Input", "Digite nome da receita")
    if newReceita is not None and newReceita != "Atual":
        receita1 = {
            "LH": 0,
            "LS": 0,
            "LV": 0,
            "LF": 0,
            "UH": 180,
            "US": 255,
            "UV": 255,
            "UF": 10000,
            "RefPt": [],
            "ROIRegion": [],
        }
        with open("parametros.conf", "w+") as file:
            receitas[newReceita] = receita1
            file.write(json.dumps(receitas))
        receitaAtual.append(newReceita)
        receita = receitas[newReceita]
        s_lh.set(receita["LH"])
        s_ls.set(receita["LS"])
        s_lv.set(receita["LV"])
        s_uh.set(receita["UH"])
        s_us.set(receita["US"])
        s_uv.set(receita["UV"])
        if len(receita["ROIRegion"]) > 0:
            maskx1.set(receita["ROIRegion"][n_mask.get()][0][0])
            maskx2.set(receita["ROIRegion"][n_mask.get()][0][1])
            masky1.set(receita["ROIRegion"][n_mask.get()][1][0])
            masky2.set(receita["ROIRegion"][n_mask.get()][1][1])
        else:
            maskx1.set(0)
            maskx2.set(0)
            masky1.set(0)
            masky2.set(0)

        string_variable.set(newReceita)


def del_rec():
    global receita, receitas
    if len(receitas) > 2 and comboExample.get() != "Default" and comboExample.get() != "Atual":
        if comboExample.get() == receitas["Atual"]:
            receitas["Atual"] = "Default"
        with open("parametros.conf", "w+") as file:
            del receitas[comboExample.get()]
            file.write(json.dumps(receitas))
        receitaAtual.remove(comboExample.get())

        receita = receitas[receitaAtual[-1]]
        s_lh.set(receita["LH"])
        s_ls.set(receita["LS"])
        s_lv.set(receita["LV"])
        s_uh.set(receita["UH"])
        s_us.set(receita["US"])
        s_uv.set(receita["UV"])
        string_variable.set(receitaAtual[-1])


def ajus_mask(x, v1, v2):
    receita["ROIRegion"][n_mask.get()][x] = [v1, v2]


def atualiza_mask():
    maskx1.set(receita["ROIRegion"][n_mask.get()][0][0])
    maskx2.set(receita["ROIRegion"][n_mask.get()][0][1])
    masky1.set(receita["ROIRegion"][n_mask.get()][1][0])
    masky2.set(receita["ROIRegion"][n_mask.get()][1][1])


root = tk.Tk()
root.title("Teste manual")
root.configure(bg="black")
froot = tk.Frame(root, borderwidth=0, highlightthickness=0)
froot.grid(row=0, column=0, rowspan=2)
fconfig = tk.Frame(root)
fconfig.grid(row=0, column=1, sticky=tk.N, padx=10, pady=10)
fconfig_mask = tk.Frame(root)
fconfig_mask.grid(row=1, column=1, sticky=tk.N, padx=10, pady=10)
f1 = tk.LabelFrame(froot, width=width, height=height, bg="black", borderwidth=0, highlightthickness=0)
f1.grid(row=0, column=0)
L1 = tk.Label(f1)
L1.grid(row=0, column=0)

s_lh = tk.Scale(
    fconfig,
    from_=0,
    to=180,
    length=200,
    orient=tk.HORIZONTAL,
    label="MIN HUE",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("LH", pos),
)
s_lh.set(receita["LH"])
s_lh.grid(row=3, column=0)

s_uh = tk.Scale(
    fconfig,
    from_=0,
    to=180,
    length=200,
    orient=tk.HORIZONTAL,
    label="MAX HUE",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("UH", pos),
)
s_uh.set(receita["UH"])
s_uh.grid(row=3, column=1)
s_ls = tk.Scale(
    fconfig,
    from_=0,
    to=255,
    length=200,
    orient=tk.HORIZONTAL,
    label="MIN SATURATION",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("LS", pos),
)
s_ls.set(receita["LS"])
s_ls.grid(row=4, column=0)
s_us = tk.Scale(
    fconfig,
    from_=0,
    to=255,
    length=200,
    orient=tk.HORIZONTAL,
    label="MAX SATURATION",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("US", pos),
)
s_us.set(receita["US"])
s_us.grid(row=4, column=1)
s_lv = tk.Scale(
    fconfig,
    from_=0,
    to=255,
    length=200,
    orient=tk.HORIZONTAL,
    label="MIN VALUE",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("LV", pos),
)
s_lv.set(receita["LV"])
s_lv.grid(row=5, column=0)
s_uv = tk.Scale(
    fconfig,
    from_=0,
    to=255,
    length=200,
    orient=tk.HORIZONTAL,
    label="MAX VALUE",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("UV", pos),
)
s_uv.set(receita["UV"])
s_uv.grid(row=5, column=1)
s_lf = tk.Scale(
    fconfig,
    from_=0,
    to=10000,
    length=200,
    orient=tk.HORIZONTAL,
    label="MIN FILL",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("LF", pos),
)
s_lf.set(receita["LF"])
s_lf.grid(row=6, column=0)
s_uf = tk.Scale(
    fconfig,
    from_=0,
    to=10000,
    length=200,
    orient=tk.HORIZONTAL,
    label="MAX FILL",
    sliderlength=10,
    activebackground="black",
    command=lambda pos: update_scale("UF", pos),
)
s_uf.set(receita["UF"])
s_uf.grid(row=6, column=1)

b_save = tk.Button(fconfig, text="Salvar", command=save_rec)
b_save.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

b_novo = tk.Button(fconfig, text="Nova", command=novo_rec)
b_novo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.E)

b_default = tk.Button(fconfig, text="Default", command=default_rec)
b_default.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

b_del = tk.Button(fconfig, text="Deletar", command=del_rec)
b_del.grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)

b_color = tk.Button(fconfig, text="Select Cor", command=color_select)
b_color.grid(row=2, column=0, padx=10, pady=10, sticky=tk.EW)

b_roi = tk.Button(fconfig, text="Criar Mask", command=roi_select)
b_roi.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)

string_variable = tk.StringVar(root, receitas["Atual"])
comboExample = ttk.Spinbox(
    fconfig,
    width=8,
    values=receitaAtual,
    command=select_receita,
    textvariable=string_variable,
    font=Font(family="Helvetica", size=18, weight="bold"),
)
comboExample.grid(row=0, column=0, rowspan=2, sticky=tk.E)

n_mask = tk.IntVar(root, 0)
spinMask = ttk.Spinbox(
    fconfig_mask,
    from_=0,
    to=len(receita["ROIRegion"]) - 1 if len(receita["ROIRegion"]) > 0 else 0,
    width=8,
    textvariable=n_mask,
    font=Font(family="Helvetica", size=18, weight="bold"),
    command=atualiza_mask,
)
spinMask.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

maskx1 = tk.IntVar(root, receita["ROIRegion"][0][0][0] if len(receita["ROIRegion"]) >= 1 else 0)
x1mask = tk.Spinbox(
    fconfig_mask,
    from_=0,
    to=width,
    width=10,
    textvariable=maskx1,
    command=lambda m=0: ajus_mask(0, maskx1.get(), maskx2.get()),
)
x1mask.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

masky1 = tk.IntVar(root, receita["ROIRegion"][0][1][0] if len(receita["ROIRegion"]) >= 1 else 0)
y1mask = tk.Spinbox(
    fconfig_mask,
    width=10,
    from_=0,
    to=height,
    textvariable=masky1,
    command=lambda m=0: ajus_mask(1, masky1.get(), masky2.get()),
)
y1mask.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

maskx2 = tk.IntVar(root, receita["ROIRegion"][0][0][1] if len(receita["ROIRegion"]) >= 1 else 0)
x2mask = tk.Spinbox(
    fconfig_mask,
    width=10,
    from_=0,
    to=width,
    textvariable=maskx2,
    command=lambda m=0: ajus_mask(0, maskx1.get(), maskx2.get()),
)
x2mask.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

masky2 = tk.IntVar(root, receita["ROIRegion"][0][1][1] if len(receita["ROIRegion"]) >= 1 else 0)
y2mask = tk.Spinbox(
    fconfig_mask,
    width=10,
    from_=0,
    to=height,
    textvariable=masky2,
    command=lambda m=0: ajus_mask(1, masky1.get(), masky2.get()),
)
y2mask.grid(row=1, column=3, padx=10, pady=10, sticky=tk.W)

w = tk.Label(fconfig, text="Receita", height=3, fg="navyblue", font="50")
w.grid(row=0, column=0, rowspan=2, sticky=tk.W)


font = cv2.FONT_HERSHEY_COMPLEX


def fechar():
    cap.release()
    cv2.destroyAllWindows()


root.protocol("WM_DELETE_WINDOW", fechar)
try:
    while True:
        ret, frame = cap.read()
        if ret is not True:
            break

        l_h = receita["LH"]
        l_s = receita["LS"]
        l_v = receita["LV"]
        l_f = receita["LF"]
        u_h = receita["UH"]
        u_s = receita["US"]
        u_v = receita["UV"]
        u_f = receita["UF"]

        for region in range(len(receita["ROIRegion"])):
            cv2.putText(
                frame,
                f"Mask:{region}",
                (receita["ROIRegion"][region][0][0], receita["ROIRegion"][region][0][1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 0),
                1,
            )
            cv2.rectangle(frame, receita["ROIRegion"][region][0], receita["ROIRegion"][region][1], (200, 200, 0), 2)
            roi = frame[
                receita["ROIRegion"][region][0][1] + 1 : receita["ROIRegion"][region][1][1] - 1,
                receita["ROIRegion"][region][0][0] + 1 : receita["ROIRegion"][region][1][0] - 1,
            ]
            # roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            blurred_frame = cv2.GaussianBlur(roi, (3, 3), 0)
            hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

            lower = np.array([l_h, l_s, l_v])
            upper = np.array([u_h, u_s, u_v])

            mask = cv2.inRange(hsv, lower, upper)
            # kernel = np.ones((7, 7), np.uint8)
            FrameThresh = cv2.dilate(mask, None, iterations=2)
            # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            # mask = cv2.erode(mask, kernel)
            # cv2.imshow("mask", mask)
            contours, _ = cv2.findContours(FrameThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            for cnt in contours:
                area = cv2.contourArea(cnt)

                if area > l_f and area < u_f:
                    cv2.drawContours(roi, [cnt], -1, (0, 255, 255), 3)
                    if ROIDetected != region:
                        ROIDetected = region
                        # if region != 0 and new_teste is True:
                        #     resultado = {
                        #         "dataHora": datetime.now().replace(microsecond=0).isoformat().replace("T", " "),
                        #         "area": region,
                        #     }
                        #     print(resultado)
                        #     text_result = resultado["dataHora"]
                        #     new_teste = False
                        if region == 0:
                            text_result = ""
                            detect = ROIDetected
                            dataHoraTeste = time.time()

        # print(ROIDetected, detect)
        if ROIDetected is not None and ROIDetected != 0 and detect == 0:
            testeatual = time.time()
            deltaTeste = round(testeatual - dataHoraTeste, 2)
            if deltaTeste > 1 and deltaTeste < 20:
                resultado = {
                    "dataHora": datetime.now().replace(microsecond=0).isoformat().replace("T", " "),
                    "area": ROIDetected,
                }
                print(resultado, deltaTeste)
                detect = ROIDetected
            else:
                detect = None

        # if ROIDetected == 0:
        #     text_result = ""
        #     detect = ROIDetected
        # dataHoraTeste = time.time()
        if resultado["area"] == 1:
            cv2.putText(
                frame,
                f"{resultado['dataHora']} OK",
                (2, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
        if resultado["area"] == 2:
            cv2.putText(
                frame,
                f"{resultado['dataHora']} NOK",
                (2, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(img))
        L1["image"] = img
        s_uh["from_"] = positions["LH"]
        s_us["from_"] = positions["LS"]
        s_uv["from_"] = positions["LV"]
        s_uf["from_"] = positions["LF"]
        comboExample["value"] = receitaAtual
        cv2.waitKey(1)
        root.update()
except BaseException as error:
    logging.error(error)
    raise
