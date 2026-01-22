package at.ac.htlleonding.danceable.ui

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import at.ac.htlleonding.danceable.ui.ListScreen
import at.ac.htlleonding.danceable.viewmodel.ViewModel

@Composable
fun MainScreen(viewModel: ViewModel = viewModel()) {
    val navController = rememberNavController()
    NavHost(
        navController = navController,
        startDestination = "recording_screen"
    ) {
        composable("list_screen") {
            ListScreen(
                viewModel = viewModel,
            )
        }
        composable("recording_screen"){
            RecordingScreen(
                viewModel = viewModel
            )
        }
    }
}