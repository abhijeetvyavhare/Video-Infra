import tkinter as tk
from tkinter import filedialog
import cv2
import json
from PIL import Image, ImageTk, ImageDraw

class ROIApp:
    def __init__(self, canvas):
        self.canvas = canvas
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.roi_shape = None
        self.rois = []

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y

    def on_mouse_drag(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.update_roi()

    def on_button_release(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.create_roi()

    def update_roi(self):
        if self.roi_shape:
            self.canvas.delete(self.roi_shape)
        self.roi_shape = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red")

    def create_roi(self):
        roi_coords = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.rois.append(roi_coords)
        self.canvas.create_rectangle(*roi_coords, outline="blue")

    def clear_rois(self):
        self.canvas.delete("all")
        self.rois = []

    def save_rois_to_json(self, file_path):
        if self.rois:
            data = {
                "rois": self.rois
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            print("RoIs saved successfully.")
        else:
            print("No RoIs to save.")

    def load_rois_from_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.rois = data["rois"]
                for roi in self.rois:
                    self.canvas.create_rectangle(*roi, outline="blue")
            print("RoIs loaded successfully.")
        except FileNotFoundError:
            print("RoI settings file not found.")
        except json.JSONDecodeError:
            print("Invalid JSON format in the RoI settings file.")

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("App")

        self.video_btn = tk.Button(root, text="Video", command=self.open_video)
        self.image_btn = tk.Button(root, text="Image", command=self.open_image)
        self.camera_btn = tk.Button(root, text="Camera", command=self.open_camera)
        self.save_roi_btn = tk.Button(root, text="Save ROI", command=self.save_roi)
        self.load_roi_btn = tk.Button(root, text="Load ROI", command=self.load_roi)
        self.clear_roi_btn = tk.Button(root, text="Clear ROI", command=self.clear_roi)
        self.exit_btn = tk.Button(root, text="Exit", command=root.quit)

        self.video_btn.pack(pady=10)
        self.image_btn.pack(pady=10)
        self.camera_btn.pack(pady=10)
        self.save_roi_btn.pack(pady=10)
        self.load_roi_btn.pack(pady=10)
        self.clear_roi_btn.pack(pady=10)
        self.exit_btn.pack(pady=10)

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        # Create ROIApp instance and pass the canvas reference
        self.roi_app = ROIApp(self.canvas)

    def open_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        if file_path:
            self.roi_app.clear_rois()
            self.process_video(file_path)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.roi_app.clear_rois()
            self.process_image(file_path)

    def open_camera(self):
        self.roi_app.clear_rois()
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                if self.roi_app.roi_shape:
                    cv2.rectangle(frame, (self.roi_app.start_x, self.roi_app.start_y), 
                                  (self.roi_app.end_x, self.roi_app.end_y), (0, 255, 0), 2)

                cv2.imshow("Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def save_roi(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.roi_app.save_rois_to_json(file_path)

    def load_roi(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.roi_app.clear_rois()
            self.roi_app.load_rois_from_json(file_path)

    def clear_roi(self):
        self.roi_app.clear_rois()

    def process_video(self, file_path):
        cap = cv2.VideoCapture(file_path)
        while True:
            ret, frame = cap.read()

            if ret:
                if self.roi_app.roi_shape:
                    cv2.rectangle(frame, (self.roi_app.start_x, self.roi_app.start_y),
                                  (self.roi_app.end_x, self.roi_app.end_y), (0, 255, 0), 2)

                cv2.imshow("Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_image(self, file_path):
        img = Image.open(file_path)

        if self.roi_app.roi_shape:
            img_draw = ImageDraw.Draw(img)
            img_draw.rectangle([self.roi_app.start_x, self.roi_app.start_y, 
                                self.roi_app.end_x, self.roi_app.end_y], outline="red")

        img.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
