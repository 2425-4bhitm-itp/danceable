package at.ac.htlleonding.danceable.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import at.ac.htlleonding.danceable.data.model.Dance
import at.ac.htlleonding.danceable.data.model.Prediction
import at.ac.htlleonding.danceable.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class ViewModel : ViewModel() {
    private val _dances = MutableStateFlow<List<Dance>>(emptyList())
    private val _predictions = MutableStateFlow<List<Prediction>>(emptyList())

    val dances: StateFlow<List<Dance>> get() = _dances
    val predictions: StateFlow<List<Prediction>> get() = _predictions

    init{
        fetchDances()
    }

    private fun fetchDances(){
        viewModelScope.launch{
            try{
                val response = RetrofitInstance.api.getDances()
                _dances.value = response;
            } catch(e:Exception){
                e.printStackTrace()
            }
        }
    }
}