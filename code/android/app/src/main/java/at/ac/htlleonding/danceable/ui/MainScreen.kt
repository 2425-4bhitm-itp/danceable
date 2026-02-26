package at.ac.htlleonding.danceable.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ModifierLocalBeyondBoundsLayout
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
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
                    NavigationBarItem(
                        icon = {
                            Icon(
                                painter = painterResource(screen.icon),
                                contentDescription = null,
                                modifier = Modifier.size(24.dp)
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
                ListScreen(viewModel = viewModel,
                    onItemClick = {itemId -> navController.navigate(Screen.Detail.createRoute(itemId))})
            }
            composable(Screen.Recording.route) {
                RecordingScreen(viewModel = viewModel)
            }
            composable(route = Screen.Detail.route, arguments =
                listOf(navArgument("itemId") {type=NavType.StringType})
            ){ backStackEntry ->
                val itemId = backStackEntry.arguments?.getString("itemId")
                DetailScreen(itemId = itemId, viewModel = viewModel, onNavigateBack = {navController.popBackStack()})
            }
        }
    }
}
