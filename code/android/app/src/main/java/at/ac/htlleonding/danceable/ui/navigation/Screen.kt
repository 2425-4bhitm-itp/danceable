package at.ac.htlleonding.danceable.ui.navigation

import androidx.annotation.DrawableRes
import at.ac.htlleonding.danceable.R
import androidx.annotation.StringRes

sealed class Screen(
    val route: String,
    @StringRes val labelRes: Int,
    @DrawableRes val icon: Int
) {
    object Dances : Screen(
        route = "dances",
        labelRes = R.string.nav_list,
        icon = R.drawable.library
    )

    object Prediction : Screen(
        route = "prediction",
        labelRes = R.string.nav_prediction,
        icon = R.drawable.batch_prediciton
    )

    object Recording : Screen(
        route = "recording",
        labelRes = R.string.nav_recording,
        icon = R.drawable.microphone
    )
}
