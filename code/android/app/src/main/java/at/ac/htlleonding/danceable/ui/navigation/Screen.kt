package at.ac.htlleonding.danceable.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Home
import androidx.compose.ui.graphics.vector.ImageVector
import at.ac.htlleonding.danceable.R
import androidx.annotation.StringRes

sealed class Screen(
    val route: String,
    @StringRes val labelRes: Int,
    val icon: ImageVector
) {
    object List : Screen(
        route = "list",
        labelRes = R.string.nav_list,
        icon = Icons.AutoMirrored.Filled.List
    )

    object Recording : Screen(
        route = "recording",
        labelRes = R.string.nav_recording,
        icon = Icons.Default.Home
    )
}
