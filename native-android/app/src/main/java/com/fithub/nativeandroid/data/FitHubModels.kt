package com.fithub.nativeandroid.data

data class FitHubProfile(
    val id: String,
    val role: String,
    val name: String,
)

data class FitHubBootstrap(
    val sessionId: String,
    val currentActorProfileId: String?,
    val profiles: List<FitHubProfile>,
)

data class FitHubLoginRequest(
    val sessionId: String,
    val role: String,
    val phone: String,
)

data class NativeHealthMetrics(
    val heightCm: Int?,
    val weightKg: Double?,
    val bodyFat: Double?,
    val restingHeartRate: Int?,
    val stepCount: Int?,
    val activeEnergyBurned: Double?,
)

data class NativeWorkoutPayload(
    val externalId: String,
    val workoutType: String,
    val sportId: String,
    val sportLabel: String,
    val durationMinutes: Int,
    val distanceKm: Double?,
    val activeEnergyBurned: Double?,
    val startedAt: String,
    val endedAt: String,
)

data class NativeHealthSyncPayload(
    val sessionId: String,
    val profileId: String,
    val source: String,
    val deviceName: String,
    val devices: List<String>,
    val metrics: NativeHealthMetrics,
    val workouts: List<NativeWorkoutPayload>,
)

data class HealthPreview(
    val heightCm: Int?,
    val weightKg: Double?,
    val bodyFat: Double?,
    val restingHeartRate: Int?,
    val stepCount: Int?,
    val activeEnergyBurned: Double?,
    val workouts: List<NativeWorkoutPayload>,
)
