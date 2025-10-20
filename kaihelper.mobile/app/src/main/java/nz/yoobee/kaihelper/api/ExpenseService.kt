package nz.yoobee.kaihelper.api

import nz.yoobee.kaihelper.models.ExpenseDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.models.GroceryDTO
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Path

interface ExpenseService {

    // ✅ Fetch all expenses for a specific user
    @GET("api/expenses/user/{id}")
    fun getExpensesByUser(@Path("id") userId: Int): Call<ResultDTO<List<ExpenseDTO>>>

    //@GET("expense/{expense_id}")
    //fun getGroceriesByExpense(@Path("expense_id") expenseId: Int): Call<ResultDTO<List<GroceryDTO>>>
}
