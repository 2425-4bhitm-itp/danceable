package at.ac.htlleonding.danceable.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import at.ac.htlleonding.danceable.R
import at.ac.htlleonding.danceable.ui.theme.Inter
import at.ac.htlleonding.danceable.viewmodel.ViewModel

@Composable
fun DetailScreen(
    itemId: String?,
    viewModel: ViewModel,
    onNavigateBack: () -> Unit
) {
    val dance = itemId?.toIntOrNull()?.let { viewModel.getDanceById(it) } ?: return
    val context = LocalContext.current

    val normalizedName = dance.name.lowercase().replace(" ", "_")
    val womenResId = context.resources.getIdentifier("${normalizedName}_steps_women", "drawable", context.packageName)
    val menResId = context.resources.getIdentifier("${normalizedName}_steps_men", "drawable", context.packageName)

    var selectedImageRes by remember { mutableStateOf<Int?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { onNavigateBack() }) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }
            Text(
                text = "Back",
                fontFamily = Inter,
                fontWeight = FontWeight.Medium,
                fontSize = 16.sp,
                color = Color.Black,
                modifier = Modifier.clickable { onNavigateBack() }
            )
        }

        if (womenResId != 0) {
            Image(
                painter = painterResource(womenResId),
                contentDescription = "${dance.name} steps women",
                modifier = Modifier.fillMaxWidth(0.95f)
                    .clickable { selectedImageRes = womenResId }
            )
            Text(
                text = "Women step pattern",
                fontFamily = Inter,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Color.Gray
            )
            Spacer(Modifier.height(12.dp))
        }

        if (menResId != 0) {
            Image(
                painter = painterResource(menResId),
                contentDescription = "${dance.name} steps men",
                modifier = Modifier.fillMaxWidth(0.95f)
                    .clickable { selectedImageRes = menResId }
            )
            Text(
                text = "Men step pattern",
                fontFamily = Inter,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Color.Gray
            )
            Spacer(Modifier.height(12.dp))
        }

        if (selectedImageRes != null) {
            Dialog(onDismissRequest = { selectedImageRes = null }) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp)
                ) {
                    Image(
                        painter = painterResource(selectedImageRes!!),
                        contentDescription = "Full screen",
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(1f)
                    )
                }
            }
        }

        Text(
            text = dance.name,
            fontFamily = Inter,
            fontSize = 50.sp,
            fontWeight = FontWeight.Bold,
            color = Color.Black
        )

        Spacer(Modifier.height(5.dp))

        Text(
            text = "${dance.minBpm} BPM - ${dance.maxBpm} BPM",
            fontFamily = Inter,
            fontSize = 20.sp,
            fontWeight = FontWeight.SemiBold,
            color = Color.Black
        )

        Spacer(Modifier.height(5.dp))

        Text(
            text = dance.description,
            fontFamily = Inter,
            fontSize = 12.sp,
            fontWeight = FontWeight.Thin,
            color = Color.Black
        )
    }
}