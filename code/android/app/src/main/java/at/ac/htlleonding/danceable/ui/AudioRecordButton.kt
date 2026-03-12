package at.ac.htlleonding.danceable.ui

import AudioRecorder
import RecordingAnimationView
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import at.ac.htlleonding.danceable.R
import at.ac.htlleonding.danceable.viewmodel.ViewModel

@Composable
fun AudioRecorderButton(viewModel: ViewModel, size: Dp = 240.dp) {
    val context = LocalContext.current
    val recorder = remember { AudioRecorder(context) }

    val volume by recorder.volume.collectAsState()

    var isRecording by remember { mutableStateOf(false) }

    print(volume)

    val permissionLauncher =
        rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) isRecording = true
            else println("Permission denied")
        }

    fun hasPermission(): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED

    LaunchedEffect(isRecording) {
        if (isRecording) {
            recorder.startRecording { result ->
                isRecording = false
                result.onSuccess { result -> viewModel.updatePrediction(result.sortedByDescending { it.confidence }.take(3)) }
                result.onFailure { println("Recording error: ${it.message}") }
            }
        }
    }

    Box(contentAlignment = Alignment.Center) {
        val pulseScale by animateFloatAsState(
            targetValue = if (isRecording) 1.2f else 1f,
            animationSpec = if (isRecording) infiniteRepeatable(animation = tween(600), repeatMode = RepeatMode.Reverse)
            else tween(300),
            label = "pulse"
        )

        Box(modifier = Modifier.size(size).scale(pulseScale).background(Color(0xFF6C63FF).copy(alpha = 0.4f), CircleShape))

        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.size(size).clip(CircleShape).background(Color(0xFF6C63FF))
                .clickable(enabled = !isRecording) {
                    if (hasPermission()) {
                        isRecording = true
                    } else {
                        permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                    }
                }
        ) {
            Text(text = volume.toString())//this alawys is 0.0 when it is not recordeing and 1.0 when it is
            if (isRecording) RecordingAnimationView(volume)
            else Icon(painter = painterResource(R.drawable.microphone), contentDescription = null, tint = Color.White, modifier = Modifier.size(72.dp))
        }
    }
}


