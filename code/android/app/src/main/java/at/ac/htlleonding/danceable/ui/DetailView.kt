package at.ac.htlleonding.danceable.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import at.ac.htlleonding.danceable.viewmodel.ViewModel


@Composable
fun DetailScreen(itemId: String?, viewModel: ViewModel){
    val item = viewModel.getDanceById(Integer.parseInt(itemId))


}