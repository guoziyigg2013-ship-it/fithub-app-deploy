# FitHub 中国大陆试运行方案

目标：

- 保留当前 `FitHub` 的全部设计和交互
- 避免 `Render Free` 冷启动黑屏
- 保留 `Supabase` 持久化数据
- 给中国大陆用户一个更稳定的试运行入口

## 推荐结构

### 前端

将当前前端静态壳部署到更适合中国大陆访问的静态托管：

- 腾讯云 `CloudBase` 静态网站托管
- 腾讯云 `COS + CDN + 自定义域名`

官方文档：

- [CloudBase 静态网站托管](https://cloud.tencent.com/document/product/876/46900)
- [COS 开启自定义 CDN 加速域名](https://cloud.tencent.com/document/product/436/36637)
- [COS 配置自定义域名支持 HTTPS 访问](https://cloud.tencent.com/document/product/436/11142)

## 后端

后端暂时保留：

- `Render + Supabase`

这样可以优先保证：

- 用户资料不丢
- 动态、关注、预约、打卡数据可持续保存

后续如果大陆用户量上来，再把 API 迁到腾讯云 / 阿里云 / 华为云。

## 当前可直接上传的静态包

本地已经准备好的静态包目录：

- `/Users/guoziyi/Documents/gpt/fithub-cn-release`

里面已经包含：

- `index.html`
- `mobile.html`
- `styles.css`
- `app.js`
- `sw.js`
- `config.js`

其中 `config.js` 已经指向当前线上 API：

```js
window.__FITHUB_CONFIG__ = {
  apiOrigin: "https://fithub-app-1btg.onrender.com"
};
```

## 部署步骤

### 方案 A：CloudBase 静态网站托管

1. 登录腾讯云 `CloudBase`
2. 新建环境
3. 进入 `静态网站托管`
4. 上传 `/Users/guoziyi/Documents/gpt/fithub-cn-release` 整个目录内容
5. 打开默认域名测试
6. 如需固定域名，再绑定你自己的自定义域名

### 方案 B：COS + CDN + 自定义域名

1. 在腾讯云创建一个 COS 存储桶
2. 开启静态网站
3. 上传 `/Users/guoziyi/Documents/gpt/fithub-cn-release` 里的文件
4. 开启 `自定义 CDN 加速域名`
5. 绑定你自己的域名，例如 `app.yourdomain.com`
6. 按控制台提示配置 CNAME

## 域名注意事项

如果你要在中国大陆长期给真实用户访问，且使用自定义域名，通常需要：

- 你自己购买的域名
- 完成备案

腾讯云官方文档里也明确提到，自定义 CDN 加速域名场景需要准备自定义域名，并按要求配置。

## 高德地图真实轨迹

当前代码已经支持：

- 浏览器真实 GPS 点位采集
- 高德地图底图叠加轨迹显示

但要真正启用高德底图，仍需在 Render 环境变量里配置：

- `FITHUB_AMAP_WEB_KEY`
- `FITHUB_AMAP_SECURITY_CODE`

高德官方文档：

- [高德 JS API 文档](https://a.amap.com/jsapi/static/doc/index.html)

## 真实轨迹原则

现在系统已经改为：

- 有真实 GPS 点位：展示真实轨迹
- 没采集到足够点位：只记录本次训练，不再伪造轨迹

这样更适合正式试运行，不会误导真实用户。
