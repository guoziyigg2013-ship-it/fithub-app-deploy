# FitHub 关键流程回归测试清单与自动化测试方案

## 目标

这份清单用于支持 `FitHub V2 大升级`。优先目标不是增加新功能，而是保证每次升级后下面这些能力不被改坏：

- 新用户注册后不丢
- 同设备和跨设备登录稳定
- 关注、粉丝、点赞、收藏、评论、私信不会错乱
- 打卡、健康、订单、商城这些主流程仍可用
- 前端固定域与后端部署更新后，数据仍然存在

## 测试环境

建议分成 3 层：

1. 本地开发环境
   - 前端：本地静态页
   - 后端：本地 `server.py`
   - 存储：单独测试用 Supabase 项目或测试 schema

2. 预发布环境
   - 前端固定域：`https://fithub-cn.pages.dev/`
   - 后端：Render 最新部署
   - 存储：同一测试 Supabase

3. 生产试运行环境
   - 真正给测试用户使用的固定域
   - 只做冒烟验证，不直接做破坏性测试

## 关键流程回归清单

### A. 账号与登录

必须通过：

1. 新用户注册
   - 训练者可正常注册
   - 教练可正常注册
   - 健身房可正常注册
   - 同手机号 + 同身份不会重复造号

2. 验证码登录
   - 输入手机号后能拿到验证码
   - 验证码登录后进入正确身份
   - 换设备登录后仍能回到原身份

3. 自动恢复登录
   - 同设备关闭网页再打开，尽量自动恢复
   - 手动退出登录后，不会立刻又被自动拉回
   - 退出后重新登录仍能回到原账号

4. 升级后稳定性
   - 后端重新部署后，原账号仍存在
   - 前端重新部署后，原账号仍存在
   - `我关注的`、粉丝、消息不会被清空

### B. 关注与社交关系

必须通过：

1. 首页/探索页关注
   - 可关注教练
   - 可关注健身房
   - 可关注健身爱好者

2. 粉丝与回关
   - 粉丝列表准确
   - 回关直接生效
   - 回关后状态正确显示

3. 数据持久化
   - 退出再登录后，关注关系仍在
   - 重新部署后，关注关系仍在

### C. 动态流

必须通过：

1. 发布动态
   - 纯文本动态
   - 图文动态
   - 图片 + 视频媒体动态
   - 发布后本人主页可见

2. 探索流
   - 关注对象的动态按时间线展示
   - 关注的健身爱好者即使没发动态，也能在探索里以信息卡展示

3. 媒体流
   - 图片/视频发布成功后能正常显示
   - 视频有封面缩略图
   - 收藏里的媒体动态可重复打开
   - 刷新后媒体仍可展示

4. 互动
   - 点赞即时反馈
   - 收藏即时反馈
   - 评论可发布
   - 点赞/收藏/评论数量正确

5. 数据持久化
   - 刷新后动态仍在
   - 重新部署后动态仍在

### D. 消息系统

必须通过：

1. 私信
   - 打开聊天窗口正常
   - 发送消息时立刻出现气泡
   - 发送中按钮状态正确
   - 不会因为延迟重复发送

2. 消息中心
   - 赞、评论、@我会进入消息页
   - 私信列表有未读红点
   - 进入消息页或聊天后未读数清理正确

3. 数据持久化
   - 刷新后聊天记录仍在
   - 重新部署后聊天记录仍在

### E. 打卡与健康

必须通过：

1. 打卡入口
   - 训练者进入打卡页正常
   - GO 后进入全屏运动页
   - 运动中不能切换项目
   - 暂停/继续可用

2. 户外运动
   - 户外跑步/行走可记录真实 GPS 点
   - 结束打卡不卡死
   - 有真实点位时能生成轨迹
   - 轨迹详情页能打开

3. 健康中心
   - 概览页正常显示
   - 趋势页正常显示
   - 打卡数据能回写到健康页

### F. 预约与订单

必须通过：

1. 训练者视角
   - 可发起预约
   - 订单在“我的”里可见

2. 教练/健身房视角
   - 能看到别人给我的预约
   - 能看到别人给我的订单

3. 数据持久化
   - 刷新后订单仍在
   - 重新部署后订单仍在

### G. 商城

必须通过：

1. 商城入口可打开
2. 分类切换正常
3. 商品列表可见
4. 咨询购买入口可用

## 自动化测试方案

## 第一层：后端 API 回归

推荐工具：

- Python 自带 `unittest` 或 `pytest`
- 直接调用本地 `server.py`

先自动化这些接口：

- `/api/auth/send-code`
- `/api/auth/login`
- `/api/register`
- `/api/follow/toggle`
- `/api/post/create`
- `/api/post/like`
- `/api/post/comment`
- `/api/message/send`
- `/api/booking/create`
- `/api/checkin/create`
- `/api/bootstrap`

重点断言：

- 同手机号同身份不会重复创建 profile
- 登录后返回的 `managedProfileIds` 正确
- follow / favorite / booking / checkin 都会反映到 bootstrap
- 更空状态不会覆盖已有远端状态

### 当前已落地

