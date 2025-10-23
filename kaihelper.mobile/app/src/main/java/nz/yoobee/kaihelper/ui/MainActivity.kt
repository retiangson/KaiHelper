package nz.yoobee.kaihelper.ui

// --- Android standard library ---
import android.Manifest
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast
import android.view.View

// --- AndroidX & Jetpack ---
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.recyclerview.widget.LinearLayoutManager

// --- Third-party libraries ---
import com.canhub.cropper.CropImageContract
import com.canhub.cropper.CropImageContractOptions
import com.canhub.cropper.CropImageOptions
import com.canhub.cropper.CropImageView
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import com.google.android.material.tabs.TabLayout
import java.text.SimpleDateFormat
import java.util.Calendar
import kotlin.math.abs
import android.view.GestureDetector
import android.view.MotionEvent
import androidx.core.view.GestureDetectorCompat

// --- Java standard library ---
import java.io.File
import java.util.Locale

// --- Project-specific (KaiHelper) ---
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.ExpenseService
import nz.yoobee.kaihelper.api.ReceiptService
import nz.yoobee.kaihelper.databinding.ActivityMainBinding
import nz.yoobee.kaihelper.models.ExpenseDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.ui.ExpenseDetailActivity
import nz.yoobee.kaihelper.ui.dashboard.ExpenseAdapter

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: ExpenseAdapter
    private val expenseService = ApiClient.retrofit.create(ExpenseService::class.java)
    private var loadingDialog: AlertDialog? = null

    private var photoUri: Uri? = null

    private lateinit var gestureDetector: GestureDetectorCompat
    private var currentTab = "Year"
    private var currentYear = Calendar.getInstance().get(Calendar.YEAR)
    private var currentMonth = Calendar.getInstance().get(Calendar.MONTH)
    private var currentWeek = Calendar.getInstance().get(Calendar.WEEK_OF_YEAR)

    private val takePictureLauncher =
        registerForActivityResult(ActivityResultContracts.TakePicture()) { success: Boolean ->
            if (success && photoUri != null) {
                val capturedFile = copyUriToFile(photoUri!!)
                if (capturedFile != null && capturedFile.exists()) {
                    // ✂️ Launch cropper before uploading with updated API fields
                    cropImageLauncher.launch(
                        CropImageContractOptions(
                            uri = Uri.fromFile(capturedFile),
                            cropImageOptions = CropImageOptions().apply {
                                // ✅ Free-form crop area (no fixed aspect ratio)
                                fixAspectRatio = false
                                guidelines = CropImageView.Guidelines.ON
                                autoZoomEnabled = true
                                allowRotation = true
                                allowFlipping = false

                                // ✅ Show full crop toolbar UI
                                activityTitle = "Crop Receipt"
                                showCropOverlay = true
                                showProgressBar = true
                                allowCounterRotation = true
                                cropMenuCropButtonTitle = "Done"

                                // ✅ Toolbar & UI colors (visible Done/Cancel)
                                activityBackgroundColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_bg
                                )
                                activityMenuIconColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_text
                                )
                                // ✅ Optional: tweak crop frame colors
                                borderLineColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.white
                                )
                                borderCornerColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.white
                                )
                                guidelinesColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_text
                                )
                            }
                        )
                    )
                } else {
                    Toast.makeText(
                        this,
                        "❌ Failed to prepare image for cropping",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            } else {
                Toast.makeText(this, "❌ Capture canceled", Toast.LENGTH_SHORT).show()
            }
        }

    private val cropImageLauncher = registerForActivityResult(CropImageContract()) { result ->
        if (result.isSuccessful) {
            val croppedUri = result.uriContent
            croppedUri?.let {
                val file = copyUriToFile(it)
                if (file != null && file.exists()) {
                    val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
                    val userId = prefs.getInt("user_id", 1)
                    uploadReceipt(userId, file)
                }
            }
        } else {
            Toast.makeText(this, "Crop canceled", Toast.LENGTH_SHORT).show()
        }
    }

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted: Boolean ->
            if (granted) openCamera()
            else Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show()
        }

    private fun openCamera() {
        try {
            val imageFile = File.createTempFile("receipt_", ".jpg", cacheDir)
            photoUri = FileProvider.getUriForFile(
                this,
                "${applicationContext.packageName}.provider",
                imageFile
            )
            photoUri?.let { takePictureLauncher.launch(it) }
        } catch (e: Exception) {
            Toast.makeText(this, "Error launching camera: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    // ✅ This must be here — inside the class, but outside onCreate
    private fun uploadReceipt(userId: Int, imageFile: File) {
        showLoading()
        val receiptService = ApiClient.retrofit.create(ReceiptService::class.java)

        // Convert userId to RequestBody
        val userIdBody = RequestBody.create("text/plain".toMediaTypeOrNull(), userId.toString())

        // Convert file to RequestBody
        val requestFile = RequestBody.create("image/jpeg".toMediaTypeOrNull(), imageFile)

        // Wrap file as Multipart
        val multipartBody = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)

        // Make API call
        receiptService.uploadReceipt(userIdBody, multipartBody)
            .enqueue(object : Callback<ResponseBody> {
                override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                    hideLoading()
                    if (response.isSuccessful) {
                        Toast.makeText(applicationContext, "✅ Upload success!", Toast.LENGTH_SHORT).show()
                        loadExpenses()
                    } else {
                        Toast.makeText(applicationContext, "⚠️ Upload failed: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    hideLoading()
                    Log.e("Upload", "Network error", t)
                    Toast.makeText(applicationContext, "❌ Network error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)  // ✅ must come first before attaching any listeners

        binding.iconOverview.setColorFilter(ContextCompat.getColor(this, R.color.teal_200))
        // ✅ Reset others to default color
        binding.iconInsight.clearColorFilter()
        binding.iconFunding.clearColorFilter()
        binding.iconTransaction.clearColorFilter()
        binding.iconCamera.clearColorFilter()

        // ✅ Initialize gesture detector
        gestureDetector = GestureDetectorCompat(this, SwipeGestureListener())

        // ✅ Attach swipe listener to the root layout
        binding.rootLayout.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
                false // allow scroll & refresh to still work
            }

        // ✅ Setup Tabs (after setContentView)
        binding.tabFilter.addTab(binding.tabFilter.newTab().setText("Year"))
        binding.tabFilter.addTab(binding.tabFilter.newTab().setText("Month"))
        binding.tabFilter.addTab(binding.tabFilter.newTab().setText("Week"))
        binding.tabFilter.selectTab(binding.tabFilter.getTabAt(0))

        binding.tabFilter.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                currentTab = tab?.text.toString()
                loadExpenses()
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })

        // ✅ RecyclerView setup
        adapter = ExpenseAdapter { selectedExpense ->
            val intent = Intent(this, ExpenseDetailActivity::class.java) // ✅ requires import
            intent.putExtra("expense_id", selectedExpense.expense_id)
            startActivity(intent)
        }

        binding.rvExpenses.layoutManager = LinearLayoutManager(this)
        binding.rvExpenses.adapter = adapter
        // Divider removed for clean card look

        // ✅ Allow horizontal swipe detection even when swiping over the list
        binding.rvExpenses.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
            false // return false so vertical scroll and refresh still work
        }

        // ✅ Floating Action Button
        binding.iconFunding.setOnClickListener {
            Toast.makeText(this, "Funding tapped", Toast.LENGTH_SHORT).show()
        }

        binding.iconTransaction.setOnClickListener {
            Toast.makeText(this, "Transaction tapped", Toast.LENGTH_SHORT).show()
        }

        binding.iconCamera.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Upload Receipt")
                .setItems(arrayOf("Take Photo", "Choose from Gallery")) { _, which ->
                    when (which) {
                        0 -> { // Camera
                            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                                == PackageManager.PERMISSION_GRANTED
                            ) {
                                openCamera()
                            } else {
                                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                            }
                        }
                        1 -> pickImageLauncher.launch("image/*")
                    }
                }
                .show()
        }

        binding.iconInsight.setOnClickListener {
            val intent = Intent(this, InsightActivity::class.java)
            startActivity(intent)
            overridePendingTransition(android.R.anim.slide_in_left, android.R.anim.slide_out_right)
        }

        binding.iconOverview.setOnClickListener {
            // ✅ Just refresh the dashboard (no navigation)
            binding.rvExpenses.smoothScrollToPosition(0)
            Toast.makeText(this, "You’re on the Overview page", Toast.LENGTH_SHORT).show()
        }

        // ✅ Pull-to-refresh setup
        binding.swipeRefresh.setOnRefreshListener {
            loadExpenses()  // 🔹 reload data when dragged down
        }

        // ✅ Load expenses on startup
        loadExpenses()
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }


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

            if (abs(diffX) > abs(diffY) &&
                abs(diffX) > SWIPE_THRESHOLD &&
                abs(velocityX) > SWIPE_VELOCITY_THRESHOLD
            ) {
                if (diffX > 0) onSwipeRight() else onSwipeLeft()
                return true
            }
            return false
        }
    }

    private fun onSwipeLeft() {
        animateRecyclerView("left")
        when (currentTab) {
            "Year" -> currentYear++
            "Month" -> {
                currentMonth++
                if (currentMonth > 11) {
                    currentMonth = 0
                    currentYear++
                }
            }
            "Week" -> {
                currentWeek++
                if (currentWeek > 52) {
                    currentWeek = 1
                    currentYear++
                }
            }
        }
        loadExpenses()
    }

    private fun onSwipeRight() {
        animateRecyclerView("right")
        when (currentTab) {
            "Year" -> currentYear--
            "Month" -> {
                currentMonth--
                if (currentMonth < 0) {
                    currentMonth = 11
                    currentYear--
                }
            }
            "Week" -> {
                currentWeek--
                if (currentWeek < 1) {
                    currentWeek = 52
                    currentYear--
                }
            }
        }
        loadExpenses()
    }

    private fun animateRecyclerView(direction: String) {
        val distance = binding.rvExpenses.width.toFloat()
        val moveOut = if (direction == "left") -distance else distance
        val moveIn = if (direction == "left") distance else -distance

        // Animate only the list itself
        binding.rvExpenses.animate()
            .translationX(moveOut)
            .alpha(0f)
            .setDuration(220)
            .withEndAction {
                // Reset position and bring new list in
                binding.rvExpenses.translationX = moveIn
                binding.rvExpenses.animate()
                    .translationX(0f)
                    .alpha(1f)
                    .setDuration(220)
                    .start()
            }
            .start()

        // Optional subtle fade effect on empty state text
        if (binding.tvEmptyState.visibility == View.VISIBLE) {
            binding.tvEmptyState.animate()
                .translationX(moveOut * 0.5f)
                .alpha(0f)
                .setDuration(220)
                .withEndAction {
                    binding.tvEmptyState.translationX = moveIn * 0.5f
                    binding.tvEmptyState.animate()
                        .translationX(0f)
                        .alpha(1f)
                        .setDuration(220)
                        .start()
                }
                .start()
        }
    }

    private fun copyUriToFile(uri: Uri): File? {
        return try {
            val inputStream = contentResolver.openInputStream(uri) ?: return null
            val tempFile = File.createTempFile("upload_", ".jpg", cacheDir)
            tempFile.outputStream().use { output ->
                inputStream.copyTo(output)
            }
            tempFile
        } catch (e: Exception) {
            Log.e("Upload", "Failed to copy URI to file: ${e.message}", e)
            null
        }
    }

    private fun loadExpenses() {
        val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
        val userId = intent.getIntExtra("user_id", prefs.getInt("user_id", 0))
        Log.d("MainActivity", "Loaded userId=$userId")

        expenseService.getExpensesByUser(userId)
            .enqueue(object : Callback<ResultDTO<List<ExpenseDTO>>> {
                override fun onResponse(
                    call: Call<ResultDTO<List<ExpenseDTO>>>,
                    response: Response<ResultDTO<List<ExpenseDTO>>>
                ) {
                    binding.swipeRefresh.isRefreshing = false

                    if (response.isSuccessful) {
                        val result = response.body()
                        val allExpenses = result?.data ?: emptyList()

                        // ✅ Apply date filter based on current tab (Year / Month / Week)
                        val filteredList = allExpenses.filter { dto ->
                            val dateStr = dto.expense_date ?: return@filter false
                            try {
                                val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                                val cal = Calendar.getInstance().apply { time = sdf.parse(dateStr)!! }

                                when (currentTab) {
                                    "Year" -> cal.get(Calendar.YEAR) == currentYear
                                    "Month" -> cal.get(Calendar.YEAR) == currentYear &&
                                            cal.get(Calendar.MONTH) == currentMonth
                                    "Week" -> cal.get(Calendar.YEAR) == currentYear &&
                                            cal.get(Calendar.WEEK_OF_YEAR) == currentWeek
                                    else -> true
                                }
                            } catch (e: Exception) {
                                Log.e("Filter", "Invalid date: $dateStr", e)
                                false
                            }
                        }

                        if (filteredList.isEmpty()) {
                            binding.tvEmptyState.visibility = View.VISIBLE
                        } else {
                            binding.tvEmptyState.visibility = View.GONE
                        }

                        adapter.submitList(filteredList)
                        updateTotals(filteredList)

                        val scopeText = when (currentTab) {
                            "Year" -> "Year $currentYear"
                            "Month" -> {
                                val monthName = SimpleDateFormat("MMMM", Locale.getDefault())
                                    .format(Calendar.getInstance().apply { set(Calendar.MONTH, currentMonth) }.time)
                                "$monthName, $currentYear"
                            }
                            "Week" -> getFriendlyWeekText(currentWeek, currentYear)
                            else -> ""
                        }
                        binding.tvBudgetTitle.text = scopeText

                        Log.d("MainActivity", "Loaded ${filteredList.size} filtered expenses ($currentTab)")
                    } else {
                        Log.e("MainActivity", "Server error ${response.code()} — ${response.errorBody()?.string()}")
                    }
                }

                override fun onFailure(call: Call<ResultDTO<List<ExpenseDTO>>>, t: Throwable) {
                    binding.swipeRefresh.isRefreshing = false
                    Log.e("MainActivity", "Network error: ${t.message}", t)
                }
            })
    }

    /** 🔹 Compute and display total spent */
    private fun updateTotals(list: List<ExpenseDTO>) {
        val totalSpent = list.sumOf { it.amount }

        // ✅ Update greeting in top app bar
        binding.topAppBar.title = "Welcome, ${intent.getStringExtra("username") ?: "User"}"

        // ✅ Update totals
        binding.tvTotalSpent.text = "$%.2f".format(totalSpent)
        binding.tvTotalBudget.text = "$1000.00"  // Example static budget
    }

    private fun getFriendlyWeekText(weekOfYear: Int, year: Int): String {
        val calendar = Calendar.getInstance()
        calendar.clear()
        calendar.set(Calendar.YEAR, year)
        calendar.set(Calendar.WEEK_OF_YEAR, weekOfYear)
        calendar.set(Calendar.DAY_OF_WEEK, Calendar.MONDAY)

        // Get month name
        val monthName = SimpleDateFormat("MMMM", Locale.getDefault()).format(calendar.time)

        // Determine week ordinal (1st, 2nd, 3rd, 4th, 5th)
        val weekInMonth = calendar.get(Calendar.WEEK_OF_MONTH)
        val ordinal = when (weekInMonth) {
            1 -> "First"
            2 -> "Second"
            3 -> "Third"
            4 -> "Fourth"
            else -> "Fifth"
        }

        return "$ordinal week of $monthName, $year"
    }

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            cropImageLauncher.launch(
                CropImageContractOptions(it, CropImageOptions())
            )
        }
    }

    private fun showLoading(message: String = "Uploading receipt...") {
        if (loadingDialog == null) {
            loadingDialog = AlertDialog.Builder(this)
                .setCancelable(false)
                .setView(ProgressBar(this))
                .setMessage(message)
                .create()
        }
        loadingDialog?.show()
    }

    private fun hideLoading() {
        loadingDialog?.dismiss()
        loadingDialog = null
    }

}
