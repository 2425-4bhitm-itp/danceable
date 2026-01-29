import android.content.Context
import android.media.MediaRecorder
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class AudioRecorder(private val context: Context) {

    private var recorder: MediaRecorder? = null
    private val scope = CoroutineScope(Dispatchers.IO)
    private var isRecording = false

    fun startRecording(
        durationMs: Long = 3_000,
        onFinished: () -> Unit = {}
    ) {
        if (isRecording) return
        isRecording = true

        val outputFile = File(
            context.filesDir,
            "recording_${System.currentTimeMillis()}.m4a"
        )

        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setOutputFile(outputFile.absolutePath)
            prepare()
            start()
        }

        scope.launch {
            delay(durationMs)
            stopRecording()
            withContext(Dispatchers.Main) {
                isRecording = false
                onFinished()
            }
        }
    }

    private fun stopRecording() {
        try {
            recorder?.stop()
        } catch (_: Exception) {
        } finally {
            recorder?.release()
            recorder = null
        }
    }
}
