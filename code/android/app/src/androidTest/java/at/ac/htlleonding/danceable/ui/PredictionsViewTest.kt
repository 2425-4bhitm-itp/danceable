package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import at.ac.htlleonding.danceable.viewmodel.ViewModel
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Rule
import org.junit.Test

class PredictionsViewTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testEmptyPredictions() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        every { viewModel.predictions } returns MutableStateFlow(emptyList())
        every { viewModel.dances } returns MutableStateFlow(emptyList())

        composeTestRule.setContent {
            PredictionsView(viewModel = viewModel)
        }

        composeTestRule.onNodeWithText("No Predictions Found").assertIsDisplayed()
    }

    @Test
    fun testVisiblePredictions() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        val predictions = listOf(Prediction(1, 0.9f, "Fast"))
        every { viewModel.predictions } returns MutableStateFlow(predictions)
        every { viewModel.dances } returns MutableStateFlow(listOf(
            Dance(1, "Waltz", 84, 90, "Desc")
        ))
        composeTestRule.setContent {
            PredictionsView(viewModel = viewModel)
        }

        composeTestRule.onNodeWithText("No Predictions Found").assertDoesNotExist()
    }
}
