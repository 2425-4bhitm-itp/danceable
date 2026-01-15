package at.htl.runnerzeigs.data.remote

import at.ac.htlleonding.danceable.data.remote.DanceApiService
import com.google.gson.GsonBuilder
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    private const val BASE_URL = "https://it210192.cloud.htl-leonding.ac.at"
    private val gson = GsonBuilder()
        .serializeNulls()
        .create()
    val api: DanceApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(DanceApiService::class.java)
    }
}