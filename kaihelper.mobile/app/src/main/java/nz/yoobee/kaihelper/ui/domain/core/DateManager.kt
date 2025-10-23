package nz.yoobee.kaihelper.core

import java.util.Calendar

/**
 * Global singleton for managing the shared date state across fragments.
 * Keeps Year/Month/Week synchronized with real calendar progression.
 */
object DateManager {
    var currentTab: String = "Year"
    var currentYear: Int = Calendar.getInstance().get(Calendar.YEAR)
    var currentMonth: Int = Calendar.getInstance().get(Calendar.MONTH)
    var currentWeek: Int = Calendar.getInstance().get(Calendar.WEEK_OF_YEAR)

    /** Move forward based on current tab */
    fun next() {
        val cal = getCalendar()
        when (currentTab) {
            "Year" -> cal.add(Calendar.YEAR, 1)
            "Month" -> cal.add(Calendar.MONTH, 1)
            "Week" -> cal.add(Calendar.WEEK_OF_YEAR, 1)
        }
        updateFromCalendar(cal)
    }

    /** Move backward based on current tab */
    fun previous() {
        val cal = getCalendar()
        when (currentTab) {
            "Year" -> cal.add(Calendar.YEAR, -1)
            "Month" -> cal.add(Calendar.MONTH, -1)
            "Week" -> cal.add(Calendar.WEEK_OF_YEAR, -1)
        }
        updateFromCalendar(cal)
    }

    /** Create a Calendar set to the current date context */
    private fun getCalendar(): Calendar {
        return Calendar.getInstance().apply {
            clear()
            set(Calendar.YEAR, currentYear)
            set(Calendar.WEEK_OF_YEAR, currentWeek)
            // Month recalculated automatically when updating from calendar
        }
    }

    /** Sync currentYear, currentMonth, currentWeek from the given Calendar */
    private fun updateFromCalendar(cal: Calendar) {
        currentYear = cal.get(Calendar.YEAR)
        currentMonth = cal.get(Calendar.MONTH)
        currentWeek = cal.get(Calendar.WEEK_OF_YEAR)
    }
}
