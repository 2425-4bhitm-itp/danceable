package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import org.junit.Rule
import org.junit.Test

class PredictionViewTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testPredictionViewDisplaysCorrectData() {
        val dance = Dance(1, "Waltz", 84, 90, "Description")
        val prediction = Prediction(1, 0.85f, "Medium")
        val dances = listOf(dance)

        composeTestRule.setContent {
            PredictionView(prediction = prediction, dances = dances)
        }

        composeTestRule.onNodeWithText("Waltz").assertIsDisplayed()
        composeTestRule.onNodeWithText("85%").assertIsDisplayed()
    }
}
