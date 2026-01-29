package at.ac.htlleonding.danceable.data.model

data class Prediction(
//    val id: Int,
    val danceId: Int,
    val confidence: Float,
    val speedCategory: String
)