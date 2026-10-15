# 语法/编译检查速查表（按文件类型）

**定位**：`README_AGENT_RULES.md` 第 1 节写的是**规则**（跑几次、什么档位），本文件只是它的**查阅表**。
本文件不在 `.clinerules/` 里，**不会被自动加载**——需要时按第 1 节的指针读它。

**用法**：改完按影响面选一条命令跑（纯局部 1 条；有扩散再加一次最小可运行路径）；同一种检查不重复跑；多种文件类型各一次。
表中没命中的语言 → 用它最小的那一次语法检查；确实没有就明说"无可用检查"，**不凭记忆编命令**（README 第 8 节）。

## 一条命令版（POSIX / macOS / Linux 与 Windows）

- `.py` → `python3 -m py_compile <文件>`（Windows：`python -m py_compile <文件>`）
- `.js` / `.mjs` / `.cjs` → `node --check <文件>`
- `.ts` / `.tsx` → `npx tsc --noEmit`（能限定到改动文件就限定）
- `.json` → `python3 -m json.tool <文件> > /dev/null`（Windows：`Get-Content -Raw <文件> | ConvertFrom-Json | Out-Null`）
- `.yaml` / `.yml` → `python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" <文件>`（没有 PyYAML 就交给 IDE/CI）
- `.toml` → `python3 -c "import tomllib,sys;tomllib.load(open(sys.argv[1],'rb'))" <文件>`（Python < 3.11 用 `tomli`）
- `.sh` / `.bash` → `bash -n <文件>`
- `.ps1` → Windows：`[ScriptBlock]::Create((Get-Content -Raw <文件>)) | Out-Null`；POSIX 交给 `pwsh` 或 CI
- `.xml` → `python3 -c "import xml.dom.minidom,sys;xml.dom.minidom.parse(sys.argv[1])" <文件>`（HTML 容错低，交给 IDE/浏览器更合适）
- `.go` → `gofmt -l <文件>`（或 `go build ./...` 限定到改动包）
- `.rs` → `cargo check`（能限定 crate/feature 就限定）
- `.java` → 项目自带 `mvn -q compile` / `gradle compileJava`；没有就 `javac -d <临时目录> <文件>`
- `.c` / `.cpp` → `cc -fsyntax-only <文件>`（或项目 make 的单文件编译目标）
- `.cs` → `dotnet build <项目> -v q`
- `.ipynb` → `python3 -c "import nbformat,sys;nbformat.read(sys.argv[1],as_version=4)" <文件>`
- `.sql` → 项目自带的迁移/校验工具；有 CLI 时才 `psql --single-transaction -c '<语句>'`
- `.md` / 规则 / 纯文本配置 / `.gitignore` → **不跑任何命令**（项目自己在用 `markdownlint` 才跑一次）

## 仍然优先的

- **项目自带的最快检查优先**：`pytest -q` / `npm test` / `make check` / `cargo check` …，有就用它，不要另造脚手架。
- 优先跑**真实入口的最小路径**，不要为了验证另写脚本把结论重算一遍。
- 默认不做：整套测试（除非它恰好是最快那条命令）、重建整份中间产物/缓存、多组参数对比、反复重跑同一检查。
