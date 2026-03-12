package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.viewmodel.ViewModel
import io.mockk.every
import io.mockk.mockk
import org.junit.Rule
import org.junit.Test

class DetailScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testDetailScreenDisplaysCorrectData() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        val dance = Dance(
            id = 1,
            name = "Salsa",
            minBpm = 160,
            maxBpm = 220,
            description = "Energetic Latin dance"
        )
        every { viewModel.getDanceById(1) } returns dance

        composeTestRule.setContent {
            DetailScreen(itemId = "1", viewModel = viewModel, onNavigateBack = {})
        }

        composeTestRule.onNodeWithText("Salsa").assertIsDisplayed()
        composeTestRule.onNodeWithText("160 BPM - 220 BPM").assertIsDisplayed()
        composeTestRule.onNodeWithText("Energetic Latin dance").assertIsDisplayed()
    }

    @Test
    fun testDetailScreenBackButton() {
        var backClicked = false
        val viewModel = mockk<ViewModel>(relaxed = true)
        val dance = Dance(1, "Salsa", 160, 220, "Desc")
        every { viewModel.getDanceById(1) } returns dance

        composeTestRule.setContent {
            DetailScreen(itemId = "1", viewModel = viewModel, onNavigateBack = { backClicked = true })
        }

        composeTestRule.onNodeWithContentDescription("Back").performClick()
        assert(backClicked)
    }
}
