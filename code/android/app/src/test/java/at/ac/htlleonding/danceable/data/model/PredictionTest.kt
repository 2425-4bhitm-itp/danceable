package at.ac.htlleonding.danceable.data.model

import org.junit.Assert.assertEquals
import org.junit.Test

class PredictionTest {
    @Test
    fun `test prediction data class`() {
        val prediction = Prediction(
            danceId = 5,
            confidence = 0.95f,
            speedCategory = "Fast"
        )

        assertEquals(5, prediction.danceId)
        assertEquals(0.95f, prediction.confidence)
        assertEquals("Fast", prediction.speedCategory)
    }

    @Test
    fun `test prediction equality`() {
        val p1 = Prediction(1, 0.5f, "Slow")
        val p2 = Prediction(1, 0.5f, "Slow")
        assertEquals(p1, p2)
    }

    @Test
    fun `test prediction copy`() {
        val p1 = Prediction(1, 0.5f, "Slow")
        val p2 = p1.copy(confidence = 0.8f)
        assertEquals(0.8f, p2.confidence)
        assertEquals(1, p2.danceId)
    }
}
