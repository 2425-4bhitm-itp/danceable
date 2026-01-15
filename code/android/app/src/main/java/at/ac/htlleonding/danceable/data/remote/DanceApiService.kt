package at.ac.htlleonding.danceable.data.remote

import at.ac.htlleonding.danceable.data.model.Dance
import retrofit2.http.GET

interface DanceApiService {

    @GET
    suspend fun getDances(): List<Dance>
}