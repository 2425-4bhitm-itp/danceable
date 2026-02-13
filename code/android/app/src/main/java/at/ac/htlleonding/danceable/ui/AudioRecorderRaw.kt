package at.ac.htlleonding.danceable.ui

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import kotlin.math.abs
import kotlin.math.log10
import kotlin.math.sqrt

class AudioRecorderRaw(private val context: Context) {

    private var audioRecord: AudioRecord? = null
    private var recordingJob: Job? = null
    private var isRecording = false

    private val sampleRate = 44100
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT

    private val _soundLevels = MutableStateFlow(List(7) { 0f })
    val soundLevels: StateFlow<List<Float>> = _soundLevels

    private val scope = CoroutineScope(Dispatchers.IO)

    fun startRecording(
        durationMs: Long = 3000,
        onFinished: (Result<File>) -> Unit
    ) {
        if (isRecording) return

        if (ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            onFinished(Result.failure(SecurityException("RECORD_AUDIO permission not granted")))
            return
        }

        isRecording = true

        val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
        val outputFile = File(context.filesDir, "recording_${System.currentTimeMillis()}.raw")
        val buffer = ShortArray(bufferSize)

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelConfig,
            audioFormat,
            bufferSize
        )

        recordingJob = scope.launch {
            try {
                audioRecord?.startRecording()

                val startTime = System.currentTimeMillis()

                FileOutputStream(outputFile).use { fos ->
                    while (System.currentTimeMillis() - startTime < durationMs) {
                        val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                        if (read > 0) {
                            val byteArray = ByteArray(read * 2)
                            for (i in 0 until read) {
                                byteArray[i * 2] = (buffer[i].toInt() and 0xFF).toByte()
                                byteArray[i * 2 + 1] = (buffer[i].toInt() shr 8).toByte()
                            }
                            fos.write(byteArray)
                            processBuffer(buffer.copyOf(read))
                        }
                    }
                }

                stopRecording()
                withContext(Dispatchers.Main) { onFinished(Result.success(outputFile)) }

            } catch (e: Exception) {
                stopRecording()
                withContext(Dispatchers.Main) { onFinished(Result.failure(e)) }
            }
        }
    }

    private fun stopRecording() {
        try {
            audioRecord?.stop()
        } catch (_: Exception) { }
        audioRecord?.release()
        audioRecord = null
        isRecording = false
    }

    private fun processBuffer(buffer: ShortArray) {
        val rms = sqrt(buffer.sumOf { it * it.toDouble() } / buffer.size)
        val db = 20 * log10(rms / Short.MAX_VALUE)
        val normalized = ((db + 50f) / 50f).coerceIn(0.0, 1.0)
        _soundLevels.value = generateSmoothedLevels(normalized)
    }

    private fun generateSmoothedLevels(normalized: Double): List<Float> {
        val count = _soundLevels.value.size
        val center = count / 2
        return List(count) { i ->
            val distance = abs(i - center)
            val scale = 1f - (distance.toFloat() / center) * 0.75f
            val jitter = (Math.random().toFloat() * 0.15f) - 0.075f
            (normalized * scale + jitter).coerceIn(0.0, 1.0).toFloat()
        }
    }
}
