package at.ac.htlleonding.danceable.viewmodel

import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import at.ac.htlleonding.danceable.data.remote.DanceApiService
import at.ac.htlleonding.danceable.data.remote.RetrofitInstance
import io.mockk.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ViewModelTest {

    private val testDispatcher = UnconfinedTestDispatcher()
    private lateinit var viewModel: ViewModel
    private val apiService = mockk<DanceApiService>()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        mockkObject(RetrofitInstance)
        every { RetrofitInstance.api } returns apiService
        coEvery { apiService.getDances() } returns emptyList()
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    @Test
    fun `initial state is correct`() = runTest {
        viewModel = ViewModel()
        assertFalse(viewModel.isSheetOpen.value)
        assertTrue(viewModel.dances.value.isEmpty())
        assertTrue(viewModel.predictions.value.isEmpty())
    }

    @Test
    fun `openSheet sets isSheetOpen to true`() = runTest {
        viewModel = ViewModel()
        viewModel.openSheet()
        assertTrue(viewModel.isSheetOpen.value)
    }

    @Test
    fun `closeSheet sets isSheetOpen to false`() = runTest {
        viewModel = ViewModel()
        viewModel.openSheet()
        viewModel.closeSheet()
        assertFalse(viewModel.isSheetOpen.value)
    }

    @Test
    fun `updatePrediction updates predictions and opens sheet`() = runTest {
        viewModel = ViewModel()
        val predictions = listOf(Prediction(1, 0.9f, "Fast"))
        viewModel.updatePrediction(predictions)
        assertEquals(predictions, viewModel.predictions.value)
        assertTrue(viewModel.isSheetOpen.value)
    }

    @Test
    fun `getDanceById returns correct dance`() = runTest {
        val danceList = listOf(
            Dance(1, "Waltz", 84, 90, "Desc 1"),
            Dance(2, "Tango", 120, 130, "Desc 2")
        )
        coEvery { apiService.getDances() } returns danceList
        
        viewModel = ViewModel()
        // Wait for fetchDances to complete (UnconfinedTestDispatcher helps here)
        
        val dance = viewModel.getDanceById(1)
        assertEquals("Waltz", dance?.name)
        
        val nullDance = viewModel.getDanceById(3)
        assertNull(nullDance)
    }

    @Test
    fun `fetchDances updates dances state flow`() = runTest {
        val danceList = listOf(Dance(1, "Waltz", 84, 90, "Desc"))
        coEvery { apiService.getDances() } returns danceList

        viewModel = ViewModel()

        assertEquals(danceList, viewModel.dances.value)
    }

    @Test
    fun `fetchDances handles error`() = runTest {
        coEvery { apiService.getDances() } throws Exception("Network error")

        viewModel = ViewModel()

        assertTrue(viewModel.dances.value.isEmpty())
    }
}