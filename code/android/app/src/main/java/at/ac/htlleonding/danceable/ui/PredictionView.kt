package at.ac.htlleonding.danceable.ui

import androidx.compose.material3.LinearProgressIndicator
import at.ac.htlleonding.danceable.data.model.Prediction

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import at.ac.htlleonding.danceable.ui.theme.Inter

@Composable
fun PredictionView(prediction: Prediction) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        color = Color(0xFFE0E0E0), // leicht grauer Hintergrund
        shape = RoundedCornerShape(8.dp),
        shadowElevation = 2.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Dance Name
            Text(
                text = prediction.danceId.toString(),
                fontFamily = Inter,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF000000)
            )

            // BPM Bereich
            LinearProgressIndicator(
                progress = { prediction.confidence },
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
