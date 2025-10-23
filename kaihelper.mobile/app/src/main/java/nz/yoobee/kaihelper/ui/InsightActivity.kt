package nz.yoobee.kaihelper.ui

import android.os.Bundle
import android.view.MotionEvent
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GestureDetectorCompat
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.data.PieData
import com.github.mikephil.charting.data.PieDataSet
import com.github.mikephil.charting.data.PieEntry
import com.github.mikephil.charting.utils.ColorTemplate
import com.google.android.material.tabs.TabLayout
import nz.yoobee.kaihelper.databinding.ActivityInsightBinding
import java.util.Calendar
import kotlin.math.abs
import android.view.GestureDetector
import androidx.core.content.ContextCompat
import nz.yoobee.kaihelper.R
import android.widget.ImageView
import android.widget.LinearLayout

class InsightActivity : AppCompatActivity() {

    private lateinit var binding: ActivityInsightBinding
    private lateinit var gestureDetector: GestureDetectorCompat

    private var currentTab = "Year"
    private var currentYear = Calendar.getInstance().get(Calendar.YEAR)
    private var currentMonth = Calendar.getInstance().get(Calendar.MONTH)
    private var currentWeek = Calendar.getInstance().get(Calendar.WEEK_OF_YEAR)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityInsightBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Get the included bottom bar root
        val bottomBar = findViewById<LinearLayout>(R.id.bottomActionBar)

        // ✅ Overview icon → return to MainActivity
        bottomBar.findViewById<ImageView>(R.id.iconOverview).setOnClickListener {
            finish() // closes InsightActivity and returns to MainActivity
            overridePendingTransition(android.R.anim.slide_in_left, android.R.anim.slide_out_right)
        }

        // ✅ Highlight Insight icon as active
        bottomBar.findViewById<ImageView>(R.id.iconInsight)
            .setColorFilter(ContextCompat.getColor(this, R.color.teal_200))

        // ✅ Reset others
        bottomBar.findViewById<ImageView>(R.id.iconOverview).clearColorFilter()
        bottomBar.findViewById<ImageView>(R.id.iconFunding).clearColorFilter()
        bottomBar.findViewById<ImageView>(R.id.iconTransaction).clearColorFilter()
        bottomBar.findViewById<ImageView>(R.id.iconCamera).clearColorFilter()

        gestureDetector = GestureDetectorCompat(this, SwipeGestureListener())

        // Attach swipe gesture to whole page
        binding.insightRootLayout.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
            true
        }

        // Tabs setup
        binding.tabInsightFilter.addTab(binding.tabInsightFilter.newTab().setText("Year"))
        binding.tabInsightFilter.addTab(binding.tabInsightFilter.newTab().setText("Month"))
        binding.tabInsightFilter.addTab(binding.tabInsightFilter.newTab().setText("Week"))
        binding.tabInsightFilter.selectTab(binding.tabInsightFilter.getTabAt(0))

        binding.tabInsightFilter.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                currentTab = tab?.text.toString()
                loadInsights()
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })

        loadInsights()
    }

    // --- Gesture detector for swipe left/right
    private inner class SwipeGestureListener : GestureDetector.SimpleOnGestureListener() {
        private val SWIPE_THRESHOLD = 100
        private val SWIPE_VELOCITY_THRESHOLD = 100

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            if (e1 == null || e2 == null) return false
            val diffX = e2.x - e1.x
            val diffY = e2.y - e1.y

            if (abs(diffX) > abs(diffY) && abs(diffX) > SWIPE_THRESHOLD && abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffX > 0) onSwipeRight() else onSwipeLeft()
                return true
            }
            return false
        }
    }

    private fun onSwipeLeft() {
        when (currentTab) {
            "Year" -> currentYear++
            "Month" -> {
                currentMonth++
                if (currentMonth > 11) { currentMonth = 0; currentYear++ }
            }
            "Week" -> {
                currentWeek++
                if (currentWeek > 52) { currentWeek = 1; currentYear++ }
            }
        }
        loadInsights()
    }

    private fun onSwipeRight() {
        when (currentTab) {
            "Year" -> currentYear--
            "Month" -> {
                currentMonth--
                if (currentMonth < 0) { currentMonth = 11; currentYear-- }
            }
            "Week" -> {
                currentWeek--
                if (currentWeek < 1) { currentWeek = 52; currentYear-- }
            }
        }
        loadInsights()
    }

    // --- Load sample chart data (later connect to API)
    private fun loadInsights() {
        val categoryEntries = listOf(
            PieEntry(40f, "Groceries"),
            PieEntry(25f, "Dining"),
            PieEntry(15f, "Utilities"),
            PieEntry(10f, "Transport"),
            PieEntry(10f, "Others")
        )

        val localizationEntries = listOf(
            PieEntry(70f, "Local"),
            PieEntry(30f, "Foreign")
        )

        setupPieChart(binding.chartByCategory, categoryEntries)
        setupPieChart(binding.chartByLocalization, localizationEntries)

        Toast.makeText(this, "Showing $currentTab view ($currentYear)", Toast.LENGTH_SHORT).show()
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
}
