#include <aubio/aubio.h>
#include <jni.h>
#include <string.h>  // Include the string.h header for memcpy
#include "at_leonding_htl_features_analyze_BPMAnalyzer.h"

JNIEXPORT jfloat JNICALL Java_at_leonding_htl_features_analyze_BPMAnalyzer_analyzeBPM(JNIEnv *env, jobject obj, jobject inputStream) {
    // Get the InputStream class and read method
    jclass inputStreamClass = (*env)->GetObjectClass(env, inputStream);
    jmethodID readMethod = (*env)->GetMethodID(env, inputStreamClass, "read", "([B)I");

    // Initialize aubio tempo detection
    aubio_tempo_t *tempo = new_aubio_tempo("default", 512, 256, 44100);
    fvec_t *out = new_fvec(512);  // Buffer to hold audio samples
    fvec_t *tempo_out = new_fvec(2);  // Buffer to hold tempo output

    float bpm = 0.0f;

    // Buffer to read data from InputStream
    jbyteArray buffer = (*env)->NewByteArray(env, 512 * sizeof(float));
    jbyte *bufferElements = (*env)->GetByteArrayElements(env, buffer, NULL);

    // Process the InputStream frame by frame until the end of the stream
    while (1) {
        // Read data from InputStream
        jint bytesRead = (*env)->CallIntMethod(env, inputStream, readMethod, buffer);
        if (bytesRead <= 0) break;  // End of stream

        // Copy data to aubio buffer
        memcpy(out->data, bufferElements, bytesRead);

        // Process the buffer with aubio
        aubio_tempo_do(tempo, out, tempo_out);
        bpm = aubio_tempo_get_bpm(tempo);  // Get BPM
    }

    // Cleanup aubio resources
    del_aubio_tempo(tempo);
    del_fvec(out);
    del_fvec(tempo_out);

    // Release the buffer
    (*env)->ReleaseByteArrayElements(env, buffer, bufferElements, 0);
    (*env)->DeleteLocalRef(env, buffer);

    return bpm;
}