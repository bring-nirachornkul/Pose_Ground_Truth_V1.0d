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


class LandmarkDraw:
    def __init__(self, master):
        self.master = master
        self.master.title("Landmark Draw")
        output_folder = "output"
        self.output_folder = os.path.join(os.getcwd(), output_folder)

        # Create Frames
        self.frame1 = tk.Frame(self.master)
        self.frame1.pack(side=tk.LEFT, padx=10, pady=10)
        self.frame2 = tk.Frame(self.master)
        self.frame2.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a button to load an image
        self.load_image_button = tk.Button(self.frame2, text='Load Image', command=self.load_image)
        self.load_image_button.pack()

        # Set up the canvas
        self.canvas_width = 600
        self.canvas_height = 400
        self.canvas = tk.Canvas(self.frame1, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Initialize variables for landmarks
        self.landmarks = []
        self.data = []
        self.current_landmark = None
        self.current_landmark_name = tk.StringVar()
        self.current_landmark_name.set("No landmark selected")
        # Define a new StringVar to hold the text for the landmark label
        self.landmark_label_text = tk.StringVar()
        self.landmark_label_text.set("No landmark selected")

        self.dot_ids = {}

        # Add a button to load the CSV files
        self.load_button = tk.Button(self.frame2, text='Load CSV', command=self.load_csv)
        self.load_button.pack()

        # Create radio buttons for landmark selection
        self.landmark_names = ['NOSE', 'LEFT_SHOULDER']
        self.radio_buttons = []
        for name in self.landmark_names:
            rb = ttk.Radiobutton(self.frame2, text=name, variable=self.current_landmark_name, value=name)
            rb.pack(anchor=tk.W)
            self.radio_buttons.append(rb)

        # Set up event bindings
        self.canvas.bind("<Button-1>", self.click_event)

        # Label to display the selected landmark
        self.landmark_label = tk.Label(self.frame2, textvariable=self.landmark_label_text)
        self.landmark_label.pack()

        # Save button
        self.save_button = ttk.Button(self.frame2, text="Save", command=self.save_data)
        self.save_button.pack(pady=10)

        # Next picture button
        self.next_button = ttk.Button(self.frame2, text="Next Picture", command=self.next_image)
        self.next_button.pack()

    def load_image(self):
        # Open a file dialog to select an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            # Load the selected image and get its dimensions
            self.img = Image.open(file_path)
            self.img_width, self.img_height = self.img.size

            # Set the canvas dimensions to match the image
            self.canvas.config(width=self.img_width, height=self.img_height)

            # Create a PhotoImage object from the loaded image
            self.photo = ImageTk.PhotoImage(self.img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def load_csv(self):
            # Open a file dialog to select the CSV file
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        self.file_path = file_path
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                frame_no = row['frame_number']
                x = int(row['landmark_x'])
                y = int(row['landmark_y'])
                self.data.append((frame_no, x, y))
            print(self.data)
    def click_event(self, event):
        name = self.current_landmark_name.get()
        # Remove the previous landmark's dot and coordinates if necessary
        if self.current_landmark is not None and name != self.current_landmark and name in self.dot_ids:
            self.remove_landmark(name)
        if name != "No landmark selected":
            self.remove_landmark(name)
            landmark = (event.x, event.y)
            self.landmarks.append(landmark)
            print('self.landmarks = ', self.landmarks)
            dot_id = self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="green", tags=("landmark_dot",))
            self.dot_ids[name] = dot_id
            self.current_landmark = name
            # Update the landmark label with the new name and coordinates
            self.landmark_label_text.set("{}: ({}, {})".format(name, event.x, event.y))


    def remove_landmark(self, name):
        dot_id = self.dot_ids.pop(name, None)
        if dot_id is not None:
            self.canvas.delete(dot_id)
        self.landmarks = [landmark for landmark in self.landmarks if landmark[0] != name]

    def save_data(self):
        # Get the current working directory
        cwd = os.getcwd()

        # Print the current working directory
        print(cwd)
        # Create the output folder if it doesn't exist
        output_folder = "output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        data2 = []
        #Merge MP_model coordinate with Ground Truth coordinate
        for i, landmark in enumerate(self.landmarks):
            key_frame = i+1
            landmark_x, landmark_y = landmark
            data2.append((key_frame, landmark_x, landmark_y))

        merged_data = []

        for i in range(len(self.data)):
            x1 = int(self.data[i][1])
            y1 = int(self.data[i][2])
            x2 = int(data2[i][1])
            y2 = int(data2[i][2])
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            print("distance = ", distance)
            merged_tuple = self.data[i] + data2[i][1:]
            merged_data.append((*merged_tuple, round(distance, 2)))
        print("Merged data", merged_data)
        """
        data_dict = {}
        for key, *values in self.data + data2:
            if key in data_dict:
                data_dict[key] += values
            else:
                data_dict[key] = values

        merged_data = [(key, *data_dict[key]) for key in data_dict.keys()]"""

        # Save the landmarks to a CSV file with timestamp in the filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        csv_filename = os.path.join(self.output_folder, f"{os.path.splitext(os.path.basename(self.file_path))[0]}_{timestamp}.csv")
        with open(csv_filename, "w", newline="") as file:
            writer = csv.writer(file)
            # Add the header row with column names
            writer.writerow(['Landmark', 'MP_X', 'MP_Y', 'GT_X', 'GT_Y', 'Eclidean_Distance'])
            # Write the data rows
            for row in merged_data:
                writer.writerow(row)

        # Combine the original image with the green dots
        img_with_dots = self.img.copy()
        draw = ImageDraw.Draw(img_with_dots)
        for name, dot_id in self.dot_ids.items():
            x0, y0, x1, y1 = self.canvas.coords(dot_id)
            draw.ellipse((x0, y0, x1, y1), fill="green")

        # Save the image with the landmarks drawn on it and timestamp in the filename
        img_filename = os.path.join(self.output_folder, f"{os.path.splitext(self.file_path)[0]}_{timestamp}.jpg")
        img_with_dots.save(img_filename)

    def next_image(self):
        # Open a file dialog to select the next image file
        image_path = filedialog.askopenfilename()
        if image_path:
            # Load the selected image and get its dimensions
            self.img = Image.open(image_path)
            self.img_width, self.img_height = self.img.size

            # Set the canvas dimensions to match the image
            self.canvas.config(width=self.img_width, height=self.img_height)

            # Create a PhotoImage object from the loaded image
            self.photo = ImageTk.PhotoImage(self.img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            # Open a file dialog to select the CSV file for the new image
            csv_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
            


root = tk.Tk()
app = LandmarkDraw(root)
root.mainloop()
