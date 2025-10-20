package nz.yoobee.kaihelper.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    //local
    private const val BASE_URL = "http://192.168.1.227:8000/"
    //prod
    //private const val BASE_URL = "https://yo463uaqt2.execute-api.ap-southeast-2.amazonaws.com/Prod/"

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val userService: UserService = retrofit.create(UserService::class.java)
}
