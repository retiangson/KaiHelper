package nz.yoobee.kaihelper.ui

import android.Manifest
import android.app.AlertDialog
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.core.view.GestureDetectorCompat
import androidx.fragment.app.Fragment
import com.canhub.cropper.CropImageContract
import com.canhub.cropper.CropImageContractOptions
import com.canhub.cropper.CropImageOptions
import com.canhub.cropper.CropImageView
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.tabs.TabLayout
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.ReceiptService
import nz.yoobee.kaihelper.core.DateManager
import nz.yoobee.kaihelper.databinding.ActivityMainBinding
import nz.yoobee.kaihelper.ui.fragments.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import kotlin.math.abs

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var gestureDetector: GestureDetectorCompat
    private var loadingDialog: AlertDialog? = null
    private var photoUri: Uri? = null

    // ✅ Use only the global DateManager
    private val dm = DateManager

    // --------------------------------------------
    // Camera, Gallery, Crop Launchers
    // --------------------------------------------
    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) openCamera() else Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show()
        }

    private val pickImageLauncher =
        registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
            uri?.let { cropImageLauncher.launch(CropImageContractOptions(it, CropImageOptions())) }
        }

    private val takePictureLauncher =
        registerForActivityResult(ActivityResultContracts.TakePicture()) { success ->
            if (success && photoUri != null) {
                val capturedFile = copyUriToFile(photoUri!!)
                if (capturedFile != null && capturedFile.exists()) {
                    cropImageLauncher.launch(
                        CropImageContractOptions(
                            uri = Uri.fromFile(capturedFile),
                            cropImageOptions = CropImageOptions().apply {
                                fixAspectRatio = false
                                cropMenuCropButtonTitle = "Done"
                                guidelines = CropImageView.Guidelines.ON
                                activityMenuIconColor = ContextCompat.getColor(this@MainActivity, R.color.white)
                            }
                        )
                    )
                } else {
                    Toast.makeText(this, "❌ Failed to prepare image", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "❌ Capture canceled", Toast.LENGTH_SHORT).show()
            }
        }

    private val cropImageLauncher = registerForActivityResult(CropImageContract()) { result ->
        if (result.isSuccessful) {
            val file = result.uriContent?.let { copyUriToFile(it) }
            val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
            val userId = prefs.getInt("user_id", 1)
            if (file != null) uploadReceipt(userId, file)
        }
    }

    // --------------------------------------------
    // Lifecycle
    // --------------------------------------------
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Load saved date state from prefs
        val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
        dm.currentYear = prefs.getInt("current_year", dm.currentYear)
        dm.currentMonth = prefs.getInt("current_month", dm.currentMonth)
        dm.currentWeek = prefs.getInt("current_week", dm.currentWeek)
        dm.currentTab = prefs.getString("current_tab", dm.currentTab) ?: "Year"

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val topAppBar = findViewById<MaterialToolbar>(R.id.topAppBar)
        topAppBar.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                R.id.action_add -> { Toast.makeText(this, "Add clicked", Toast.LENGTH_SHORT).show(); true }
                R.id.action_menu -> { Toast.makeText(this, "Menu clicked", Toast.LENGTH_SHORT).show(); true }
                else -> false
            }
        }

        gestureDetector = GestureDetectorCompat(this, SwipeGestureListener())

        binding.rootLayout.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
            false
        }

        setupTabs()
        setupBottomNav()

        if (savedInstanceState == null) {
            showFragment(OverviewFragment())
            highlightSelectedIcon(binding.root.findViewById(R.id.iconOverview))
            updateToolbarTitle("Expenses")
            notifyAllFragments()
        }
    }

    // --------------------------------------------
    // Tabs (shared across fragments)
    // --------------------------------------------
    private fun setupTabs() {
        binding.tabFilter.apply {
            addTab(newTab().setText("Year"))
            addTab(newTab().setText("Month"))
            addTab(newTab().setText("Week"))
            selectTab(when (dm.currentTab) {
                "Month" -> getTabAt(1)
                "Week" -> getTabAt(2)
                else -> getTabAt(0)
            })
        }

        binding.tabFilter.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                dm.currentTab = tab?.text.toString()
                notifyAllFragments()
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
    }

    // --------------------------------------------
    // Bottom Navigation
    // --------------------------------------------
    private fun setupBottomNav() {
        val iconFunding: ImageView = findViewById(R.id.iconFunding)
        val iconTransaction: ImageView = findViewById(R.id.iconTransaction)
        val iconCamera: ImageView = findViewById(R.id.iconCamera)
        val iconInsight: ImageView = findViewById(R.id.iconInsight)
        val iconOverview: ImageView = findViewById(R.id.iconOverview)

        findViewById<View>(R.id.navFunding).setOnClickListener {
            highlightSelectedIcon(iconFunding)
            updateToolbarTitle("Funding")
            showFragment(FundingFragment())
            notifyAllFragments()
        }

        findViewById<View>(R.id.navTransaction).setOnClickListener {
            highlightSelectedIcon(iconTransaction)
            updateToolbarTitle("Transactions")
            showFragment(TransactionFragment())
            notifyAllFragments()
        }

        findViewById<View>(R.id.navUpload).setOnClickListener {
            highlightSelectedIcon(iconCamera)
            updateToolbarTitle("Upload")
            showUploadDialog()
            notifyAllFragments()
        }

        findViewById<View>(R.id.navInsight).setOnClickListener {
            highlightSelectedIcon(iconInsight)
            updateToolbarTitle("Insights")
            showFragment(InsightFragment())
            notifyAllFragments()
        }

        findViewById<View>(R.id.navOverview).setOnClickListener {
            highlightSelectedIcon(iconOverview)
            updateToolbarTitle("Expenses")
            showFragment(OverviewFragment())
            notifyAllFragments()
        }
    }

    private fun highlightSelectedIcon(selectedIcon: ImageView) {
        val activeColor = ContextCompat.getColor(this, R.color.teal_200)
        val inactiveColor = ContextCompat.getColor(this, R.color.gray_400)

        val pairs = listOf(
            R.id.iconFunding to R.id.labelFunding,
            R.id.iconTransaction to R.id.labelTransaction,
            R.id.iconCamera to R.id.labelUpload,
            R.id.iconInsight to R.id.labelInsight,
            R.id.iconOverview to R.id.labelOverview
        )

        pairs.forEach { (iconId, labelId) ->
            val icon = findViewById<ImageView>(iconId)
            val label = findViewById<TextView>(labelId)
            val isActive = icon == selectedIcon
            icon.setColorFilter(if (isActive) activeColor else inactiveColor)
            label.setTextColor(if (isActive) activeColor else inactiveColor)
        }
    }

    fun updateToolbarTitle(title: String) {
        findViewById<TextView?>(R.id.tvToolbarTitle)?.text = title.uppercase()
    }

    fun attachSwipeTo(view: View) {
        view.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
            false
        }
    }

    // --------------------------------------------
    // Fragment Navigation
    // --------------------------------------------
    private fun showFragment(fragment: Fragment, animateInFromLeft: Boolean? = null) {
        val transaction = supportFragmentManager.beginTransaction()
        when (animateInFromLeft) {
            true -> transaction.setCustomAnimations(R.anim.slide_in_left, R.anim.slide_out_right)
            false -> transaction.setCustomAnimations(R.anim.slide_in_right, R.anim.slide_out_left)
            else -> transaction.setCustomAnimations(android.R.anim.fade_in, android.R.anim.fade_out)
        }
        transaction.replace(R.id.fragmentContainer, fragment)
            .addToBackStack(fragment::class.java.simpleName)
            .commitAllowingStateLoss()
    }

    override fun onBackPressed() {
        if (supportFragmentManager.backStackEntryCount > 1) {
            supportFragmentManager.popBackStack()
        } else {
            super.onBackPressed()
        }
    }

    // --------------------------------------------
    // Upload Helpers
    // --------------------------------------------
    private fun openCamera() {
        val imageFile = File.createTempFile("receipt_", ".jpg", cacheDir)
        photoUri = FileProvider.getUriForFile(
            this,
            "${applicationContext.packageName}.provider",
            imageFile
        )
        photoUri?.let { takePictureLauncher.launch(it) }
    }

    private fun showUploadDialog() {
        AlertDialog.Builder(this)
            .setTitle("Upload Receipt")
            .setItems(arrayOf("Take Photo", "Choose from Gallery")) { _, which ->
                when (which) {
                    0 -> {
                        val hasPermission = ContextCompat.checkSelfPermission(
                            this, Manifest.permission.CAMERA
                        ) == PackageManager.PERMISSION_GRANTED
                        if (hasPermission) openCamera()
                        else requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                    }
                    1 -> pickImageLauncher.launch("image/*")
                }
            }.show()
    }

    private fun uploadReceipt(userId: Int, imageFile: File) {
        showLoading()
        val receiptService = ApiClient.retrofit.create(ReceiptService::class.java)
        val userIdBody = RequestBody.create("text/plain".toMediaTypeOrNull(), userId.toString())
        val requestFile = RequestBody.create("image/jpeg".toMediaTypeOrNull(), imageFile)
        val multipartBody = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)

        receiptService.uploadReceipt(userIdBody, multipartBody)
            .enqueue(object : Callback<ResponseBody> {
                override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                    hideLoading()
                    Toast.makeText(
                        this@MainActivity,
                        if (response.isSuccessful) "✅ Upload success!" else "⚠️ Upload failed",
                        Toast.LENGTH_SHORT
                    ).show()
                }

                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    hideLoading()
                    Toast.makeText(
                        this@MainActivity,
                        "❌ Network error: ${t.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            })
    }

    private fun copyUriToFile(uri: Uri): File? {
        return try {
            val input = contentResolver.openInputStream(uri) ?: return null
            val tempFile = File.createTempFile("upload_", ".jpg", cacheDir)
            tempFile.outputStream().use { output -> input.copyTo(output) }
            tempFile
        } catch (e: Exception) {
            Log.e("Upload", "Copy failed: ${e.message}")
            null
        }
    }

    // --------------------------------------------
    // Loading UI
    // --------------------------------------------
    private fun showLoading(message: String = "Uploading...") {
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

    // --------------------------------------------
    // Tabs notify all fragments
    // --------------------------------------------
    private fun notifyAllFragments() {
        val fragments = supportFragmentManager.fragments
        fragments.forEach { fragment ->
            if (fragment is DateFilterable) {
                fragment.onDateFilterChanged(
                    dm.currentTab,
                    dm.currentYear,
                    dm.currentMonth,
                    dm.currentWeek
                )
            }
        }

        updateGlobalDateIndicator()
        // ✅ Persist date after updates
        val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
        prefs.edit()
            .putInt("current_year", dm.currentYear)
            .putInt("current_month", dm.currentMonth)
            .putInt("current_week", dm.currentWeek)
            .putString("current_tab", dm.currentTab)
            .apply()
    }

    fun updateGlobalDateIndicator() {
        val indicator = findViewById<TextView?>(R.id.tvCoverage) ?: return

        val label = when (DateManager.currentTab) {
            "Year" -> "Year ${DateManager.currentYear}"

            "Month" -> {
                val cal = java.util.Calendar.getInstance().apply {
                    set(java.util.Calendar.YEAR, DateManager.currentYear)
                    set(java.util.Calendar.MONTH, DateManager.currentMonth)
                }
                val monthName = java.text.SimpleDateFormat("MMMM", java.util.Locale.getDefault()).format(cal.time)
                "$monthName ${DateManager.currentYear}"
            }

            "Week" -> {
                // ✅ Compute actual start and end of that week
                val weekCal = java.util.Calendar.getInstance().apply {
                    clear()
                    set(java.util.Calendar.YEAR, DateManager.currentYear)
                    set(java.util.Calendar.WEEK_OF_YEAR, DateManager.currentWeek)
                    firstDayOfWeek = java.util.Calendar.MONDAY
                }

                val startOfWeek: java.util.Date = weekCal.time
                weekCal.add(java.util.Calendar.DAY_OF_WEEK, 6)
                val endOfWeek: java.util.Date = weekCal.time

                val fmt = java.text.SimpleDateFormat("MMM d", java.util.Locale.getDefault())
                val startLabel = fmt.format(startOfWeek)
                val endLabel = fmt.format(endOfWeek)
                "$startLabel – $endLabel ${DateManager.currentYear}"
            }

            else -> ""
        }

        indicator.text = label
    }

    // --------------------------------------------
    // Swipe Gestures
    // --------------------------------------------
    private inner class SwipeGestureListener :
        android.view.GestureDetector.SimpleOnGestureListener() {
        private val SWIPE_THRESHOLD = 100
        private val SWIPE_VELOCITY_THRESHOLD = 100

        override fun onFling(e1: MotionEvent?, e2: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
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
        dm.next()
        animateSwipe(-1)
        notifyAllFragments()
    }

    private fun onSwipeRight() {
        dm.previous()
        animateSwipe(1)
        notifyAllFragments()
    }

    private fun animateSwipe(direction: Int) {
        val container = findViewById<View>(R.id.pageContainer)
        val distance = container.width.toFloat() * direction
        container.animate()
            .translationX(distance)
            .setDuration(200)
            .withEndAction {
                container.translationX = -distance
                notifyAllFragments()
                container.animate().translationX(0f).setDuration(200).start()
            }.start()
    }
}
