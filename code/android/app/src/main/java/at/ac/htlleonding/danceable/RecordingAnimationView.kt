import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun RecordingAnimationView(
    volume: Float,
    modifier: Modifier = Modifier,
    barColor: Color = Color.White,
) {
    val density = LocalDensity.current.density
    val animatedLevels = remember { List(SoundLevelGenerator.BAR_COUNT) { Animatable(0f) } }
    val lastTime = remember { mutableLongStateOf(System.nanoTime()) }

    LaunchedEffect(volume) {
        while (true) {
            val now = System.nanoTime()
            val delta = ((now - lastTime.longValue) / 1_000_000_000f).coerceAtMost(0.05f)
            lastTime.longValue = now

            val newLevels = SoundLevelGenerator.generateLevels(volume, delta)
            animatedLevels.forEachIndexed { i, anim ->
                launch {
                    anim.animateTo(
                        targetValue = newLevels[i],
                        animationSpec = tween(80, easing = EaseInOut)
                    )
                }
            }
            delay(80)
        }
    }

    Row(
        horizontalArrangement = Arrangement.spacedBy(7.5.dp),
        verticalAlignment = Alignment.CenterVertically,
        modifier = modifier,
    ) {
        animatedLevels.forEachIndexed { i, animLevel ->
            val level by animLevel.asState()
            val maxForThisBar = SoundLevelGenerator.circleMaxHeights[i]
            val heightDp = (level * maxForThisBar).coerceAtLeast(0f)

            Box(
                modifier = Modifier
                    .width(7.dp)
                    .height(heightDp.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(barColor.copy(alpha = if (heightDp < 4f) heightDp / 4f else 1f))
            )
        }
    }
}