- 已新增 API 回归测试骨架：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/support.py`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_auth.py`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_social.py`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_content.py`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_booking.py`
- 当前自动覆盖 7 条主链：
  - 训练者注册并验证码登录
  - 同手机号同身份复用同一 profile
  - 关注关系在重新登录和服务重启后仍存在
  - 粉丝与互相关注正确回显
  - 动态、点赞、收藏、评论、通知正确回显
  - 打卡、私信、预约会正确出现在 bootstrap 里
  - 发起预约后发起方/接收方都能看到对应记录
- 本地运行命令：
  - `python3 -m unittest discover -s tests/api -p 'test_*.py' -v`
- 已新增 GitHub Actions 自动化：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/.github/workflows/api-regression.yml`
  - 触发时机：`push main` 和 `pull_request`

## 第二层：浏览器 E2E 自动化

推荐工具：

- `Playwright`

原因：

- 你当前是单页前端 + Python 后端
- 重点问题都发生在真实浏览器交互层
- Playwright 很适合测短信登录、关注、私信、打卡、页面切换

建议先做 8 条主链自动化：

1. 新用户注册成功
2. 验证码登录成功
3. 关注教练/健身房/爱好者
4. 发布一条带图片的动态
5. 点赞与收藏即时反馈
6. 私信发送即时反馈
7. 打卡完成并保存
8. 刷新后数据仍在

### 当前已落地

- 已新增 Playwright 浏览器测试骨架：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/package.json`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/playwright.config.js`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/scripts/run_test_server.py`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/helpers.js`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/auth.spec.js`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/social.spec.js`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/messaging.spec.js`
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/checkin.spec.js`
- 当前已跑通 4 条 UI 主链：
  - 训练者注册成功后，同设备重进会自动恢复，退出后可验证码重新登录
  - 训练者可以关注推荐对象，并在“我关注的”里看到对方
  - 训练者关注后可以打开私信并即时发送一条消息
  - 训练者可以切换到室内项目并完成一次打卡
- 本地运行命令：
  - `npx playwright test tests/e2e --reporter=line --timeout=30000`
- 已新增 GitHub Actions 自动化：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/.github/workflows/ui-regression.yml`
  - 触发时机：`push main`、`pull_request`、`workflow_dispatch`
- 当前为了保证稳定性，Playwright 默认串行执行（`workers: 1`），避免同一临时服务和同一份测试数据互相污染

## 第三层：部署后冒烟测试

每次 Render 或固定域重新发布后，只跑最小 5 条：

1. 登录
2. `我关注的`
3. 发动态
4. 发私信
5. 打卡

这层要尽量在 3 到 5 分钟内跑完。

### 当前已落地

- 已新增一键自检脚本：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/scripts/preflight_check.py`
- 已新增部署后冒烟脚本：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/scripts/deploy_smoke.py`
- 已新增 GitHub Actions 手动冒烟工作流：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/.github/workflows/deploy-smoke.yml`
- 当前可直接执行：
  - `python3 scripts/preflight_check.py`
  - `python3 scripts/deploy_smoke.py`
  - `npm run check:preflight`
  - `npm run check:smoke`

## 推荐的自动化目录结构

```text
tests/
  api/
    test_auth.py
    test_follows.py
    test_posts.py
    test_messages.py
    test_checkin.py
  e2e/
    auth.spec.ts
    social.spec.ts
    messaging.spec.ts
    checkin.spec.ts
    booking.spec.ts
  fixtures/
    seed_data.json
```

## 测试账号策略

建议固定 4 类测试账号：

- `训练者 A`
- `训练者 B`
- `教练 A`
- `健身房 A`

并固定一套种子数据：

- 至少 2 条动态
- 至少 1 组关注关系
- 至少 1 条私信线程
- 至少 1 笔预约
- 至少 1 条打卡

这样可以稳定复现所有主流程。

## 发布前检查清单

每次升级前必须确认：

1. 本地语法检查通过
   - `node --check app.js`
   - `python3 -m py_compile server.py`

2. API 回归通过
3. E2E 主链通过
4. 固定域冒烟通过

## 第一阶段落地顺序

建议我们按这个顺序正式开工：

1. 先补 `tests/api/` 的最小接口回归
2. 再补 `Playwright` 的登录、关注、私信、打卡 4 条主链
3. 最后补一份发布前一键自检脚本

## 通过标准

当下面 4 条同时满足，就算第一阶段完成：

1. 新注册账号在重新部署后不会丢
2. `我关注的` 在重新部署后不会丢
3. 私信和点赞不会因为延迟导致重复操作
4. 打卡、动态、订单能在部署后继续可用

## 下一步

如果确认这份清单没问题，下一步直接开始：

**第一阶段第 1 步：搭建 API 回归测试骨架**

## 第二阶段当前进展

媒体与内容系统升级已经开始，当前第一步已落地：

- 注册头像优先上传到 `Supabase Storage`
- 动态图片/视频优先上传到 `Supabase Storage`
- 图片会同步生成缩略图，视频会同步生成封面缩略图
- 如果对象存储暂时不可用，服务端会自动回退到内联媒体，避免发布流程直接失败
- 当前默认大小限制：
  - 图片 `10 MB`
  - 视频 `8 MB`
  - 缩略图 `2 MB`
