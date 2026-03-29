package com.fithub.nativeandroid.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fithub.nativeandroid.data.FitHubApiClient
import com.fithub.nativeandroid.data.HealthPreview
import com.fithub.nativeandroid.health.HealthConnectManager
import com.fithub.nativeandroid.health.XiaomiSyncProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

data class MainUiState(
    val serverUrl: String = "https://fithub-app-1btg.onrender.com",
    val phone: String = "",
    val role: String = "enthusiast",
    val sessionId: String = UUID.randomUUID().toString(),
    val profileId: String = "",
    val status: String = "连接 Health Connect 后即可把真实训练同步到 FitHub。",
    val preview: HealthPreview? = null,
    val isBusy: Boolean = false,
)

class MainViewModel(
    private val healthManager: HealthConnectManager,
    private val xiaomiSyncProvider: XiaomiSyncProvider = XiaomiSyncProvider(),
) : ViewModel() {
    private val _uiState = MutableStateFlow(
        MainUiState(status = healthManager.availabilitySummary())
    )
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    fun updateServerUrl(value: String) = update { copy(serverUrl = value) }
    fun updatePhone(value: String) = update { copy(phone = value) }
    fun updateRole(value: String) = update { copy(role = value) }
    fun updateProfileId(value: String) = update { copy(profileId = value) }

    fun loadPreview() {
        viewModelScope.launch {
            update { copy(isBusy = true, status = "正在读取 Health Connect 数据...") }
            runCatching { healthManager.loadPreview() }
                .onSuccess { preview ->
                    update { copy(preview = preview, isBusy = false, status = "已读取 Health Connect，可同步到 FitHub。") }
                }
                .onFailure { error ->
                    update { copy(isBusy = false, status = error.message ?: "Health Connect 读取失败。") }
                }
        }
    }

    fun syncToFitHub() {
        viewModelScope.launch {
            val state = _uiState.value
            if (state.profileId.isBlank()) {
                update { copy(status = "请先填入训练者 profileId，再同步。") }
                return@launch
            }

            update { copy(isBusy = true, status = "正在同步到 FitHub...") }
            runCatching {
                val payload = healthManager.buildSyncPayload(state.sessionId, state.profileId)
                FitHubApiClient(state.serverUrl).syncHealth(payload)
            }
                .onSuccess {
                    update { copy(isBusy = false, status = "Health Connect 数据已同步到 FitHub。") }
                }
                .onFailure { error ->
                    update { copy(isBusy = false, status = error.message ?: "同步失败。") }
                }
        }
    }

    fun showXiaomiMessage() {
        update { copy(status = xiaomiSyncProvider.statusMessage()) }
    }

    private fun update(transform: MainUiState.() -> MainUiState) {
        _uiState.value = _uiState.value.transform()
    }
}
