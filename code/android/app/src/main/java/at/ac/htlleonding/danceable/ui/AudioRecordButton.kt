package at.ac.htlleonding.danceable.ui

import AudioRecorder
import androidx.compose.animation.core.EaseInOut
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import at.ac.htlleonding.danceable.R

@Composable
fun AudioRecorderButton(
    size: Dp = 240.dp
) {
    val context = LocalContext.current
    val recorder = remember { AudioRecorder(context) }

    var isRecording by remember { mutableStateOf(false) }

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

        Box(
            modifier = Modifier
                .size(size)
                .scale(pulseScale)
                .background(
                    color = Color(0xFF6C63FF).copy(alpha = 0.4f),
                    shape = CircleShape
                )
        )

        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(size)
                .background(
                    color = Color(0xFF6C63FF),
                    shape = CircleShape
                )
                .clip(CircleShape)
                .clickable(enabled = !isRecording) {
                    isRecording = true
                    recorder.startRecording {
                        isRecording = false
                    }
                }
        ) {
            if (!isRecording) {
                Icon(
                    painter = painterResource(R.drawable.microphone),
                    contentDescription = null,
                    modifier = Modifier.size(72.dp),
                    tint = Color.White
                )
            } else {
                Text(
                    text = "Recording...",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 30.sp
                )
            }

        }
    }
}
