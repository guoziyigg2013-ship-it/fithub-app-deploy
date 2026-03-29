package com.fithub.nativeandroid.health

/**
 * 小米官方健康云当前需要正式合作权限、AppID / AppKey 与 OAuth token。
 * 在拿到这些权限前，优先走 Health Connect。
 */
class XiaomiSyncProvider {
    fun statusMessage(): String {
        return "等待小米健康云正式合作权限。当前建议优先通过 Health Connect 读取小米设备同步后的数据。"
    }
}
