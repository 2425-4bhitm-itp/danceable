package at.ac.htlleonding.danceable.data.model

data class Dance(
    val id: Int,
    val name: String,
    val minBpm: Int,
    val maxBpm: Int,
    val description: String
)
