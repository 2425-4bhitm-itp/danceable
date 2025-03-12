import moviepy

def convert_webm_to_wav(input_file, output_file):
    clip = moviepy.VideoFileClip(input_file)
    clip.audio.write_audiofile(output_file)