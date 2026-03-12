// SoundLevelGenerator.kt
import kotlin.math.*
import kotlin.random.Random

object SoundLevelGenerator {
    const val BAR_COUNT = 11
    private const val BAR_WIDTH_PX = 7f
    private const val GAP_PX = 5f
    private const val CIRCLE_RADIUS_DP = 90f

    private val positionWeights = floatArrayOf(0.25f, 0.4f, 0.6f, 0.78f, 0.92f, 1.0f, 0.92f, 0.78f, 0.6f, 0.4f, 0.25f)

    val circleMaxHeights: List<Float> by lazy {
        val totalWidth = BAR_COUNT * BAR_WIDTH_PX + (BAR_COUNT - 1) * GAP_PX
        val startX = -totalWidth / 2f + BAR_WIDTH_PX / 2f
        List(BAR_COUNT) { i ->
            val x = startX + i * (BAR_WIDTH_PX + GAP_PX)
            2f * sqrt(max(0f, CIRCLE_RADIUS_DP.pow(2) - x.pow(2)))
        }
    }

    private val phases = FloatArray(BAR_COUNT) { Random.nextFloat() * 2f * PI.toFloat() }
    private val speeds = FloatArray(BAR_COUNT) { 1.2f + Random.nextFloat() * 2.2f }

    fun generateLevels(volume: Float, deltaSeconds: Float): List<Float> {
        return List(BAR_COUNT) { i ->
            phases[i] += deltaSeconds * speeds[i] * (2.0f + volume * 4.0f)
            val wave1 = 0.5f + 0.5f * sin(phases[i])
            val wave2 = 0.5f + 0.5f * sin(phases[i] * 0.37f + 1.3f)
            val osc = 0.4f + 0.6f * (wave1 * 0.65f + wave2 * 0.35f)
            (volume * osc * positionWeights[i]).coerceIn(0f, 1f)
        }
    }

    fun normalizeAmplitude(amplitude: Float): Float {
        if (amplitude < 500f) return 0f
        return ((amplitude - 500f) / (25000f - 500f))
            .coerceIn(0f, 1f)
            .pow(0.6f)
    }
}