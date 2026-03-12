package at.ac.htlleonding.danceable.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import at.ac.htlleonding.danceable.viewmodel.ViewModel
import io.mockk.mockk
import io.mockk.verify
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AudioRecorderButtonTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testInitialButtonState() {
        val viewModel = mockk<ViewModel>(relaxed = true)
        
        composeTestRule.setContent {
            AudioRecorderButton(viewModel = viewModel)
        }

        composeTestRule.onNode(hasClickAction()).assertIsDisplayed()
    }
}
