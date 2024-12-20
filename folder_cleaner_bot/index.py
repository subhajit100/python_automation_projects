import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define file extensions for each category (add more if required)
FILE_TYPES = {
    "Videos": [".mp4", ".avi", ".mov", ".mkv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Docs": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
}

def organizeFiles(dirPath):
    try:
        # return if given directory path doesn't exist
        if not os.path.exists(dirPath):
            print(f'The given director: {dirPath} does not exist')
            return
        
        # Create subfolders for categories if they don't exist
        for folder in FILE_TYPES.keys():
            folder_path = os.path.join(dirPath, folder)
            os.makedirs(folder_path, exist_ok=True)

        # Traverse files from root directory and move to specific folders based on extension
        for file in os.listdir(dirPath):
            filePath = os.path.join(dirPath, file)
            if os.path.isdir(filePath) or file in FILE_TYPES.keys():
                continue

            # check file extension an move to respective folder
            fileExtension = os.path.splitext(file)[1].lower()
            for folder, extensions in FILE_TYPES.items():
                if fileExtension in extensions:
                    targetPath = os.path.join(dirPath, folder, file)
                    shutil.move(filePath, targetPath)
                    print(f'Moved the file {file} to {folder} folder')
                    break
            else:
                print(f'File {file} does not match any category and hence not moved')        

    except Exception as e:
        print(f'Some error occurred: {e}');  


class DirectoryHandler(FileSystemEventHandler):
    def __init__(self, directory):
        self.directory = directory

    def on_modified(self, event):
        if not event.is_directory:
            organizeFiles(self.directory)

    def on_created(self, event):
        if not event.is_directory:
            organizeFiles(self.directory)

# this method will be running till you will press Ctrl+C on keyboard
def watchDirectory(path):
    event_handler = DirectoryHandler(path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"Watching directory: {path}")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching directory.")
    observer.join()    # waits for the observer thread to finish before ending the script


dirPath = '' # Enter the directory which you want to organize
organizeFiles(dirPath)
watchDirectory(dirPath)
