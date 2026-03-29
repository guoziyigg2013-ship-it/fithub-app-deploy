package com.fithub.nativeandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.health.connect.client.PermissionController
import com.fithub.nativeandroid.health.HealthConnectManager
import com.fithub.nativeandroid.ui.MainUiState
import com.fithub.nativeandroid.ui.MainViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val healthManager = HealthConnectManager(this)
        val viewModel = MainViewModel(healthManager)

        setContent {
            val uiState by viewModel.uiState.collectAsState()
            val permissionLauncher = rememberLauncherForActivityResult(
                PermissionController.createRequestPermissionResultContract()
            ) {
                viewModel.loadPreview()
            }

            MaterialTheme {
                MainScreen(
                    uiState = uiState,
                    onServerChanged = viewModel::updateServerUrl,
                    onPhoneChanged = viewModel::updatePhone,
                    onRoleChanged = viewModel::updateRole,
                    onProfileChanged = viewModel::updateProfileId,
                    onLogin = viewModel::loginToFitHub,
                    onGrantPermissions = {
                        permissionLauncher.launch(healthManager.permissions)
                    },
                    onLoadPreview = viewModel::loadPreview,
                    onSync = viewModel::syncToFitHub,
                    onXiaomiInfo = viewModel::showXiaomiMessage,
                )
            }
        }
    }
}

@Composable
private fun MainScreen(
    uiState: MainUiState,
    onServerChanged: (String) -> Unit,
    onPhoneChanged: (String) -> Unit,
    onRoleChanged: (String) -> Unit,
    onProfileChanged: (String) -> Unit,
    onLogin: () -> Unit,
    onGrantPermissions: () -> Unit,
    onLoadPreview: () -> Unit,
    onSync: () -> Unit,
    onXiaomiInfo: () -> Unit,
) {
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(padding)
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text("FitHub Android 原生同步", style = MaterialTheme.typography.headlineSmall)
            Text(uiState.status, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

            OutlinedTextField(
                value = uiState.serverUrl,
                onValueChange = onServerChanged,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("正式网址") },
            )
            OutlinedTextField(
                value = uiState.phone,
                onValueChange = onPhoneChanged,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("手机号") },
            )

            SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                listOf("enthusiast" to "健身爱好者", "gym" to "健身房", "coach" to "教练").forEachIndexed { index, option ->
                    SegmentedButton(
                        selected = uiState.role == option.first,
                        onClick = { onRoleChanged(option.first) },
                        shape = androidx.compose.material3.SegmentedButtonDefaults.itemShape(index = index, count = 3),
                    ) {
                        Text(option.second)
                    }
                }
            }

            Button(onClick = onLogin, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isBusy) "登录中..." else "登录 FitHub")
            }

            if (uiState.resolvedProfileName.isNotBlank()) {
                Text("当前训练者：${uiState.resolvedProfileName}", style = MaterialTheme.typography.bodyMedium)
            } else {
                OutlinedTextField(
                    value = uiState.profileId,
                    onValueChange = onProfileChanged,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("训练者 profileId（高级手动模式）") },
                )
            }

            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedButton(onClick = onGrantPermissions, modifier = Modifier.weight(1f)) {
                    Text("授权 Health Connect")
                }
                OutlinedButton(onClick = onLoadPreview, modifier = Modifier.weight(1f)) {
                    Text("读取预览")
                }
            }

            Button(onClick = onSync, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isBusy) "同步中..." else "同步到 FitHub")
            }

            OutlinedButton(onClick = onXiaomiInfo, modifier = Modifier.fillMaxWidth()) {
                Text("查看小米接入说明")
            }

            uiState.preview?.let { preview ->
                Spacer(modifier = Modifier.height(8.dp))
                Text("健康预览", style = MaterialTheme.typography.titleMedium)
                Text("身高：${preview.heightCm ?: "--"} cm")
                Text("体重：${preview.weightKg ?: "--"} kg")
                Text("体脂：${preview.bodyFat ?: "--"} %")
                Text("静息心率：${preview.restingHeartRate ?: "--"} bpm")
                Text("今日步数：${preview.stepCount ?: "--"}")
                Text("今日活跃卡路里：${preview.activeEnergyBurned ?: "--"} kcal")
                Text("最近训练：${preview.workouts.size} 条")
            }
        }
    }
}
