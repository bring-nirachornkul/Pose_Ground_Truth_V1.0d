from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk
import os
import csv
import time
import tkinter.filedialog
from tkinter.messagebox import askquestion
from tkinter import filedialog
import math


file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
data = []

with open(file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    if 'GT_X' not in reader.fieldnames or 'GT_Y' not in reader.fieldnames:
        print("The CSV file does not contain GT_X or GT_Y columns.")
    else:
        for row in reader:
            gt_x = row['GT_X']
            gt_y = row['GT_Y']
            data.append({'GT_X': gt_x, 'GT_Y': gt_y})
            
print(data)


