package at.ac.htlleonding.danceable.data.model

import org.junit.Assert.assertEquals
import org.junit.Test

class DanceTest {
    @Test
    fun `test dance data class`() {
        val dance = Dance(
            id = 1,
            name = "Waltz",
            minBpm = 84,
            maxBpm = 90,
            description = "A smooth, progressive ballroom dance"
        )

        assertEquals(1, dance.id)
        assertEquals("Waltz", dance.name)
        assertEquals(84, dance.minBpm)
        assertEquals(90, dance.maxBpm)
        assertEquals("A smooth, progressive ballroom dance", dance.description)
    }

    @Test
    fun `test dance equality`() {
        val dance1 = Dance(1, "Waltz", 84, 90, "Desc")
        val dance2 = Dance(1, "Waltz", 84, 90, "Desc")
        assertEquals(dance1, dance2)
        assertEquals(dance1.hashCode(), dance2.hashCode())
    }

    @Test
    fun `test dance copy`() {
        val dance1 = Dance(1, "Waltz", 84, 90, "Desc")
        val dance2 = dance1.copy(name = "Tango")
        assertEquals(1, dance2.id)
        assertEquals("Tango", dance2.name)
    }
}
