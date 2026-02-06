import android.content.Context
import android.media.MediaRecorder
import android.os.Handler
import android.os.Looper
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import at.ac.htlleonding.danceable.data.remote.DanceApiService
import at.ac.htlleonding.danceable.data.remote.RetrofitInstance
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class AudioRecorder(private val context: Context) {
    private var recorder: MediaRecorder? = null
    private val scope = CoroutineScope(Dispatchers.IO)
    private var isRecording = false

    fun startRecording(
        durationMs: Long = 3_000,
        onResult: (Result<List<Prediction>>) -> Unit
    ) {
        if (isRecording) return
        isRecording = true

        val outputFile = File(
            context.filesDir,
            "recording_${System.currentTimeMillis()}.webm"
        )

        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.WEBM)
            setAudioEncoder(MediaRecorder.AudioEncoder.OPUS)
            setAudioSamplingRate(48_000)
            setAudioChannels(1)
            setOutputFile(outputFile.absolutePath)
            prepare()
            start()
        }

        scope.launch {
            delay(durationMs)
            stopRecording()

            val result = uploadAudio(outputFile);

            withContext(Dispatchers.Main) {
                isRecording = false
                onResult(result)
            }
        }
    }

    private fun stopRecording() {
        try {
            recorder?.stop()
            recorder?.release()
        } catch (_: Exception) {
        } finally {
            recorder = null
        }
    }

    private suspend fun uploadAudio(file: File): Result<List<Prediction>> {
        return try {
            val requestBody = file.asRequestBody("audio/webm".toMediaType())
            val response = RetrofitInstance.api.uploadWebm(requestBody)

            if (response.isSuccessful) {
                Result.success(response.body().orEmpty())
            } else {
                Result.failure(
                    RuntimeException("Upload failed: ${response.code()}")
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
