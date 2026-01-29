package at.ac.htlleonding.danceable.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import at.ac.htlleonding.danceable.ui.theme.Inter
import at.ac.htlleonding.danceable.viewmodel.ViewModel


@Composable
fun PredictionsView(
    viewModel: ViewModel = viewModel(),
) {
    val predictions by viewModel.predictions.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFFFFFF))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Spacer(modifier = Modifier.height(16.dp))

        Column (
            modifier = Modifier.padding(8.dp)
        ) {
            if (predictions.isEmpty()) {
                Text("No Predictions Found", fontFamily = Inter, fontWeight = FontWeight.SemiBold)
            } else {
                predictions.forEach { prediction ->
                    PredictionView(prediction)
                }
            }
        }

    }
}