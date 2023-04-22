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
    # Create a class-level variable to store the current image's landmarks and current_landmark variable
    current_image_data = {}
    def __init__(self, root, current_image_index, initial_landmarks=None):

        self.root = root
        self.current_image_path = ""
        self.file_path = ""
        self.current_image_index = current_image_index  # Set the current_image_index attribute
        self.current_image_name = tk.StringVar()  # create a StringVar to hold the image name
        self.current_image_name.set("No image loaded")  # set its initial value

        #save checked point
        self.data_saved = False

        # Create Frames
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(side=tk.LEFT, padx=0, pady=10)
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create a button to load an image
        self.load_image_button = tk.Button(self.frame2, text='Load Image', command=self.load_image)
        self.load_image_button.pack()

        # Set up the canvas
        self.canvas_width = 600
        self.canvas_height = 400
        self.canvas = tk.Canvas(self.frame1, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)


        self.landmark_dict = {}
        self.canvas.bind("<Button-1>", self.click_event)


        # Initialize variables for landmarks
        self.landmarks = initial_landmarks or {}
        self.data = []
        self.current_landmark = None
        self.current_landmark_name = tk.StringVar()
        self.current_landmark_name.set("No landmark selected")
        self.landmark_label_text = tk.StringVar()
        self.landmark_label_text.set("No landmark selected")

        self.dot_ids = {}

        # Add a button to load the CSV files
        self.load_button = tk.Button(self.frame2, text='Load CSV', command=self.load_csv)
        self.load_button.pack()

        # Create radio buttons for landmark selection
        #self.landmark_names = ['NOSE', 'LEFT_SHOULDER']
        self.landmark_names = ['NOSE', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 
                               'RIGHT_ELBOW', 'LEFT_WRIST', 'RIGHT_WRIST','LEFT_HIP', 
                               'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE']
        self.radio_buttons = []
        for name in self.landmark_names:
            rb = ttk.Radiobutton(self.frame2, text=name, variable=self.current_landmark_name, value=name)
            rb.pack(anchor=tk.W)
            self.radio_buttons.append(rb)



        # Label to display the selected landmark
        self.landmark_label = tk.Label(self.frame2, textvariable=self.landmark_label_text)
        self.landmark_label.pack()

        # Save button
        self.save_button = ttk.Button(self.frame2, text="Save", command=self.save_data)
        self.save_button.pack(pady=10)

        # Next picture button
        self.next_button = ttk.Button(self.frame2, text="Next Picture", command=self.new_image)
        self.next_button.pack()

        self.image_label = tk.Label(self.frame2, textvariable=self.current_image_name)
        self.image_label.pack()            
        
        #self.header = tk.Label(root, textvariable=self.current_image_name, font=("Helvetica", 16))  # add the label to display the image name
        #self.header.pack(side=tk.TOP, pady=10)  # pack it in the top of the root window


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


            # Check if there is saved data for the current image and set the landmarks and current_landmark accordingly
            if file_path in self.current_image_data:
                self.landmarks = self.current_image_data[file_path]['landmarks']
                self.current_landmark = self.current_image_data[file_path]['current_landmark']

            # Set the current image path
            self.current_image_path = file_path

            # update the current image name
            self.current_image_name.set(os.path.basename(self.current_image_path))

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
            print("Load_csv : self.data = ", self.data)

    def click_event(self, event):
        name = self.current_landmark_name.get()

        if name != "No landmark selected":
            # Save coordinates.
            landmark = {"x": event.x, "y": event.y}
            self.landmarks[name] = landmark

            # Delete the old dot if it exists.
            if name in self.dot_ids:
                self.canvas.delete(self.dot_ids[name])

            # Draw a new dot and save its ID.
            dot_id = self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="green", tags=("landmark_dot",))
            self.dot_ids[name] = dot_id
            #print(dot_id)

            self.current_landmark = name
            self.landmark_label_text.set("{}: ({}, {})".format(name, event.x, event.y))

    def draw_loaded_landmarks(self):
        for name, landmark in self.landmarks.items():
            x, y = landmark['x'], landmark['y']
            dot_id = self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="green", tags=("landmark_dot",))
            self.dot_ids[name] = dot_id
 
    def save_data(self):
        # Get the current working directory
        cwd = os.getcwd()
        self.data_saved = True

        # Save the landmarks and current_landmark variable for the current image
        self.current_image_data[self.current_image_path] = {'landmarks': self.landmarks, 'current_landmark': self.current_landmark}

        # Create the output folder if it doesn't exist
        self.output_folder = "output"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.merged_data = {}
        print("save_data : self.data = ", self.data)

        # Merge MP_model coordinate with Ground Truth coordinate
        for i, (key, landmark) in enumerate(self.landmarks.items()):
            print("i = ", i)
            print("landmark = ", landmark)
            x1, y1 = int(self.data[i][1]), int(self.data[i][2])
            x2, y2 = int(landmark['x']), int(landmark['y'])
            distance = round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2)
            self.merged_data[key] = {
                'MP_model_coordinate': (x1, y1),
                'Ground_Truth_coordinate': (x2, y2),
                'distance': distance
            }
            #print(f"{i}x1 = {x1}")
            #print(f"{i}x2 = {x2}")
        
        print("Merged data", self.merged_data)

        # Save the landmarks to a CSV file with timestamp in the filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        csv_filename = os.path.join(self.output_folder, f"{os.path.splitext(os.path.basename(self.file_path))[0]}_{timestamp}.csv")
        with open(csv_filename, "w", newline="") as file:
            writer = csv.writer(file)
            # Add the header row with column names
            writer.writerow(['Landmark', 'MP_X', 'MP_Y', 'GT_X', 'GT_Y', 'Eclidean_Distance'])
            # Write the data rows
            for key, value in self.merged_data.items():
                row = [key, value['MP_model_coordinate'][0], value['MP_model_coordinate'][1], 
                    value['Ground_Truth_coordinate'][0], value['Ground_Truth_coordinate'][1], value['distance']]
                writer.writerow(row)

        # Combine the original image with the green dots
        img_with_dots = self.img.copy()
        draw = ImageDraw.Draw(img_with_dots)
        for name, dot_id in self.dot_ids.items():
            x0, y0, x1, y1 = self.canvas.coords(dot_id)
            draw.ellipse((x0, y0, x1, y1), fill="green")

        # Save the image with the landmarks drawn on it and timestamp in the filename
        img_filename = os.path.join(self.output_folder, f"{os.path.splitext(os.path.basename(self.file_path))[0]}_{timestamp}.jpg")
        img_with_dots.save(img_filename)

    def new_image(self):
        if self.data_saved:
            pass
        else:
            print("Data has not been saved yet. Saving data...")
            self.save_data()    
        # Forward the current landmarks to the next image
        next_image_index = self.current_image_index + 1

        # You can add logic here to determine the next image path if you have a list of images or a naming pattern
        next_image_path = "path/to/next/image"

        # Create a new instance of LandmarkDraw for the next image with the current landmarks
        next_landmark_draw = LandmarkDraw(self.root, next_image_index, self.landmarks)

        # Load the next image
        next_landmark_draw.current_image_path = next_image_path
        next_landmark_draw.load_image()

        # Draw the landmarks from the previous image
        next_landmark_draw.draw_loaded_landmarks()


        # Hide the current frame and show the next frame
        self.frame1.pack_forget()
        self.frame2.pack_forget()
        next_landmark_draw.frame1.pack(side=tk.LEFT, padx=0, pady=10)
        next_landmark_draw.frame2.pack(side=tk.RIGHT, padx=10, pady=10)

root = tk.Tk()
app = LandmarkDraw(root, 0)
root.mainloop()
