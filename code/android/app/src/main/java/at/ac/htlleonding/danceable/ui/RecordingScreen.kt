package at.ac.htlleonding.danceable.ui

import AudioRecorder
import android.Manifest
import android.media.MediaRecorder
import android.os.Handler
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import at.ac.htlleonding.danceable.viewmodel.ViewModel

var recorder: MediaRecorder? = null
lateinit var outputFile: String

private val handler = Handler(Looper.getMainLooper())

@Composable
fun RecordingScreen(
    viewModel: ViewModel = viewModel(),
){
    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) {}

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFFFFFF))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        AudioRecorderButton()
    }
}

@Composable
fun AudioRecorderButton() {
    val context = LocalContext.current
    val recorder = remember { AudioRecorder(context) }

    var isRecording by remember { mutableStateOf(false) }

    Button(
        enabled = !isRecording,
        onClick = {
            isRecording = true
            recorder.startRecording {
                isRecording = false
            }
        }
    ) {
        Text(if (isRecording) "Recording…" else "Record 3 seconds")
    }
}
