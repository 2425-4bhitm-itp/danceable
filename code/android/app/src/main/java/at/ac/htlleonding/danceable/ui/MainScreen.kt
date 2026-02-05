package at.ac.htlleonding.danceable.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import at.ac.htlleonding.danceable.ui.ListScreen
import at.ac.htlleonding.danceable.ui.navigation.Screen
import at.ac.htlleonding.danceable.viewmodel.ViewModel

@Composable
fun MainScreen(viewModel: ViewModel = viewModel()) {
    val navController = rememberNavController()

    val items = listOf(
        Screen.Recording,
        Screen.List
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                val currentDestination =
                    navController.currentBackStackEntryAsState().value?.destination

                items.forEach { screen ->
//                    NavigationBarItem(
//                        icon = { Icon(screen.icon, contentDescription = screen.label) },
//                        label = { Text(screen.label) },
//                        selected = currentDestination?.route == screen.route,
//                        onClick = {
//                            navController.navigate(screen.route) {
//                                popUpTo(navController.graph.startDestinationId) {
//                                    saveState = true
//                                }
//                                launchSingleTop = true
//                                restoreState = true
//                            }
//                        }
//                    )
//                    import androidx.compose.ui.res.stringResource

                    NavigationBarItem(
                        icon = {
                            Icon(
                                screen.icon,
                                contentDescription = stringResource(screen.labelRes)
                            )
                        },
                        label = {
                            Text(stringResource(screen.labelRes))
                        },
                        selected = currentDestination?.route == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.List.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.List.route) {
                ListScreen(viewModel = viewModel)
            }
            composable(Screen.Recording.route) {
                RecordingScreen(viewModel = viewModel)
            }
        }
    }
}
