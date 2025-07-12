import cv2
import face_recognition
import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time

class SimpleAttendance:
    def __init__(self):
        self.known_faces = []
        self.known_names = []
        self.attendance = {}
        
        # Create folder for faces
        os.makedirs("faces", exist_ok=True)
        self.load_faces()
    
    def load_faces(self):
        """Load all face images from 'faces' folder"""
        self.known_faces = []
        self.known_names = []
        
        for filename in os.listdir("faces"):
            if filename.endswith(('.jpg', '.png')):
                name = filename.split('.')[0]
                image = face_recognition.load_image_file(f"faces/{filename}")
                encoding = face_recognition.face_encodings(image)
                
                if encoding:
                    self.known_faces.append(encoding[0])
                    self.known_names.append(name)
                    print(f"✓ Loaded: {name}")
    
    def add_person(self, name, image_path):
        """Add new person"""
        import shutil
        shutil.copy(image_path, f"faces/{name}.jpg")
        self.load_faces()
        print(f"✓ Added: {name}")
    
    def mark_attendance(self, name):
        """Mark attendance"""
        today = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M")
        
        if today not in self.attendance:
            self.attendance[today] = {}
        
        if name not in self.attendance[today]:
            self.attendance[today][name] = time
            self.save_attendance()
            return True
        return False
    
    def save_attendance(self):
        """Save to file"""
        with open("attendance.json", "w") as f:
            json.dump(self.attendance, f, indent=2)
    
    def recognize_faces(self, frame):
        """Recognize faces in frame"""
        # Find faces
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_faces, face_encoding)
            name = "Unknown"
            
            if True in matches:
                match_index = matches.index(True)
                name = self.known_names[match_index]
            
            names.append(name)
        
        return face_locations, names

