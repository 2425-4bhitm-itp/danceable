package at.ac.htlleonding.danceable.ui

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun RecordingAnimationView(soundLevels: List<Float>) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        soundLevels.forEach { level ->
            val barHeight by animateFloatAsState(
                targetValue = 60.dp.value * level,
                animationSpec = tween(durationMillis = 100),
                label = "barHeight"
            )

            Box(
                modifier = Modifier
                    .width(12.dp)
                    .height(barHeight.dp)
                    .background(Color.White, RoundedCornerShape(4.dp))
            )
        }
    }
}
