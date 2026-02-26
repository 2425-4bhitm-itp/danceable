package at.ac.htlleonding.danceable.ui.navigation

import androidx.annotation.DrawableRes
import at.ac.htlleonding.danceable.R
import androidx.annotation.StringRes

sealed class Screen(
    val route: String,
    @StringRes val labelRes: Int,
    @DrawableRes val icon: Int
) {
    object List : Screen(
        route = "list",
        labelRes = R.string.nav_list,
        icon = R.drawable.library
    )

    object Recording : Screen(
        route = "recording",
        labelRes = R.string.nav_recording,
        icon = R.drawable.microphone
    )

    object Detail: Screen(
        route = "detail/{itemId}",
        labelRes = R.string.nav_detail,
        icon = R.drawable.library
    ){
        fun createRoute(itemId: String) = "detail/$itemId"
    }
}
