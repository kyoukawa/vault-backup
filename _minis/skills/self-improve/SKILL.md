---
name: self-improve
description: 在代码仓库里跑「自我改进循环」时使用。用户说「自我提升 / 优化代码 / 体检 / 跑一轮」，或你想在不打断用户的情况下小步改进代码时。用仓库自带的 scripts/selfprompt.sh 生成任务提示，再用 selfcheck 验证，一次只改一件事。
---

# 自我改进循环

## 何时用

- 用户说「自我提升」「优化代码」「体检」「跑一轮」
- 大功能刚落地，需要收尾
- 你发现一个小问题、但不值得单独问用户时

## 流程

1. **生成提示**（不要自己凭空想任务）：

   ```sh
   sh scripts/selfprompt.sh --run
   ```

   输出包含：分支/未提交改动、最近提交、测试用例数、测试与类型检查结果、
   异味计数（TODO/FIXME/console.log/as never）、最大文件、候选任务与约束。

2. **只挑一件**，按输出里的优先级：
   失败项 → 未收尾改动 → 异味 → 过大文件（>400 行）→ 缺测试的纯函数。

3. **改**：一个关注点，diff 控制在 300 行内；不顺手重排格式。

4. **验证**：

   ```sh
   pnpm test && pnpm typecheck && pnpm build
   sh scripts/selfcheck.sh --build
   ```

5. **提交**：Conventional Commits + 中文，写「为什么」。

6. **部署（可选）**：构建绿了才部署；部署后

   ```sh
   curl -s localhost:<port>/api/health
   sh scripts/smoke.sh http://127.0.0.1:<port>
   ```

## 硬规则

- 一次只改一件事；多个失败不要混着修
- 不跳过验证、不注释断言、不用 `--no-verify`
- 不碰生产数据；迁移先看 SQL 是否可逆
- 连续两轮没进展 → 停下，写清缺什么信息交给用户

## 常见收获

跑这个循环最容易发现三类问题：

1. 服务器上生成了迁移但没提交回仓库（下次部署会缺表）
2. `pnpm-lock.yaml` / `next-env.d.ts` 这类文件漏提交
3. 依赖 prisma 的「纯函数」无法单测 → 该拆分
