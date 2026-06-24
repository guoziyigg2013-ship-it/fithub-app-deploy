# FitHub 发布前后执行顺序

这份手册用于支持 `FitHub V2 大升级` 的日常发布。目标很明确：

- 发布前先把明显会出问题的改动挡在本地
- 发布后 3 到 5 分钟内确认固定域和后端没被改坏
- 避免“更新成功了，但登录/关注/打卡/消息坏了”这种情况

## 一、发布前

在发布前，先进入发布仓库目录：

```bash
cd /Users/guoziyi/Documents/gpt/fithub-app-deploy
```

### 1. 跑一键自检

```bash
npm run check:preflight
```

这一步会依次检查：

1. `node --check app.js`
2. `python3 -m py_compile server.py`
3. API 回归测试
4. Playwright UI 主链回归

通过标准：

- 命令退出码是 `0`
- 没有失败用例

如果失败：

- 先修失败项
- 不要继续发布

### 1.5 跑生产配置门禁

准备小程序上架或真实用户测试前，必须执行：

```bash
npm run check:production
```

这一步会检查：

1. Web 前端是否仍指向 Render、Pages、trycloudflare 等临时域名
2. 小程序是否仍使用 `touristappid`
3. 小程序 API 是否仍指向临时域名
4. Supabase Project URL 是否真实可解析
5. 线上后端是否仍在 `local-fallback`

当前如果还没有备案生产 API 域名，这一步失败是预期的。它的作用是提醒我们：只能继续内部测试，不能提交审核或面向真实用户发布。

拿到正式备案 API 域名和真实小程序 AppID 后，先执行一次配置切换：

```bash
npm run config:production -- \
  --api-origin https://api.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID
```

切换后再跑：

```bash
npm run check:production
```

如果还没正式切换，只想预览会改什么：

```bash
npm run config:production -- \
  --api-origin https://api.yourdomain.com \
  --miniapp-appid wx你的真实小程序AppID \
  --dry-run
```

### 2. 看一眼本次改动范围

重点确认是否触碰了这些高风险链路：

- 账号登录/验证码
- 关注/粉丝
- 动态/消息
- 打卡/健康
- 预约/订单
- 商城

如果触碰了上面任意一类，就必须保证 `check:preflight` 已通过。

### 3. 推送代码

确认自检通过后，再进行：

```bash
git add .
git commit -m "..."
git push
```

### 3.5 构建腾讯云后端发布包

如果这次要部署到国内后端，执行：

```bash
npm run release:tencent
```

把生成的 `dist/fithub-tencent-release-*.tar.gz` 上传到腾讯云服务器。不要上传本地整个工作区，避免误带测试数据、备份和密钥。

### 4. 大升级前做生产数据快照

如果这次发布会影响账号、关注、动态、消息、预约、打卡、媒体或存储配置，先执行：

```bash
FITHUB_ADMIN_TOKEN=你的管理员token npm run snapshot:prod
```

生成的快照会写入本地 `backups/` 目录，该目录已被 `.gitignore` 忽略，不会被误提交。请记录快照文件路径，发布后用于对比。

## 二、发布中

### 1. 后端发布

迁到国内前，旧流程是在 Render 上：

- 选择 `Deploy latest commit`

迁到腾讯云后，改为在服务器上：

```bash
tar -xzf fithub-tencent-release-*.tar.gz
cd fithub-app-deploy/deploy/tencent-cloud
cp .env.production.example .env.production
# 填写真实域名、数据库、管理员 token 后：
./deploy.sh
```

### 2. 中国固定域发布

如果这次改动包含前端页面或样式，执行：

```bash
./deploy-cn-pages.sh
```

## 三、发布后

### 1. 跑部署后冒烟

```bash
npm run check:smoke
```

默认检查：

- 前端：`https://fithub-cn.pages.dev/`
- 后端：`https://fithub-app-1btg.onrender.com`

通过标准：

- 前端首页返回正常
- `healthz` 返回 `ok`
- `storage/status` 显示后端仍在使用 Supabase 持久化，不是本地 JSON fallback
- `bootstrap` 结构正常

### 1.5 对比生产数据快照

如果发布前已经生成快照，发布后执行：

```bash
FITHUB_ADMIN_TOKEN=你的管理员token \
python3 scripts/production_snapshot.py \
  --compare backups/fithub-production-snapshot-旧版本时间.json
```

这一步会拦截真实用户、关注、动态、私信、预约、打卡等关键计数异常下降。除非确认是人工删除，否则不要使用 `--allow-decrease` 绕过。

### 2. 手工确认最小 5 条

每次发布后，至少手工过这 5 条：

1. 登录
2. `我关注的`
3. 发动态
4. 发私信
5. 打卡

如果只想做最短验证，建议顺序就是：

1. 打开固定域
2. 进入已有账号
3. 看 `我关注的`
4. 发送一条私信
5. 完成一次打卡

### 3. 出问题时怎么判断

#### 如果 `check:preflight` 失败

说明是本地代码问题，先修代码，不要发布。

#### 如果 `check:preflight` 通过，但 `check:smoke` 失败

说明更像是部署、环境变量或线上配置问题。优先检查：

- Render 是否部署到最新提交
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- 固定域是否已经发布到最新前端

#### 如果冒烟通过，但用户反馈局部功能异常

优先检查：

- 是否为 Safari 缓存
- 是否为历史脏数据
- 是否为这次改动只影响特定身份

## 四、推荐执行节奏

建议以后每次升级，都按这个节奏：

1. 本地改完
2. `npm run check:preflight`
3. 推送代码
4. Render 发布
5. Pages 发布
6. `npm run check:smoke`
7. 生产快照对比
8. 手工最小 5 条验收

如果是小程序上架前最终验收，把第 6 步前面加上：

```bash
npm run check:production
```

只有 `check:production` 和 `check:smoke` 同时通过，才说明“固定域、后端、数据库、小程序配置”都进入可提交状态。

## 五、当前第一阶段完成标准

当下面几条都稳定成立，就算第一阶段基本收口：

1. `npm run check:preflight` 稳定通过
2. `npm run check:smoke` 稳定通过
3. 新注册账号在部署后不丢
4. `我关注的` 在部署后不丢
5. 私信和点赞不会因为延迟导致重复操作
6. 打卡、动态、订单在部署后继续可用
