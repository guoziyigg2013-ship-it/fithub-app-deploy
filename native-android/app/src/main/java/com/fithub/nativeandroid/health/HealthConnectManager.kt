package com.fithub.nativeandroid.health

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.HealthConnectClient.Companion.SDK_AVAILABLE
import androidx.health.connect.client.HealthConnectClient.Companion.SDK_UNAVAILABLE
import androidx.health.connect.client.HealthConnectClient.Companion.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ActiveCaloriesBurnedRecord
import androidx.health.connect.client.records.BodyFatRecord
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.HeightRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.WeightRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import com.fithub.nativeandroid.data.HealthPreview
import com.fithub.nativeandroid.data.NativeHealthMetrics
import com.fithub.nativeandroid.data.NativeHealthSyncPayload
import com.fithub.nativeandroid.data.NativeWorkoutPayload
import java.time.Instant
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit
import kotlin.math.roundToInt

class HealthConnectManager(private val context: Context) {
    companion object {
        private const val PROVIDER_PACKAGE = "com.google.android.apps.healthdata"
    }

    private val client by lazy { HealthConnectClient.getOrCreate(context) }

    val permissions = setOf(
        HealthPermission.getReadPermission(HeightRecord::class),
        HealthPermission.getReadPermission(WeightRecord::class),
        HealthPermission.getReadPermission(BodyFatRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
    )

    fun availabilitySummary(): String {
        return when (HealthConnectClient.getSdkStatus(context, PROVIDER_PACKAGE)) {
            SDK_AVAILABLE -> "Health Connect 已可用，可以读取真实训练和身体数据。"
            SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> "需要先安装或更新 Health Connect，再继续同步。"
            SDK_UNAVAILABLE -> "当前设备暂不支持 Health Connect。"
            else -> "Health Connect 状态未知，请在真机上检查。"
        }
    }

    suspend fun loadPreview(days: Long = 30): HealthPreview {
        val end = Instant.now()
        val start = end.minus(days, ChronoUnit.DAYS)

        val height = latestHeight()
        val weight = latestWeight()
        val bodyFat = latestBodyFat()
        val heartRate = latestRestingHeartRate()
        val steps = totalStepsToday()
        val calories = activeCaloriesToday()
        val workouts = recentWorkouts(start, end)

        return HealthPreview(
            heightCm = height,
            weightKg = weight,
            bodyFat = bodyFat,
            restingHeartRate = heartRate,
            stepCount = steps,
            activeEnergyBurned = calories,
            workouts = workouts,
        )
    }

    suspend fun buildSyncPayload(sessionId: String, profileId: String): NativeHealthSyncPayload {
        val preview = loadPreview()
        return NativeHealthSyncPayload(
            sessionId = sessionId,
            profileId = profileId,
            source = "health-connect",
            deviceName = "Android + Health Connect",
            devices = listOf("Health Connect"),
            metrics = NativeHealthMetrics(
                heightCm = preview.heightCm,
                weightKg = preview.weightKg,
                bodyFat = preview.bodyFat,
                restingHeartRate = preview.restingHeartRate,
                stepCount = preview.stepCount,
                activeEnergyBurned = preview.activeEnergyBurned,
            ),
            workouts = preview.workouts,
        )
    }

    private suspend fun latestHeight(): Int? {
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = HeightRecord::class,
                timeRangeFilter = TimeRangeFilter.after(Instant.EPOCH),
            )
        )
        return response.records.maxByOrNull { it.time }?.height?.inMeters?.times(100)?.roundToInt()
    }

    private suspend fun latestWeight(): Double? {
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = WeightRecord::class,
                timeRangeFilter = TimeRangeFilter.after(Instant.EPOCH),
            )
        )
        return response.records.maxByOrNull { it.time }?.weight?.inKilograms
    }

    private suspend fun latestBodyFat(): Double? {
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = BodyFatRecord::class,
                timeRangeFilter = TimeRangeFilter.after(Instant.EPOCH),
            )
        )
        return response.records.maxByOrNull { it.time }?.percentage?.value?.times(100)
    }

    private suspend fun latestRestingHeartRate(): Int? {
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.after(Instant.EPOCH),
            )
        )
        return response.records.maxByOrNull { it.endTime }
            ?.samples
            ?.lastOrNull()
            ?.beatsPerMinute
            ?.roundToInt()
    }

    private suspend fun totalStepsToday(): Int? {
        val start = Instant.now().atZone(ZoneOffset.systemDefault()).toLocalDate().atStartOfDay().toInstant(ZoneOffset.UTC)
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = StepsRecord::class,
                timeRangeFilter = TimeRangeFilter.between(start, Instant.now()),
            )
        )
        return response.records.sumOf { it.count.toInt() }
    }

    private suspend fun activeCaloriesToday(): Double? {
        val start = Instant.now().atZone(ZoneOffset.systemDefault()).toLocalDate().atStartOfDay().toInstant(ZoneOffset.UTC)
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = ActiveCaloriesBurnedRecord::class,
                timeRangeFilter = TimeRangeFilter.between(start, Instant.now()),
            )
        )
        return response.records.sumOf { it.energy.inKilocalories }
    }

    private suspend fun recentWorkouts(start: Instant, end: Instant): List<NativeWorkoutPayload> {
        val response = client.readRecords(
            ReadRecordsRequest(
                recordType = ExerciseSessionRecord::class,
                timeRangeFilter = TimeRangeFilter.between(start, end),
            )
        )

        return response.records
            .sortedByDescending { it.endTime }
            .take(20)
            .map { record ->
                NativeWorkoutPayload(
                    externalId = record.metadata.id,
                    workoutType = record.exerciseType.toString(),
                    sportId = mapSportId(record.exerciseType),
                    sportLabel = mapSportLabel(record.exerciseType),
                    durationMinutes = ChronoUnit.MINUTES.between(record.startTime, record.endTime).toInt().coerceAtLeast(1),
                    distanceKm = null,
                    activeEnergyBurned = null,
                    startedAt = record.startTime.toString(),
                    endedAt = record.endTime.toString(),
                )
            }
    }

    private fun mapSportId(type: Int): String = when (type) {
        ExerciseSessionRecord.EXERCISE_TYPE_RUNNING -> "run"
        ExerciseSessionRecord.EXERCISE_TYPE_WALKING -> "outdoor-walk"
        ExerciseSessionRecord.EXERCISE_TYPE_HIKING -> "hiking"
        ExerciseSessionRecord.EXERCISE_TYPE_BIKING -> "outdoor-cycling"
        ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING -> "strength"
        ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING -> "hiit"
        ExerciseSessionRecord.EXERCISE_TYPE_YOGA -> "yoga"
        ExerciseSessionRecord.EXERCISE_TYPE_PILATES -> "pilates"
        ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL, ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER -> "swim"
        else -> "cardio-mix"
    }

    private fun mapSportLabel(type: Int): String = when (type) {
        ExerciseSessionRecord.EXERCISE_TYPE_RUNNING -> "户外跑步"
        ExerciseSessionRecord.EXERCISE_TYPE_WALKING -> "户外行走"
        ExerciseSessionRecord.EXERCISE_TYPE_HIKING -> "徒步"
        ExerciseSessionRecord.EXERCISE_TYPE_BIKING -> "户外骑行"
        ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING -> "传统力量训练"
        ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING -> "HIIT"
        ExerciseSessionRecord.EXERCISE_TYPE_YOGA -> "瑜伽"
        ExerciseSessionRecord.EXERCISE_TYPE_PILATES -> "普拉提"
        ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL, ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER -> "泳池游泳"
        else -> "混合有氧"
    }
}
