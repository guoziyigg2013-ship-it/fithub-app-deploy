package com.fithub.nativeandroid.data

import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class FitHubApiClient(
    private val baseUrl: String,
) {
    fun bootstrap(sessionId: String): FitHubBootstrap {
        val cleanBase = baseUrl.removeSuffix("/")
        val apiBase = if (cleanBase.endsWith("/fitness-app-prototype")) {
            "$cleanBase/api"
        } else {
            "$cleanBase/api"
        }
        val url = URL("$apiBase/bootstrap?session_id=$sessionId")
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 15000
            readTimeout = 15000
        }
        return connection.useJsonObject { body ->
            val session = body.getJSONObject("session")
            val profiles = body.getJSONArray("profiles").toProfiles()
            FitHubBootstrap(
                sessionId = session.getString("id"),
                currentActorProfileId = session.optString("currentActorProfileId").takeIf { it.isNotBlank() },
                profiles = profiles,
            )
        }
    }

    fun syncHealth(payload: NativeHealthSyncPayload) {
        val cleanBase = baseUrl.removeSuffix("/")
        val apiBase = if (cleanBase.endsWith("/fitness-app-prototype")) {
            "$cleanBase/api"
        } else {
            "$cleanBase/api"
        }
        val url = URL("$apiBase/health/native-sync")
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 15000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
        }

        val body = JSONObject()
            .put("sessionId", payload.sessionId)
            .put("profileId", payload.profileId)
            .put("source", payload.source)
            .put("deviceName", payload.deviceName)
            .put("devices", JSONArray(payload.devices))
            .put(
                "metrics",
                JSONObject()
                    .put("heightCm", payload.metrics.heightCm)
                    .put("weightKg", payload.metrics.weightKg)
                    .put("bodyFat", payload.metrics.bodyFat)
                    .put("restingHeartRate", payload.metrics.restingHeartRate)
                    .put("stepCount", payload.metrics.stepCount)
                    .put("activeEnergyBurned", payload.metrics.activeEnergyBurned)
            )
            .put(
                "workouts",
                JSONArray(
                    payload.workouts.map { workout ->
                        JSONObject()
                            .put("externalId", workout.externalId)
                            .put("workoutType", workout.workoutType)
                            .put("sportId", workout.sportId)
                            .put("sportLabel", workout.sportLabel)
                            .put("durationMinutes", workout.durationMinutes)
                            .put("distanceKm", workout.distanceKm)
                            .put("activeEnergyBurned", workout.activeEnergyBurned)
                            .put("startedAt", workout.startedAt)
                            .put("endedAt", workout.endedAt)
                    }
                )
            )

        connection.outputStream.use { it.write(body.toString().toByteArray()) }
        connection.useJsonObject { }
    }
}

private fun JSONArray.toProfiles(): List<FitHubProfile> {
    return buildList {
        for (index in 0 until length()) {
            val item = getJSONObject(index)
            add(
                FitHubProfile(
                    id = item.getString("id"),
                    role = item.optString("role"),
                    name = item.optString("name"),
                )
            )
        }
    }
}

private fun <T> HttpURLConnection.useJsonObject(block: (JSONObject) -> T): T {
    return try {
        val code = responseCode
        val stream = if (code in 200..299) inputStream else errorStream
        val text = BufferedReader(InputStreamReader(stream)).use { it.readText() }
        if (code !in 200..299) {
            throw IllegalStateException(text.ifBlank { "FitHub API 请求失败" })
        }
        val json = if (text.isBlank()) JSONObject() else JSONObject(text)
        block(json)
    } finally {
        disconnect()
    }
}
