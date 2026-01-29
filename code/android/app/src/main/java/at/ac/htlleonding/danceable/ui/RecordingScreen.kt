package at.ac.htlleonding.danceable.ui

import AudioRecorder
import android.Manifest
import android.media.MediaRecorder
import android.os.Handler
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.EaseInOut
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
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
fun AudioRecorderButton(
    size: Dp = 240.dp
) {
    val context = LocalContext.current
    val recorder = remember { AudioRecorder(context) }

    var isRecording by remember { mutableStateOf(false) }

    // Pulse animation
    val pulseScale by animateFloatAsState(
        targetValue = if (isRecording) 1.2f else 1f,
        animationSpec = if (isRecording) {
            infiniteRepeatable(
                animation = tween(600, easing = EaseInOut),
                repeatMode = RepeatMode.Reverse
            )
        } else {
            tween(durationMillis = 300, easing = EaseInOut)
        },
        label = "pulse"
    )


    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .size(size)
            .padding(16.dp)
    ) {

        // Pulsing background circle
        Box(
            modifier = Modifier
                .size(size)
                .scale(pulseScale)
                .background(
                    color = Color(0xFF6C63FF).copy(alpha = 0.4f),
                    shape = CircleShape
                )
        )

        // Main button
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(size)
                .background(
                    color = Color(0xFF6C63FF),
                    shape = CircleShape
                )
                .clickable(enabled = !isRecording) {
                    isRecording = true
                    recorder.startRecording {
                        isRecording = false
                    }
                }
        ) {
//            Icon(
//                imageVector = Icons.Filled.M,
//                contentDescription = "Record",
//                tint = Color.White,
//                modifier = Modifier.size(48.dp)
//            )
            Text(
                text = if (isRecording) "Recording..." else "Record",
                color = Color.White,
                fontWeight = FontWeight.Bold,
                fontSize = 30.sp
            )

        }
    }
}

