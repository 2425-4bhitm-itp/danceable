from moviepy import AudioFileClip

def convert_webm_to_wav(input_file, output_file):
    clip = AudioFileClip(input_file)
    clip.write_audiofile(output_file)

def convert_caf_to_wav(input_file, output_file):
    clip = AudioFileClip(input_file)
    clip.write_audiofile(output_file)

def convert_mp3_to_wav(input_file, output_file):
    clip = AudioFileClip(input_file)
    clip.write_audiofile(output_file)