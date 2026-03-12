package at.ac.htlleonding.danceable.ui.navigation

import org.junit.Assert.assertEquals
import org.junit.Test

class ScreenTest {
    @Test
    fun `test screen routes`() {
        assertEquals("list", Screen.List.route)
        assertEquals("recording", Screen.Recording.route)
        assertEquals("detail/{itemId}", Screen.Detail.route)
    }

    @Test
    fun `test detail route creation`() {
        val route = Screen.Detail.createRoute("5")
        assertEquals("detail/5", route)
    }
}
