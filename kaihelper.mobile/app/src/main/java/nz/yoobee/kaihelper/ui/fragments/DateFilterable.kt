package nz.yoobee.kaihelper.ui.fragments

interface DateFilterable {
    fun onDateFilterChanged(tab: String, year: Int, month: Int, week: Int)
}