- 已新增媒体上传 API 回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_content.py`

第二步也已经落地：

- 动态卡片和收藏页里的图片/视频支持详情预览
- 多图/多视频帖子支持在详情页里左右切换和缩略条定位
- 发布弹窗里删除未发布媒体时，会尝试同步清理对象存储草稿文件
- 关闭发布弹窗或切到底部其他页面时，也会清理未发布的草稿媒体
- 已新增媒体元数据持久化与草稿清理 API 回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/api/test_content.py`

第三步当前已落地：

- 媒体详情页补充了更完整的查看动作和媒体信息标签
- 已新增对象存储巡检/清理脚本：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/scripts/media_maintenance.py`
- 已新增线上媒体维护接口：
  - `POST /api/media/maintenance`
  - 通过 `FITHUB_MEDIA_MAINTENANCE_TOKEN` 控制调用权限
- 脚本会区分：
  - 已被引用的对象
  - 会话中的草稿对象
  - 最近未引用对象
  - 超过阈值的未引用候选对象
- 可通过：
  - `npm run media:report`
  - `npm run media:clean`
  做媒体桶巡检与清理
- 模拟头像和探索页模拟图片已去掉外部 Pexels 依赖，改为内置轻量素材；旧状态中残留的 Pexels 图片也会在客户端兜底替换，降低中国大陆用户首屏图片等待时间

第四步当前已落地：

- 已新增浏览器层媒体与收藏回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/media.spec.js`
- 自动覆盖：
  - 训练者发布一条带图片的动态
  - 发布后动态卡片能显示媒体
  - 收藏按钮即时变为已收藏状态
  - “我的 > 收藏”能打开该媒体动态
  - 媒体详情页能正常打开
  - 刷新页面后收藏媒体仍然存在

第五步当前已落地：

- 已新增浏览器层预约/订单回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/booking.spec.js`
- 自动覆盖：
  - 种子教练账号完成入驻
  - 训练者在首页搜索该教练并进入主页
  - 训练者点击课程定价里的预约入口
  - 训练者预约页能看到已预约订单和价格
  - 教练换设备/新页面验证码登录后，预约页能看到别人给我的预约

第六步当前已落地：

- 已新增浏览器层消息中心回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/messages-center.spec.js`
- 自动覆盖：
  - 作者账号发布动态
  - 另一个真实账号点赞、评论、关注并发送私信
  - 作者换设备/新页面验证码登录后进入 `我的 > 消息`
  - `互动消息` 能看到点赞和评论
  - `私信咨询` 能看到最新私信与未读提示
  - 点击私信线程能打开聊天并看到消息内容
- 同时加固了 E2E 登录 helper，避免注册弹窗已打开时误点底层身份按钮导致超时

第七步当前已落地：

- 点赞改为乐观更新：
  - 点击后立刻切换桃心状态和数量
  - 连续点击不会锁按钮，按真实顺序判定为点赞 / 取消 / 再点赞
  - 后台按点击次数排队同步服务端，避免用户因为延迟重复误操作
  - 点赞不再触发整页重渲染，减少探索页图片和头像闪动
- 已新增浏览器层即时点赞回归用例：
  - `/Users/guoziyi/Documents/gpt/fithub-app-deploy/tests/e2e/social.spec.js`
- 同时优化：
  - 模拟健身房、教练和动态图片改为更像真实场景的本地轻量素材
  - 未上传头像的默认用户头像改为中性灰蓝头像，去掉原来偏黄的身体块

第八步当前已落地：

- 收藏改为乐观更新：
  - 点击后立刻切换星标状态和数量
  - 连续点击不会锁按钮，按真实顺序判定为收藏 / 取消 / 再收藏
  - 后台按点击次数排队同步服务端，不再触发整页重渲染，减少探索页闪动
- 收藏页的数据结构兼容已加固：
  - 收藏列表里的帖子对象会同步更新互动状态
  - 服务端返回动态时补齐收藏数，刷新后数字不乱跳
- 媒体 E2E 已覆盖：
  - 收藏按钮即时反馈
  - 快速取消后再次收藏
  - 进入“我的 > 收藏”仍能打开媒体详情

第九步当前已落地：

- 点赞 / 收藏同步链路降载：
  - 互动按钮点击后只做本地即时状态更新
  - 后台请求改为 compact 小包确认，不再把整份用户、动态、图片状态同步回前端
  - 按钮图标不再通过替换整段 innerHTML 切换，改为 class + CSS 填充，减少局部闪动
- 真实图片测试链路：
  - 模拟健身房和教练改用本地压缩 JPG 真实照片素材
  - 每张动态图控制在约 30-65 KB，头像约 5-10 KB
  - Service Worker 对本地图片走 cache-first，第二次进入更快
- 默认头像优化：
  - 未上传头像时改为灰蓝中性头像
  - 去掉原先偏黄的卡通身体块
- 收藏数修复：
  - 收藏后数字立即显示至少 1
  - 快速取消 / 再收藏会同步显示 0 / 1
