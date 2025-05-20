import moviepy

def convert_webm_to_wav(input_file, output_file):
    clip = moviepy.VideoFileClip(input_file)
    clip.audio.write_audiofile(output_file)

def convert_caf_to_wav(input_file, output_file):
    clip = moviepy.AudioFileClip(input_file)
    clip.write_audiofile(output_file)