# FitHub Supabase 配置

这套 FitHub 现在支持两种存储模式：

- 默认：本地 `JSON` 文件
- 推荐：`Supabase` 作为持久化状态存储

当服务端检测到以下环境变量时，会自动改为 Supabase：

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

可选环境变量：

- `FITHUB_SUPABASE_TABLE`
  默认值：`fithub_app_state`
- `FITHUB_SUPABASE_ROW_ID`
  默认值：`primary`
- `FITHUB_SUPABASE_TIMEOUT`
  默认值：`12`
- `FITHUB_SUPABASE_BACKUP_RETENTION`
  默认值：`96`，表示保留最近 96 个小时备份
- `FITHUB_SUPABASE_PRUNE_INTERVAL_SECONDS`
  默认值：`3600`，表示最多每小时清理一次过期小时备份

## 1. 在 Supabase 执行 SQL

```sql
create table if not exists public.fithub_app_state (
  id text primary key,
  payload jsonb not null,
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_fithub_app_state_updated_at
  on public.fithub_app_state (updated_at desc);
```

说明：

- 服务端会把整份应用状态写入 `payload`
- 使用 `service_role key` 访问时，不依赖前台用户登录
- 当前方案目标是先解决“用户数据不再因 Render 重启丢失”

## 2. 在 Supabase 获取两个值

进入 `Project Settings -> API`，复制：

- `Project URL`
- `service_role` key

注意：

- 不要把 `service_role` key 放到前端
- 只放到 Render 服务端环境变量里

## 3. 在 Render 设置环境变量

在你的 `fithub-app-1btg` 服务里添加：

- `SUPABASE_URL=https://你的项目.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY=你的service_role_key`
- `FITHUB_SUPABASE_TABLE=fithub_app_state`
- `FITHUB_SUPABASE_ROW_ID=primary`

## 4. 配置效果

配置完成后：

- 注册用户不会因为 Render 实例重启而消失
- 关注、动态、预约、私信、打卡等共享数据会保存在 Supabase
- 即使没有 Render Disk，也能保留核心业务数据
- 访问 `/api/storage/status` 可以看到当前是否正在使用 Supabase，而不是本地 JSON fallback

## 5. 发布后检查

线上发布后执行：

```bash
npm run check:smoke
```

这一步现在会检查：

- 前端固定域是否正常
- 后端 `/healthz` 是否正常
- 后端 `/api/storage/status` 是否仍为 Supabase 持久化
- 后端 `/api/bootstrap` 是否能返回完整业务结构

如果 `/api/storage/status` 显示 `local-fallback`，说明后端最近读取 Supabase 失败。此时服务会保护远端数据，不会用本地 fallback 覆盖生产数据，但需要检查：

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- Supabase 项目是否暂停或网络不可达
- Render 环境变量是否被清空

## 6. 当前限制

当前是“整份状态 JSON 持久化”方案，优点是改动小、上线快。

后续如果你准备正式商用，建议再拆成真正的业务表：

- `profiles`
- `accounts`
- `posts`
- `bookings`
- `threads`
- `messages`
- `follows`
- `checkins`

这样更适合检索、统计、并发和权限控制。
