package at.ac.htlleonding.danceable.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Home
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(
    val route: String,
    val label: String,
    val icon: ImageVector
) {
    object List : Screen("list_screen", "Dances", Icons.AutoMirrored.Filled.List)
    object Recording : Screen("recording_screen", "Recognize", Icons.Default.Home)
}
