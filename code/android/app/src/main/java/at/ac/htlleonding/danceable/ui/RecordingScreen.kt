package at.ac.htlleonding.danceable.ui

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import at.ac.htlleonding.danceable.R
import at.ac.htlleonding.danceable.viewmodel.ViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordingScreen(
    viewModel: ViewModel = viewModel(),
){
    val sheetState = rememberModalBottomSheetState()
    val isSheetOpen by viewModel.isSheetOpen.collectAsState()

    val bounceOffset = remember{Animatable(0f)}

    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) {}

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)

        var bouncesCounter = 0;
        var maxBounces = 2;
        while(bouncesCounter < maxBounces){
            bounceOffset.animateTo(targetValue = -30f, animationSpec = tween(durationMillis = 400))
            bounceOffset.animateTo(targetValue = 0f, animationSpec = tween(durationMillis = 300))
            bouncesCounter++;
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .padding(16.dp)
            .pointerInput(Unit){
                detectVerticalDragGestures(){change, dragAmount ->
                    if(dragAmount < -10f){
                        viewModel.openSheet();
                    }
                    change.consume();
                }
            },
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        AudioRecorderButton(viewModel)

        Spacer(modifier = Modifier.weight(1f))

        Icon(
            Icons.Filled.KeyboardArrowUp, tint = Color(0XBBBFBFBF),
            contentDescription = "Pull sheet", modifier= Modifier.size(70.dp).offset(y=bounceOffset.value.dp)
            )
    }

    if (isSheetOpen) {
        ModalBottomSheet(
            onDismissRequest = { viewModel.closeSheet() },
            sheetState = sheetState
        ) {
            PredictionsView(viewModel)
        }
    }
}
