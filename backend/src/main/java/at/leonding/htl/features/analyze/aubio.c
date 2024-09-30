#include <aubio/aubio.h>
#include <jni.h>
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/opt.h>
#include <libavutil/samplefmt.h>
#include <libavutil/channel_layout.h>
#include <libavutil/mem.h>
#include <libavutil/imgutils.h>
#include <libswresample/swresample.h>
#include <stdint.h>
#include <string.h>
#include "at_leonding_htl_features_analyze_BPMAnalyzer.h"

JNIEXPORT jfloat JNICALL Java_at_leonding_htl_features_analyze_BPMAnalyzer_analyzeBPM(JNIEnv *env, jobject obj, jstring filePath) {
    const char *input_file = (*env)->GetStringUTFChars(env, filePath, NULL);

    // Initialize FFmpeg
    avformat_network_init();

    AVFormatContext *format_ctx = avformat_alloc_context();
    if (avformat_open_input(&format_ctx, input_file, NULL, NULL) != 0) {
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not open file
    }

    if (avformat_find_stream_info(format_ctx, NULL) < 0) {
        avformat_close_input(&format_ctx);
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not find stream information
    }

    int audio_stream_index = -1;
    for (int i = 0; i < format_ctx->nb_streams; i++) {
        if (format_ctx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
            audio_stream_index = i;
            break;
        }
    }

    if (audio_stream_index == -1) {
        avformat_close_input(&format_ctx);
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not find audio stream
    }

    AVCodecParameters *codecpar = format_ctx->streams[audio_stream_index]->codecpar;
    const AVCodec *codec = avcodec_find_decoder(codecpar->codec_id);
    if (!codec) {
        avformat_close_input(&format_ctx);
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not find codec
    }

    AVCodecContext *codec_ctx = avcodec_alloc_context3(codec);
    if (avcodec_parameters_to_context(codec_ctx, codecpar) < 0) {
        avcodec_free_context(&codec_ctx);
        avformat_close_input(&format_ctx);
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not copy codec context
    }

    if (avcodec_open2(codec_ctx, codec, NULL) < 0) {
        avcodec_free_context(&codec_ctx);
        avformat_close_input(&format_ctx);
        (*env)->ReleaseStringUTFChars(env, filePath, input_file);
        return -1; // Could not open codec
    }

    // Initialize aubio tempo detection
    aubio_tempo_t *tempo = new_aubio_tempo("hfc", 1024, 512, codec_ctx->sample_rate);
    fvec_t *out = new_fvec(1024);  // Buffer to hold audio samples
    fvec_t *tempo_out = new_fvec(2);  // Buffer to hold tempo output

    float bpm = 0.0f;

    AVPacket packet;
    AVFrame *frame = av_frame_alloc();
    struct SwrContext *swr_ctx = swr_alloc();

    // Set up channel layout and other parameters for swr
    int64_t in_channel_layout = codecpar->ch_layout.nb_channels == 1 ? AV_CH_LAYOUT_MONO : AV_CH_LAYOUT_STEREO;
    av_opt_set_int(swr_ctx, "in_channel_layout", in_channel_layout, 0);
    av_opt_set_int(swr_ctx, "out_channel_layout", AV_CH_LAYOUT_MONO, 0);
    av_opt_set_int(swr_ctx, "in_sample_rate", codec_ctx->sample_rate, 0);
    av_opt_set_int(swr_ctx, "out_sample_rate", 44100, 0);
    av_opt_set_sample_fmt(swr_ctx, "in_sample_fmt", codec_ctx->sample_fmt, 0);
    av_opt_set_sample_fmt(swr_ctx, "out_sample_fmt", AV_SAMPLE_FMT_FLT, 0);
    swr_init(swr_ctx);

    while (av_read_frame(format_ctx, &packet) >= 0) {
        if (packet.stream_index == audio_stream_index) {
            if (avcodec_send_packet(codec_ctx, &packet) == 0) {
                while (avcodec_receive_frame(codec_ctx, frame) == 0) {
                    float *converted_data[1];
                    converted_data[0] = out->data;
                    swr_convert(swr_ctx, (uint8_t **)converted_data, 1024, (const uint8_t **)frame->data, frame->nb_samples);

                    // Process the buffer with aubio
                    aubio_tempo_do(tempo, out, tempo_out);
                }
            }
        }
        av_packet_unref(&packet);
    }

    // Get the final BPM
    bpm = aubio_tempo_get_bpm(tempo);

    // Multiply BPM by 2.6 if it is under 65
    if (bpm < 65) {
        bpm *= 2.6;
    }

    // Cleanup
    swr_free(&swr_ctx);
    av_frame_free(&frame);
    avcodec_free_context(&codec_ctx);
    avformat_close_input(&format_ctx);
    del_aubio_tempo(tempo);
    del_fvec(out);
    del_fvec(tempo_out);
    (*env)->ReleaseStringUTFChars(env, filePath, input_file);

    return bpm;
}