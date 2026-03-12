package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import at.ac.htlleonding.danceable.MainActivity
import org.junit.Rule
import org.junit.Test

class MainScreenTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun testNavigationToDetailsAndBack() {
        composeTestRule.waitUntil(5000) {
            composeTestRule.onAllNodesWithTag("dance_item").fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onAllNodesWithTag("dance_item").onFirst().performClick()

        composeTestRule.onNodeWithText("Dance Details").assertIsDisplayed()

        composeTestRule.onNodeWithContentDescription("Back").performClick()

        composeTestRule.onNodeWithText("Danceable").assertIsDisplayed()
    }

    @Test
    fun testRecordingBottomSheetOpens() {
        composeTestRule.onNodeWithContentDescription("Start Recording", ignoreCase = true).performClick()

        composeTestRule.onNodeWithText("Recording...", ignoreCase = true).assertExists()
    }
}
