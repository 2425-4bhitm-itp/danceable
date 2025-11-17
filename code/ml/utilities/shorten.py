import os
from pydub import AudioSegment

def split_wav_files(input_folder, output_folder, segment_length):
    if segment_length is None or segment_length <= 0:
        segment_length = 5000

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            filepath = os.path.join(input_folder, filename)
            audio = AudioSegment.from_wav(filepath)
            
            duration = len(audio)
            num_segments = duration // segment_length
            
            for i in range(num_segments):
                start_time = i * segment_length
                end_time = start_time + segment_length
                segment = audio[start_time:end_time]
                
                output_filename = f"{os.path.splitext(filename)[0]}_part{i+1}.wav"
                output_path = os.path.join(output_folder, output_filename)
                
                segment.export(output_path, format="wav")
                print(f"Saved {output_path}")

            os.remove(filepath)