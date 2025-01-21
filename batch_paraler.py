import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import re
from pathlib import Path
import threading
from queue import Queue
import concurrent.futures
import time

import multiprocessing

class FFmpegBatchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Batch Folder Processor")
        self.root.geometry("800x600")
        
        # Variables to store paths
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.matched_files = []
        self.processing_queue = Queue()
        self.is_processing = False
        
        # For tracking progress
        self.completed_files = 0
        self.total_files = 0
       
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input folder selection
        ttk.Label(main_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output folder selection
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # List of files to be processed
        ttk.Label(main_frame, text="Files to be processed:").grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Create text widget for file list
        self.file_list = tk.Text(main_frame, height=20, width=80)
        self.file_list.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Scrollbar for file list
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.file_list.yview)
        scrollbar.grid(row=3, column=3, sticky="ns")
        self.file_list.configure(yscrollcommand=scrollbar.set)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=600, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=5, column=0, columnspan=3)
        
        # Process button
        ttk.Button(main_frame, text="Process Files", command=self.process_files).grid(row=6, column=0, columnspan=3, pady=20)
    
    
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            self.find_matching_files()
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            
            
        
    def find_matching_files(self):
        """Optimized file matching using sets and generators"""
        self.matched_files = []
        self.file_list.delete(1.0, tk.END)
        
        if not self.input_folder.get():
            return
            
        folder_path = self.input_folder.get()
        
        # Use set for faster lookups
        files = set(os.listdir(folder_path))
        pattern = r'(\d{4}-\d{2}-\d{2} - Lecture \d+.*?)_(audio|video)\.m4s'
        
        # Process files in batches using generator
        def find_matches():
            for file in files:
                match = re.match(pattern, file)
                if match:
                    yield match.group(1), match.group(2), file

        # Group matches efficiently
        lectures = {}
        for base_name, file_type, file in find_matches():
            if base_name not in lectures:
                lectures[base_name] = {'audio': None, 'video': None}
            lectures[base_name][file_type] = file
        
        # Find complete pairs
        self.matched_files = [
            {
                'audio': files['audio'],
                'video': files['video'],
                'output': f"{base_name}.mp4"
            }
            for base_name, files in lectures.items()
            if files['audio'] and files['video']
        ]
        
        self.update_file_list()

    def update_file_list(self):
        """Update GUI with matched files"""
        self.file_list.delete(1.0, tk.END)
        for pair in self.matched_files:
            self.file_list.insert(tk.END, 
                f"Found matching pair:\n"
                f"  Video: {pair['video']}\n"
                f"  Audio: {pair['audio']}\n"
                f"  Output: {pair['output']}\n\n"
            )
        self.status_label.config(text=f"Found {len(self.matched_files)} matching pairs")

    def process_single_file(self, pair):
        """Process a single file pair with timing"""
        start_time = time.time()
        try:
            video_path = os.path.join(self.input_folder.get(), pair['video'])
            audio_path = os.path.join(self.input_folder.get(), pair['audio'])
            output_path = os.path.join(self.output_folder.get(), pair['output'])
            
            command = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream without re-encoding
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-y',
                output_path
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Non-blocking read of output
            while True:
                # Only read stderr as we need error messages
                _, stderr = process.communicate()
                if process.poll() is not None:
                    break
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {stderr}")
                
            processing_time = time.time() - start_time
            print(f"Processed {pair['output']} in {processing_time:.2f} seconds")
            return True
        except Exception as e:
            return str(e)

    def update_progress(self):
        """Update progress bar and status"""
        if self.is_processing:
            self.progress['value'] = self.completed_files
            self.status_label.config(
                text=f"Processing: {self.completed_files}/{self.total_files} files completed"
            )
            self.root.after(100, self.update_progress)

    def process_files(self):
        """Process files using thread pool"""
        if not self.matched_files or not self.output_folder.get():
            messagebox.showerror("Error", "No files to process or no output folder selected")
            return
            
        self.is_processing = True
        self.completed_files = 0
        self.total_files = len(self.matched_files)
        self.progress['maximum'] = self.total_files
        
        # Calculate optimal number of workers
        cpu_count = multiprocessing.cpu_count()
        max_workers = min(cpu_count * 2, len(self.matched_files))
        
        def process_thread():
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Create a dictionary to track futures
                future_to_file = {
                    executor.submit(self.process_single_file, pair): pair['output']
                    for pair in self.matched_files
                }
                
                # Process completed futures
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    self.completed_files += 1
                    try:
                        result = future.result()
                        if isinstance(result, str):  # Error occurred
                            messagebox.showerror("Error", f"Error processing {filename}: {result}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error processing {filename}: {str(e)}")
                
                self.is_processing = False
                self.root.after(0, lambda: self.status_label.config(text="Processing complete!"))
                messagebox.showinfo("Success", "All files have been processed!")
        
        # Start processing thread and progress updates
        threading.Thread(target=process_thread, daemon=True).start()
        self.update_progress()


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    root = tk.Tk()
    
    if not check_ffmpeg():
        messagebox.showerror("Error", "FFmpeg not found. Please install FFmpeg and add it to your system PATH.")
        root.destroy()
    else:
        app = FFmpegBatchGUI(root)
        root.mainloop()
        