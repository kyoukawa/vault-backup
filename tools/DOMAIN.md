# 自定义域名

2026-11-26 上线。

| 站点 | 域名 | 记录 |
|---|---|---|
| 个人主页 | https://kyoukawa.is-a.dev/ | 4 条 A 记录 |
| 知识库 | https://kb.is-a.dev/ | CNAME → `kyoukawa.github.io` |

旧地址 `kyoukawa.github.io` 与 `/vault-backup/` 已 301 到新域名，链接不会断。

## 怎么来的

1. **选 is-a.dev**：免费、走 GitHub PR、不会过期。查可用性看 `domains/<name>.json` 是否 404：
   ```
   https://raw.githubusercontent.com/is-a-dev/register/main/domains/<name>.json
   ```
   > 不能用 DNS 判断——is-a.dev 有通配解析，任何名字都能解析出来。

2. **提 PR**：https://github.com/is-a-dev/register/pull/62875（已合并）
   - 根域名只能用 **A 记录**（DNS 规范不允许根级 CNAME），用 GitHub Pages 那四个 IP
   - 子域可以用 CNAME

3. **PR 模板是硬性要求**：必须保留 HTML 注释、复选框改 `[x]`、填 `WEBSITE_PREVIEW` 和 `WEBSITE_PURPOSE` 两个标记区。漏了 `Template` 检查就 FAILURE。
   - 规则细节：**只有根子域名需要"软件开发相关"**，子域不受此限

4. **等 DNS 生效后再加 CNAME**（顺序不能反）：
   ```powershell
   Resolve-DnsName kb.is-a.dev -DnsOnly
   ```
   然后两个仓库根目录各放一个 `CNAME` 文件（无扩展名，单行域名，无换行）。

5. **开 HTTPS**：
   ```powershell
   gh api --method PUT repos/kyoukawa/<repo>/pages --input pages.json
   # pages.json: {"https_enforced": true}
   ```
   注意：`gh api -f key=value` 会报 `Invalid request`，必须用 `--input` 传 JSON。

## 怎么判断域名是否已经生效

**不要只看 HTTP 200**。is-a.dev 有通配解析：**未注册**的子域名也会解析到 Cloudflare，
并返回 `302 → https://is-a.dev/available?d=<name>`——那是个"这名字可以注册"的占位页。

正确判断：

```powershell
curl.exe -sI --max-time 20 https://<name>.is-a.dev/ | Select-String 'HTTP/|location'
```

| 结果 | 含义 |
|---|---|
| `302` + `Location: https://is-a.dev/available?d=<name>` | **未注册**（PR 还没合并） |
| `200` 且返回你自己的页面 | 已生效 |
| `404` / `5xx` | 注册了但源站有问题 |

DNS 层面同理：`Resolve-DnsName` 对任何名字都能出结果，**不能用来判断可用性**。
可用性只能查 `raw.githubusercontent.com/is-a-dev/register/main/domains/<name>.json` 是否 404。

## 换域名要改的地方

跑 `tools/retarget_domain.py`：

```powershell
python tools/retarget_domain.py --home https://new.is-a.dev/ --vault https://kb.new.is-a.dev/ --apply
```

它改的是两个仓库里的 `github.io` 绝对地址（vault 2 处、home 10 处）。
**相对路径不用改**，字体、样式、ids.json 全都是相对引用。

个人主页的读书数据源有**回退链**，新域名挂了会自动用 github.io，过渡期不会白屏：

```js
var DATA_URLS = [
  'https://kb.is-a.dev/assets/weread.json',
  'https://kyoukawa.github.io/vault-backup/assets/weread.json'
];
```

## 已解决的权限坑

`gh` 之前没登录，MCP 那个 GitHub token 是 Copilot 托管的**只读**凭据（连自己仓库建分支都 403）。

2026-11-25 用设备码登录解决：`gh auth login --web --git-protocol ssh`。
设备码流程在非交互 shell 里能跑——用 `Start-Process` 起进程，读 stderr 拿 code，浏览器授权后进程自己退出。

现在 scope 是 `gist, read:org, repo`，够做：fork、提 PR、改 Pages 设置、建仓、发 release。
