package com.fithub.nativeandroid

import android.app.Activity
import android.os.Bundle
import android.widget.TextView

class PermissionsRationaleActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val view = TextView(this).apply {
            text = "FitHub 需要读取 Health Connect 中的训练、体重、身高、体脂、心率和卡路里数据，用于生成真实训练记录与健康概览。"
            textSize = 18f
            setPadding(48, 96, 48, 48)
        }
        setContentView(view)
    }
}
