import tkinter as tk
from tkinter import filedialog
import csv

class MyGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.file_path = None
        self.data = []
        self.load_csv_button = tk.Button(self.master, text="Load CSV", command=self.load_csv)
        self.load_csv_button.pack()
        self.data_label = tk.Label(self.master, text="Data will be displayed here")
        self.data_label.pack()


    def print_csv(file_path):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)


    def load_csv(self):
        # Open a file dialog to select the CSV file
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        self.file_path = file_path
        self.print_csv(file_path)  # Call the print_csv function with the file path
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                frame_no = row['frame_number']
                x = int(row['landmark_x'])
                y = int(row['landmark_y'])
                gt_x = int(row['GT_X'])  # Load GT_X value from CSV file
                gt_y = int(row['GT_Y'])  # Load GT_Y value from CSV file
                self.data.append((frame_no, x, y, gt_x, gt_y))  # Add GT_X and GT_Y values to self.data
            self.show_data()

    def show_data(self):
        # Clear the previous contents of the label
        self.data_label.config(text="")
        # Display the contents of self.data in the label
        for item in self.data:
            self.data_label.config(text=self.data_label.cget("text") + str(item) + "\n")

root = tk.Tk()
my_gui = MyGUI(root)
my_gui.pack()
root.mainloop()
