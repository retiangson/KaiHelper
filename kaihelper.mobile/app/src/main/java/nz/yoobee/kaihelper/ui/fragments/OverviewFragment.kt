package nz.yoobee.kaihelper.ui.fragments

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.ExpenseService
import nz.yoobee.kaihelper.core.DateManager
import nz.yoobee.kaihelper.databinding.FragmentOverviewBinding
import nz.yoobee.kaihelper.models.ExpenseDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.ui.ExpenseDetailActivity
import nz.yoobee.kaihelper.ui.MainActivity
import nz.yoobee.kaihelper.ui.dashboard.ExpenseAdapter
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.*
import android.widget.TextView

class OverviewFragment : Fragment(R.layout.fragment_overview), DateFilterable {

    private lateinit var binding: FragmentOverviewBinding
    private lateinit var adapter: ExpenseAdapter
    private val expenseService = ApiClient.retrofit.create(ExpenseService::class.java)
    private val dm = DateManager  // ✅ Use global DateManager

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentOverviewBinding.bind(view)

        adapter = ExpenseAdapter { expense ->
            val i = Intent(requireContext(), ExpenseDetailActivity::class.java)
            i.putExtra("expense_id", expense.expense_id)
            startActivity(i)
        }
        binding.rvExpenses.layoutManager = LinearLayoutManager(requireContext())
        binding.rvExpenses.adapter = adapter

        // Pull-to-refresh
        binding.swipeRefresh.setOnRefreshListener {
            loadExpenses(dm.currentTab, dm.currentYear, dm.currentMonth, dm.currentWeek)
        }

        // Enable swipe gestures (left/right) handled by MainActivity
        binding.rvExpenses.setOnTouchListener { v, ev ->
            when (ev?.actionMasked) {
                MotionEvent.ACTION_MOVE -> {
                    val hx = if (ev.historySize > 0) ev.getHistoricalX(0) else ev.x
                    val hy = if (ev.historySize > 0) ev.getHistoricalY(0) else ev.y
                    val dx = ev.x - hx
                    val dy = ev.y - hy
                    binding.swipeRefresh.isEnabled = kotlin.math.abs(dy) > kotlin.math.abs(dx)
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> binding.swipeRefresh.isEnabled = true
            }
            (requireActivity() as? MainActivity)?.attachSwipeTo(v)
            false
        }

        (requireActivity() as? MainActivity)?.attachSwipeTo(binding.root)

        // ✅ Initial load uses global date
        loadExpenses(dm.currentTab, dm.currentYear, dm.currentMonth, dm.currentWeek)
    }

    override fun onDateFilterChanged(tab: String, year: Int, month: Int, week: Int) {
        loadExpenses(tab, year, month, week)
    }

    private fun loadExpenses(tab: String, year: Int, month: Int, week: Int) {
        val prefs = requireContext().getSharedPreferences("kaihelper_prefs", Context.MODE_PRIVATE)
        val userId = prefs.getInt("user_id", 1)
        binding.swipeRefresh.isRefreshing = true

        expenseService.getExpensesByUser(userId)
            .enqueue(object : Callback<ResultDTO<List<ExpenseDTO>>> {
                override fun onResponse(
                    call: Call<ResultDTO<List<ExpenseDTO>>>,
                    res: Response<ResultDTO<List<ExpenseDTO>>>
                ) {
                    binding.swipeRefresh.isRefreshing = false
                    val all = res.body()?.data ?: emptyList()
                    val filtered = filter(all, tab, year, month, week)
                    adapter.submitList(filtered)

                    // ✅ Update total spent dynamically
                    val totalSpent = filtered.sumOf { it.subtotal_amount ?: 0.0 }
                    (requireActivity().findViewById<TextView>(R.id.tvTotalSpent))
                        ?.text = String.format("$%.2f", totalSpent)

                    binding.tvEmptyState.visibility =
                        if (filtered.isEmpty()) View.VISIBLE else View.GONE

                    updateCoverageText(tab, year, month, week)
                }

                override fun onFailure(call: Call<ResultDTO<List<ExpenseDTO>>>, t: Throwable) {
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(requireContext(), "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun filter(
        list: List<ExpenseDTO>,
        tab: String,
        year: Int,
        month: Int,
        week: Int
    ): List<ExpenseDTO> {
        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val cal = Calendar.getInstance()

        return list.filter { e ->
            val dateStr = e.expense_date ?: return@filter false
            val expenseDate = try { sdf.parse(dateStr) } catch (_: Exception) { return@filter false } ?: return@filter false
            cal.time = expenseDate

            when (tab) {
                "Year" ->
                    cal.get(Calendar.YEAR) == year

                "Month" ->
                    cal.get(Calendar.YEAR) == year &&
                            cal.get(Calendar.MONTH) == month

                "Week" -> {
                    // ✅ Compute start and end of the *actual week of the year*
                    val targetCal = Calendar.getInstance().apply {
                        clear()
                        set(Calendar.YEAR, year)
                        set(Calendar.WEEK_OF_YEAR, week)
                        firstDayOfWeek = Calendar.MONDAY
                    }
                    val startOfWeek = targetCal.time
                    targetCal.add(Calendar.DAY_OF_WEEK, 6)
                    val endOfWeek = targetCal.time
                    Log.d("WeekFilter", "Filtering week $week of $year → $startOfWeek to $endOfWeek, expense=${e.expense_date}")
                    // ✅ Keep expenses that fall within that week
                    expenseDate in startOfWeek..endOfWeek
                }

                else -> true
            }
        }
    }

    private fun updateCoverageText(tab: String, year: Int, month: Int, week: Int) {
        (requireActivity() as? MainActivity)?.updateGlobalDateIndicator()
    }
}
