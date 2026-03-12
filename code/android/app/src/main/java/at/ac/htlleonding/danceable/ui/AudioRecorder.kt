import android.annotation.SuppressLint
import android.content.Context
import android.media.MediaRecorder
import at.ac.htlleonding.danceable.data.model.Prediction
import at.ac.htlleonding.danceable.data.remote.RetrofitInstance
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class AudioRecorder(private val context: Context) {
    private val scope = CoroutineScope(Dispatchers.IO)
    private var recordingJob: Job? = null
    private var mediaRecorder: MediaRecorder? = null
    private var isRecording = false
    private var outputFile: File? = null

    private val _volume = MutableStateFlow(0f)
    val volume: StateFlow<Float> = _volume

    @SuppressLint("MissingPermission")
    fun startRecording(
        durationMs: Long = 3_000,
        onResult: (Result<List<Prediction>>) -> Unit
    ) {
        if (isRecording) return

        stopAndRelease()

        isRecording = true
        outputFile = File(context.filesDir, "recording_${System.currentTimeMillis()}.webm")

        try {
            mediaRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.WEBM)
                setAudioEncoder(MediaRecorder.AudioEncoder.OPUS)
                setAudioSamplingRate(48_000)
                setAudioChannels(1)
                setOutputFile(outputFile!!.absolutePath)
                prepare()
                start()
            }
        } catch (e: Exception) {
            isRecording = false
            onResult(Result.failure(e))
            return
        }

        recordingJob = scope.launch {
            val startTime = System.currentTimeMillis()
            var smoothed = 0f

            while (isRecording && System.currentTimeMillis() - startTime < durationMs) {
                val amplitude = mediaRecorder?.maxAmplitude?.toFloat() ?: 0f
                val normalized = SoundLevelGenerator.normalizeAmplitude(amplitude)
                smoothed = if (normalized > smoothed) {
                    normalized * 0.7f + smoothed * 0.3f  // fast attack
                } else {
                    normalized * 0.1f + smoothed * 0.9f  // slow decay
                }
                _volume.value = smoothed
                delay(80)
            }

            val file = outputFile
            stopAndRelease()

            if (file != null) {
                val result = uploadAudio(file)
                withContext(Dispatchers.Main) { onResult(result) }
            }
        }
    }

    fun stopRecording() {
        isRecording = false
    }

    private fun stopAndRelease() {
        isRecording = false
        _volume.value = 0f
        try {
            mediaRecorder?.stop()
        } catch (_: Exception) { }
        try {
            mediaRecorder?.release()
        } catch (_: Exception) { }
        mediaRecorder = null
    }

    private suspend fun uploadAudio(file: File): Result<List<Prediction>> {
        return try {
            val requestBody = file.asRequestBody("audio/webm".toMediaType())
            val response = RetrofitInstance.api.uploadWebm(requestBody)
            if (response.isSuccessful) Result.success(response.body().orEmpty())
            else Result.failure(RuntimeException("Upload failed: ${response.code()}"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}