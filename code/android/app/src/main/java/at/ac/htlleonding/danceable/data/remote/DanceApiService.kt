package at.ac.htlleonding.danceable.data.remote

import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface DanceApiService {

    @GET("dances")
    suspend fun getDances(): List<Dance>

    @POST("audio/uploadWebmStream/tmp")
    suspend fun uploadWebm(
        @Body body: RequestBody
    ): Response<List<Prediction>>
}