class SimpleGUI:
    def __init__(self):
        self.attendance = SimpleAttendance()
        self.video_source = None
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure styles
        self.setup_styles()
        
        # Create main frame with padding
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Face Recognition Attendance System", 
                              font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 30))
        
        # Add Person Section
        self.create_add_person_section(main_frame)
        
        # Separator
        separator1 = ttk.Separator(main_frame, orient='horizontal')
        separator1.pack(fill=tk.X, pady=20)
        
        # Attendance Section
        self.create_attendance_section(main_frame)
        
        # Separator
        separator2 = ttk.Separator(main_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=20)
        
        # Status and Display Section
        self.create_status_section(main_frame)
        
        self.update_display()
    
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Green.TButton', background='#27ae60', foreground='white')
        style.configure('Blue.TButton', background='#3498db', foreground='white')
        style.configure('Orange.TButton', background='#e67e22', foreground='white')
        style.configure('Red.TButton', background='#e74c3c', foreground='white')
        
        # Configure frame styles
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
    
    def create_add_person_section(self, parent):
        """Create add person section"""
        # Section frame
        section_frame = ttk.Frame(parent, style='Card.TFrame')
        section_frame.pack(fill=tk.X, pady=10, padx=10, ipady=20)
        
        # Section title
        title_label = tk.Label(section_frame, text="Add New Person", 
                              font=("Arial", 14, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=(10, 15))
        
        # Name input frame
        input_frame = tk.Frame(section_frame, bg='white')
        input_frame.pack(pady=5)
        
        tk.Label(input_frame, text="Name:", font=("Arial", 11), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.name_entry = tk.Entry(input_frame, font=("Arial", 12), width=25, relief='solid', bd=1)
        self.name_entry.pack(side=tk.LEFT)
        
        # Add button
        add_button = ttk.Button(section_frame, text="Select Photo & Add Person", 
                               command=self.add_person, style='Green.TButton')
        add_button.pack(pady=15)
    
    def create_attendance_section(self, parent):
        """Create attendance section"""
        # Section frame
        section_frame = ttk.Frame(parent, style='Card.TFrame')
        section_frame.pack(fill=tk.X, pady=10, padx=10, ipady=20)
        
        # Section title
        title_label = tk.Label(section_frame, text="Take Attendance", 
                              font=("Arial", 14, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=(10, 15))
        
        # Buttons frame
        button_frame = tk.Frame(section_frame, bg='white')
        button_frame.pack(pady=10)
        
        video_button = ttk.Button(button_frame, text="Process Video File", 
                                 command=self.select_video, style='Blue.TButton')
        video_button.pack(side=tk.LEFT, padx=10)
        
        manual_button = ttk.Button(button_frame, text="Manual Attendance", 
                                  command=self.manual_attendance, style='Orange.TButton')
        manual_button.pack(side=tk.LEFT, padx=10)
    
    def create_status_section(self, parent):
        """Create status and display section"""
        # Status frame
        status_frame = ttk.Frame(parent, style='Card.TFrame')
        status_frame.pack(fill=tk.X, pady=10, padx=10, ipady=15)
        
        # Status label
        tk.Label(status_frame, text="System Status", font=("Arial", 12, "bold"), 
                bg='white', fg='#2c3e50').pack(pady=(10, 5))
        
        self.status_label = tk.Label(status_frame, text="Ready", font=("Arial", 10), 
                                    bg='white', fg='#27ae60')
        self.status_label.pack(pady=(0, 10))
        
        # Attendance display frame
        display_frame = ttk.Frame(parent, style='Card.TFrame')
        display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10, ipady=15)
        
        # Attendance title
        attendance_title = tk.Label(display_frame, text="Today's Attendance", 
                                   font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        attendance_title.pack(pady=(10, 5))
        
        # Attendance text with scrollbar
        text_frame = tk.Frame(display_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.attendance_text = tk.Text(text_frame, height=8, width=50, 
                                      font=("Arial", 10), relief='solid', bd=1,
                                      yscrollcommand=scrollbar.set)
        self.attendance_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.attendance_text.yview)
        
        # Refresh button
        refresh_button = ttk.Button(display_frame, text="Refresh Display", 
                                   command=self.update_display, style='Blue.TButton')
        refresh_button.pack(pady=10)
    
    def add_person(self):
        """Add new person"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name!")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.png *.jpeg")]
        )
        
        if file_path:
            try:
                self.attendance.add_person(name, file_path)
                self.name_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Successfully added {name}!")
                self.update_display()
                self.status_label.config(text=f"Added {name} to system", fg='#27ae60')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add person: {str(e)}")
    
    def select_video(self):
        """Select video file for attendance"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        
        if file_path:
            self.process_video(file_path)
    
    def process_video(self, video_path):
        """Process video file for attendance with optimizations"""
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Processing settings
        process_every_n_frames = max(1, int(fps // 5))  # Process 5 frames per second
        frame_count = 0
        processed_frames = 0
        
        # Track marked attendance to avoid duplicates
        marked_today = set()
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.attendance.attendance:
            marked_today = set(self.attendance.attendance[today].keys())
        
        self.status_label.config(text="Processing video - Press 'q' to stop", fg='#e67e22')
        
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Skip frames for performance
            if frame_count % process_every_n_frames != 0:
                continue
            
            processed_frames += 1
            
            # Resize frame for faster processing (25% of original size)
            height, width = frame.shape[:2]
            small_frame = cv2.resize(frame, (width // 4, height // 4))
            
            # Recognize faces on small frame
            face_locations, face_names = self.attendance.recognize_faces(small_frame)
            
            # Scale back up face locations for display
            face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                            for (top, right, bottom, left) in face_locations]
            
            # Draw results and mark attendance
            newly_marked = []
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Determine color based on attendance status
                if name == "Unknown":
                    color = (0, 0, 255)  # Red for unknown
                elif name in marked_today:
                    color = (0, 255, 255)  # Yellow for already marked
                else:
                    color = (0, 255, 0)  # Green for new
                
                # Draw rectangle and name
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Create label with status
                if name != "Unknown" and name in marked_today:
                    label = f"{name} ✓"
                else:
                    label = name
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (left, top - 25), (left + label_size[0], top), color, -1)
                cv2.putText(frame, label, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                # Mark attendance (only once per person)
                if name != "Unknown" and name not in marked_today:
                    if self.attendance.mark_attendance(name):
                        marked_today.add(name)
                        newly_marked.append(name)
                        print(f"✓ Attendance marked for {name}")
            
            # Calculate progress
            progress = (frame_count / total_frames) * 100
            
            # Draw progress and stats on frame
            stats_text = [
                f"Progress: {progress:.1f}%",
                f"Marked Today: {len(marked_today)}",
                f"Frame: {frame_count}/{total_frames}"
            ]
            
            if newly_marked:
                stats_text.append(f"New: {', '.join(newly_marked)}")
            
            # Draw stats background
            y_offset = 30
            for i, text in enumerate(stats_text):
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(frame, (10, y_offset + i * 30 - 20), 
                            (20 + text_size[0], y_offset + i * 30 + 5), (0, 0, 0), -1)
                cv2.putText(frame, text, (15, y_offset + i * 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw progress bar
            bar_width = 400
            bar_height = 20
            bar_x = width - bar_width - 20
            bar_y = 20
            
            # Progress bar background
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
            
            # Progress bar fill
            fill_width = int((progress / 100) * bar_width)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), (0, 255, 0), -1)
            
            # Progress text
            cv2.putText(frame, f"{progress:.1f}%", (bar_x + bar_width // 2 - 30, bar_y + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Video Attendance - Enhanced', frame)
            
            # Update GUI periodically
            if processed_frames % 10 == 0:
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Processing: {progress:.1f}% - {len(marked_today)} marked", fg='#e67e22'))
            
            # Check for quit (faster response)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Calculate processing time and stats
        processing_time = time.time() - start_time
        fps_processed = processed_frames / processing_time if processing_time > 0 else 0
        
        # Show completion summary
        summary = f"""Video Processing Complete!
        
Processing Time: {processing_time:.1f} seconds
Processed Frames: {processed_frames}/{total_frames}
Average FPS: {fps_processed:.1f}
People Marked: {len(marked_today)}
        
Performance: {3 if fps_processed > 5 else 2 if fps_processed > 2 else 1}x faster than real-time"""
        
        messagebox.showinfo("Processing Complete", summary)
        
        # Update status and display
        self.status_label.config(text=f"Processing complete - {len(marked_today)} people marked", fg='#27ae60')
        self.update_display()
    
    def manual_attendance(self):
        """Manual attendance marking"""
        if not self.attendance.known_names:
            messagebox.showwarning("Warning", "No registered faces found!")
            return
        
        # Create selection window
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Manual Attendance")
        selection_window.geometry("400x500")
        selection_window.configure(bg='#f0f0f0')
        selection_window.resizable(False, False)
        
        # Center the window
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        # Main frame
        main_frame = tk.Frame(selection_window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Select Person for Attendance", 
                              font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # List frame
        list_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        listbox = tk.Listbox(list_frame, font=("Arial", 11), height=15,
                            yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with attendance status
        today = datetime.now().strftime("%Y-%m-%d")
        marked_today = set()
        if today in self.attendance.attendance:
            marked_today = set(self.attendance.attendance[today].keys())
        
        for name in sorted(self.attendance.known_names):
            display_name = f"{name} ✓" if name in marked_today else name
            listbox.insert(tk.END, display_name)
        
        def mark_selected():
            selection = listbox.curselection()
            if selection:
                display_name = listbox.get(selection[0])
                name = display_name.replace(" ✓", "")  # Remove checkmark if present
                
                if self.attendance.mark_attendance(name):
                    messagebox.showinfo("Success", f"Attendance marked for {name}!")
                    self.update_display()
                    self.status_label.config(text=f"Marked attendance for {name}", fg='#27ae60')
                else:
                    messagebox.showwarning("Warning", f"{name} already marked today!")
                selection_window.destroy()
            else:
                messagebox.showerror("Error", "Please select a person!")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        mark_button = ttk.Button(button_frame, text="Mark Attendance", 
                               command=mark_selected, style='Green.TButton')
        mark_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=selection_window.destroy, style='Red.TButton')
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def update_display(self):
        """Update attendance display"""
        self.attendance_text.delete(1.0, tk.END)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in self.attendance.attendance:
            self.attendance_text.insert(tk.END, f"Date: {today}\n")
            self.attendance_text.insert(tk.END, "-" * 40 + "\n")
            
            for name, time in self.attendance.attendance[today].items():
                self.attendance_text.insert(tk.END, f"{name:<20} - {time}\n")
                
            self.attendance_text.insert(tk.END, "-" * 40 + "\n")
            self.attendance_text.insert(tk.END, f"Total Present: {len(self.attendance.attendance[today])}\n")
        else:
            self.attendance_text.insert(tk.END, "No attendance recorded for today")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleGUI()
    app.run()