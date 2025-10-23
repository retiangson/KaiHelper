package nz.yoobee.kaihelper.ui.fragments

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.data.PieData
import com.github.mikephil.charting.data.PieDataSet
import com.github.mikephil.charting.data.PieEntry
import com.github.mikephil.charting.utils.ColorTemplate
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.*
import nz.yoobee.kaihelper.core.DateManager
import nz.yoobee.kaihelper.models.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.*

class InsightFragment : Fragment(), DateFilterable {

    private lateinit var chartByCategory: PieChart
    private lateinit var chartByLocalization: PieChart
    private val dm = DateManager
    private val expenseService = ApiClient.retrofit.create(ExpenseService::class.java)
    private val groceryService = ApiClient.retrofit.create(GroceryService::class.java)
    private val categoryService = ApiClient.retrofit.create(CategoryService::class.java)
    private val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    private val categoryMap = mutableMapOf<Int, String>()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_insight, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        chartByCategory = view.findViewById(R.id.chartByCategory)
        chartByLocalization = view.findViewById(R.id.chartByLocalization)

        loadCategoriesThenInsights()
    }

    override fun onDateFilterChanged(tab: String, year: Int, month: Int, week: Int) {
        loadInsights(tab, year, month, week)
    }

    private fun loadCategoriesThenInsights() {
        categoryService.getCategories().enqueue(object : Callback<ResultDTO<Any>> {
            override fun onResponse(
                call: Call<ResultDTO<Any>>,
                response: Response<ResultDTO<Any>>
            ) {
                try {
                    // ✅ Log full JSON for debugging
                    val gson = com.google.gson.GsonBuilder().setPrettyPrinting().create()
                    val json = gson.toJson(response.body())
                    Log.d("InsightDebug", "✅ Categories raw JSON:\n$json")

                    // ✅ Unwrap nested ResultDTO
                    val outerData = response.body()?.data
                    val innerMap = outerData as? Map<*, *>
                    val innerData = innerMap?.get("data") as? List<*>

                    val categories = innerData?.mapNotNull { item ->
                        (item as? Map<*, *>)?.let {
                            CategoryDTO(
                                category_id = (it["category_id"] as? Double)?.toInt(),
                                name = it["name"] as? String ?: "Unnamed",
                                description = it["description"] as? String,
                                created_at = it["created_at"] as? String,
                                updated_at = it["updated_at"] as? String
                            )
                        }
                    } ?: emptyList()

                    categoryMap.clear()
                    categoryMap.putAll(
                        categories.associate { (it.category_id ?: 0) to (it.name.ifEmpty { "Unnamed" }) }
                    )

                    Log.d("InsightDebug", "✅ Category map loaded: $categoryMap")

                    loadInsights(dm.currentTab, dm.currentYear, dm.currentMonth, dm.currentWeek)

                } catch (ex: Exception) {
                    Log.e("InsightDebug", "❌ Failed to parse categories: ${ex.message}")
                    loadInsights(dm.currentTab, dm.currentYear, dm.currentMonth, dm.currentWeek)
                }
            }

            override fun onFailure(call: Call<ResultDTO<Any>>, t: Throwable) {
                Log.e("InsightDebug", "⚠️ Failed to load categories: ${t.message}")
                loadInsights(dm.currentTab, dm.currentYear, dm.currentMonth, dm.currentWeek)
            }
        })
    }


    private fun loadInsights(tab: String, year: Int, month: Int, week: Int) {
        val prefs = requireContext().getSharedPreferences("kaihelper_prefs", Context.MODE_PRIVATE)
        val userId = prefs.getInt("user_id", 1)

        expenseService.getExpensesByUser(userId)
            .enqueue(object : Callback<ResultDTO<List<ExpenseDTO>>> {
                override fun onResponse(
                    call: Call<ResultDTO<List<ExpenseDTO>>>,
                    response: Response<ResultDTO<List<ExpenseDTO>>>
                ) {
                    val expenses = response.body()?.data ?: emptyList()
                    val filteredExpenses = filterExpensesByDate(expenses, tab, year, month, week)

                    if (filteredExpenses.isEmpty()) {
                        showEmptyCharts("No expenses found for $tab")
                        return
                    }

                    Log.d("InsightDebug", "✅ Filtered ${filteredExpenses.size} expenses for $tab")
                    loadAllGroceries(filteredExpenses)
                }

                override fun onFailure(call: Call<ResultDTO<List<ExpenseDTO>>>, t: Throwable) {
                    showEmptyCharts("Error: ${t.message}")
                }
            })
    }

    private fun loadAllGroceries(filteredExpenses: List<ExpenseDTO>) {
        val allGroceries = mutableListOf<GroceryDTO>()
        var remaining = filteredExpenses.size

        if (remaining == 0) {
            showEmptyCharts("No data to show")
            return
        }

        filteredExpenses.forEach { expense ->
            groceryService.getGroceriesByExpense(expense.expense_id)
                .enqueue(object : Callback<ResultDTO<List<GroceryDTO>>> {
                    override fun onResponse(
                        call: Call<ResultDTO<List<GroceryDTO>>>,
                        response: Response<ResultDTO<List<GroceryDTO>>>
                    ) {
                        if (response.isSuccessful && response.body()?.success == true) {
                            val groceries = response.body()?.data ?: emptyList()
                            allGroceries.addAll(groceries)
                            Log.d("InsightDebug", "Expense ${expense.expense_id}: Loaded ${groceries.size} groceries")
                        } else {
                            Log.w("InsightDebug", "Expense ${expense.expense_id}: No groceries")
                        }

                        remaining--
                        if (remaining == 0) updateCharts(allGroceries)
                    }

                    override fun onFailure(call: Call<ResultDTO<List<GroceryDTO>>>, t: Throwable) {
                        remaining--
                        Log.e("InsightDebug", "Failed to load groceries for expense ${expense.expense_id}: ${t.message}")
                        if (remaining == 0) updateCharts(allGroceries)
                    }
                })
        }
    }

    private fun updateCharts(groceries: List<GroceryDTO>) {
        if (groceries.isEmpty()) {
            showEmptyCharts("No groceries found for this range")
            return
        }

        // ✅ Group by category_id and calculate total cost
        val categoryTotals = groceries
            .filter { it.category_id != null && it.category_id != 0 }
            .groupBy { it.category_id!! }
            .mapValues { (_, gList) -> gList.sumOf { it.total_cost ?: 0.0 } }

        Log.d("InsightDebug", "📊 Category totals (IDs): $categoryTotals")

        val categoryEntries = categoryTotals.map { (id, total) ->
            val name = categoryMap[id]?.ifBlank { "Unnamed" } ?: "Unnamed"
            Log.d("InsightDebug", "➡️ Category $id resolved as '$name'")
            PieEntry(total.toFloat(), name)
        }

        val localizationTotals = groceries.groupBy { if (it.local == true) "Local" else "Foreign" }
            .mapValues { (_, gList) -> gList.sumOf { it.total_cost ?: 0.0 } }

        Log.d("InsightDebug", "🌏 Localization totals: $localizationTotals")

        val localizationEntries = localizationTotals.map { (label, total) ->
            PieEntry(total.toFloat(), label)
        }

        setupPieChart(chartByCategory, categoryEntries)
        setupPieChart(chartByLocalization, localizationEntries)
    }

    private fun filterExpensesByDate(
        list: List<ExpenseDTO>,
        tab: String,
        year: Int,
        month: Int,
        week: Int
    ): List<ExpenseDTO> {
        val cal = Calendar.getInstance()
        return list.filter { e ->
            val dateStr = e.expense_date ?: return@filter false
            val expenseDate = try { sdf.parse(dateStr) } catch (_: Exception) { return@filter false } ?: return@filter false
            cal.time = expenseDate

            when (tab) {
                "Year" -> cal.get(Calendar.YEAR) == year
                "Month" -> cal.get(Calendar.YEAR) == year && cal.get(Calendar.MONTH) == month
                "Week" -> {
                    val targetCal = Calendar.getInstance().apply {
                        clear()
                        set(Calendar.YEAR, year)
                        set(Calendar.WEEK_OF_YEAR, week)
                        firstDayOfWeek = Calendar.MONDAY
                    }
                    val startOfWeek = targetCal.time
                    targetCal.add(Calendar.DAY_OF_WEEK, 6)
                    val endOfWeek = targetCal.time
                    expenseDate in startOfWeek..endOfWeek
                }
                else -> true
            }
        }
    }

    private fun setupPieChart(chart: PieChart, entries: List<PieEntry>) {
        val dataSet = PieDataSet(entries, "")
        dataSet.colors = ColorTemplate.MATERIAL_COLORS.toList()
        dataSet.valueTextColor = android.graphics.Color.WHITE
        dataSet.valueTextSize = 14f

        val data = PieData(dataSet)
        chart.data = data
        chart.description.isEnabled = false
        chart.legend.textColor = android.graphics.Color.LTGRAY
        chart.animateY(800)
        chart.invalidate()
    }

    private fun showEmptyCharts(message: String) {
        chartByCategory.clear()
        chartByLocalization.clear()
        chartByCategory.invalidate()
        chartByLocalization.invalidate()
        Toast.makeText(requireContext(), message, Toast.LENGTH_SHORT).show()
    }
}
