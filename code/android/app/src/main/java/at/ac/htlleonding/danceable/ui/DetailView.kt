package at.ac.htlleonding.danceable.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import at.ac.htlleonding.danceable.R
import at.ac.htlleonding.danceable.ui.theme.Inter
import at.ac.htlleonding.danceable.viewmodel.ViewModel
import kotlin.math.roundToInt


@Composable
fun DetailScreen(itemId: String?, viewModel: ViewModel, onNavigateBack: () -> Unit){
    val dance = viewModel.getDanceById(Integer.parseInt(itemId))

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        Image(
            painter = painterResource(R.drawable.placeholder),
            contentDescription = "Placeholder",
            modifier = Modifier.fillMaxWidth(0.7f)
        )

        Text(text = dance!!.name,
            fontFamily = Inter,
            fontSize = 50.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF000000))

        Spacer(Modifier.height(5.dp))

        Text(
            text = String.format("%d BPM - %d BPM", dance.minBpm, dance.maxBpm),
                fontFamily = Inter,
                fontSize= 20.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF0000000)
        )

        Spacer(Modifier.height(5.dp))

        Text(
            text = "Lorem Ipsum",
            fontFamily = Inter,
            fontSize = 10.sp,
            fontWeight = FontWeight.Thin,
            color = Color(0xFF000000),
        )
    }

}