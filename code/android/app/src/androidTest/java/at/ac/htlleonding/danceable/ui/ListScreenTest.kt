package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.viewmodel.ViewModel
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ListScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testEmptyListDisplaysNoDancesFound() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        every { viewModel.dances } returns MutableStateFlow(emptyList())

        composeTestRule.setContent {
            ListScreen(viewModel = viewModel, onItemClick = {})
        }

        composeTestRule.onNodeWithText("No Dances Found").assertIsDisplayed()
    }

    @Test
    fun testPopulatedListDisplaysItems() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        val dances = listOf(
            Dance(1, "Waltz", 84, 90, "Desc"),
            Dance(2, "Tango", 120, 130, "Desc")
        )
        every { viewModel.dances } returns MutableStateFlow(dances)

        composeTestRule.setContent {
            ListScreen(viewModel = viewModel, onItemClick = {})
        }

        composeTestRule.onNodeWithText("Waltz").assertIsDisplayed()
        composeTestRule.onNodeWithText("Tango").assertIsDisplayed()
    }
}
