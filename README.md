# VMware Workstation 中文语言包（zh_CN）

汉化 VMware Workstation / Player 的 Linux 版 GUI 界面文字，共 **2822 条**消息翻译。

## 效果预览

![主界面](screenshots/ui-overview.png)

![文件菜单](screenshots/menu-file.png)

![虚拟机菜单](screenshots/menu-vm.png)

## 原理

VMware 自带多语言消息机制 `Msg_SetLocaleEx`：启动时按系统 locale（如 `zh_CN`）
从 `<VMware安装目录>/messages/<locale>/<name>.vmsg` 加载消息字典，用其中的中文
覆盖程序内置的英文。官方安装包不附带任何 locale 字典，本补丁自建
`messages/zh_CN/vmware.vmsg`，因此：

* **不修改任何 VMware 程序文件**，只新增一个数据文件；
* **重启电脑后依然有效**（文件在系统目录中）；
* **可随时卸载**，恢复原始英文界面。

## 环境要求

1. VMware Workstation 或 Player（Linux 版，本补丁按 26.0.1 制作，其他版本同样适用，
   未翻译的条目会自动显示英文）。
2. 系统 locale 必须是中文，VMware 据此决定加载哪个目录：

```bash
locale        # 应显示 LANG=zh_CN.UTF-8
# 若不是，设置：
sudo localectl set-locale LANG=zh_CN.UTF-8
```

## 安装

```bash
chmod +x install.sh uninstall.sh
./install.sh
```

脚本会自动：
* 定位 VMware 的 `messages` 目录（`/usr/lib/vmware/messages` 等常见路径，
  找不到时从 `vmware` 可执行文件反查）；
* 备份已存在的 `vmware.vmsg` 为 `vmware.vmsg.orig`；
* 复制新字典并设置 `644 root:root`；
* 用官方 `dictTool` 校验语法，失败会报错退出。

安装后**完全关闭并重启 VMware**（含托盘图标）即显示中文；重启电脑后仍然有效。

## 卸载

```bash
sudo ./uninstall.sh
```

优先恢复 `vmware.vmsg.orig` 备份；没有备份则直接删除中文字典。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `install.sh` | 安装脚本（定位目录、备份、安装、校验） |
| `uninstall.sh` | 卸载脚本（恢复备份 / 删除字典） |
| `vmware.vmsg` | 汉化字典成品（可直接分发） |
| `zh/*.tsv` | 翻译源表：`key<TAB>中文`，一行一条，换行写作 `\n` |
| `build.py` | 从 `zh/*.tsv` 生成 `vmware.vmsg`，并校验 key 存在、占位符与英文一致 |
| `strings.json` | 英文原文提取结果（key → 英文，含顺序），随仓库提供，`build.py` 默认读取同目录下的该文件 |

重新构建（可选，仅在修改翻译后需要）：

```bash
python3 build.py      # 输出 vmware.vmsg
```

## 已知限制

* 极少数菜单项（如 File 菜单的 `Open...`、`Quit`）取自程序内建的 GTK stock
  标签，不经过 VMware 消息字典，无法通过本补丁汉化。
* 对话框中的动态文本若由插件/子进程生成，可能仍为英文。
* 界面语言由系统 locale 决定；英文系统想看中文界面需临时切换：
  `LC_ALL=zh_CN.UTF-8 LANG=zh_CN.UTF-8 vmware`。

## 字典格式备忘（供维护者）

```
.encoding = "UTF-8"
msg.xxx = "中文文本"
```

* key 必须带 `msg.` 前缀，与程序内置英文的 key 完全一致；
* **唯一转义机制是 `|XX` 十六进制字节**：`|22` = `"`、`|7C` = `|`、`|0A` = 换行、
  `|0D` = 回车、`|09` = 制表符；
* 反斜杠不是特殊字符（`\n` 会按字面两个字符显示）；
* 裸 `"` 或裸 `|` 会导致整个字典 `DictionaryParseReadLine: syntax error` 而加载失败；
* 占位符 `%s %d %u %zd` 必须与英文原文完全一致（`build.py` 会自动检查）。
