import os
import shutil

def sort_and_delete_wav_files(source_dir):
    completed_count = 0
    
    for file_name in os.listdir(source_dir):
        if file_name.endswith(".wav"):
            file_path = os.path.join(source_dir, file_name)
            
            # Split the file name by underscore and hyphen
            name_parts = file_name.split('_')
            
            if len(name_parts) >= 2:
                genre_part = name_parts[1].split('-')  # The second part after the underscore is the genres
                
                # Skip files with multiple genres
                if len(genre_part) > 1:
                    # delete song with multiple genre
                    os.remove(file_path)
                    print(f"Deleted {file_name}")
                    continue
                
                genre = genre_part[0]  # Take only the first genre
                genre_dir = os.path.join(source_dir, genre)
                
                if not os.path.exists(genre_dir):
                    os.makedirs(genre_dir)
                
                # Move the file into the genre directory
                shutil.move(file_path, os.path.join(genre_dir, file_name))
                print(f"Moved {file_name} to {genre_dir}")
                completed_count += 1
            else:
                print(f"File name format is incorrect: {file_path}")
    
    print(f"Total files processed: {completed_count}")