    package nz.yoobee.kaihelper.api

    import nz.yoobee.kaihelper.models.GroceryDTO
    import nz.yoobee.kaihelper.models.ResultDTO
    import retrofit2.Call
    import retrofit2.http.GET
    import retrofit2.http.PUT
    import retrofit2.http.DELETE
    import retrofit2.http.Body
    import retrofit2.http.Path

    interface GroceryService {
        @GET("api/groceries/expense/{expense_id}")
        fun getGroceriesByExpense(@Path("expense_id") expenseId: Int): Call<ResultDTO<List<GroceryDTO>>>

        @PUT("api/groceries/update")
        fun updateGrocery(@Body grocery: GroceryDTO): Call<ResultDTO<GroceryDTO>>

        @DELETE("api/groceries/delete/{id}")
        fun deleteGrocery(@Path("id") id: Int): Call<ResultDTO<Boolean>>

    }
