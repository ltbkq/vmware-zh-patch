#!/bin/bash
#
# VMware Workstation/Player 中文语言包安装脚本
# 安装消息字典 vmware.vmsg 到 VMware 的 messages/<locale> 目录
#
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VMSG="$SCRIPT_DIR/vmware.vmsg"
LOCALE="zh_CN"

[ -f "$VMSG" ] || { echo "错误: 未找到 $VMSG"; exit 1; }

# ---- 1. 定位 VMware messages 目录 ----
CANDIDATES=(
    /usr/lib/vmware/messages
    /usr/lib/vmware-player/messages
    /usr/lib/vmware-workstation/messages
    /usr/lib/vmware-pxe-server/messages
)
DEST=""
for d in "${CANDIDATES[@]}"; do
    if [ -d "$d" ]; then DEST="$d"; break; fi
done
if [ -z "$DEST" ]; then
    # 兜底：从 vmware 可执行文件反查安装前缀
    VBIN="$(command -v vmware || true)"
    if [ -n "$VBIN" ]; then
        REAL="$(readlink -f "$VBIN")"
        PRE="$(dirname "$(dirname "$REAL")")"
        [ -d "$PRE/messages" ] && DEST="$PRE/messages"
    fi
fi
if [ -z "$DEST" ]; then
    echo "错误: 未找到 VMware messages 目录，请确认已安装 VMware Workstation/Player"
    exit 1
fi
echo "VMware messages 目录: $DEST"

# ---- 2. 权限 ----
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
    echo "需要 root 权限，将使用 sudo ..."
else
    SUDO=""
fi

# ---- 3. 备份原文件（若存在） ----
TARGET_DIR="$DEST/$LOCALE"
TARGET="$TARGET_DIR/vmware.vmsg"
if [ -f "$TARGET" ] && [ ! -f "$TARGET.orig" ]; then
    $SUDO cp -p "$TARGET" "$TARGET.orig"
    echo "已备份原文件 -> $TARGET.orig"
fi

# ---- 4. 安装 ----
$SUDO mkdir -p "$TARGET_DIR"
$SUDO cp "$VMSG" "$TARGET"
$SUDO chmod 644 "$TARGET"
$SUDO chown root:root "$TARGET" 2>/dev/null || true
echo "已安装: $TARGET ($(wc -c < "$VMSG") 字节)"

# ---- 5. 校验 ----
DICTTOOL=""
for t in /usr/lib/vmware/bin/dictTool /usr/lib/vmware-player/bin/dictTool; do
    [ -x "$t" ] && DICTTOOL="$t" && break
done
if [ -n "$DICTTOOL" ]; then
    if "$DICTTOOL" print "$TARGET" > /dev/null 2>&1; then
        echo "字典校验: 通过"
    else
        echo "字典校验: 失败！字典存在语法错误，VMware 将回退到英文界面"
        exit 1
    fi
else
    echo "字典校验: 跳过（未找到 dictTool）"
fi

# ---- 6. 提示 ----
echo
echo "=================================================="
echo " 安装完成。"
echo
echo " 生效条件（缺一不可）:"
echo "   1) 系统 locale 为中文，如 LANG=zh_CN.UTF-8"
echo "      检查: locale   若不是，先执行: sudo localectl set-locale LANG=zh_CN.UTF-8"
echo "   2) 重启 VMware（关闭所有 VMware 窗口后重新打开）"
echo "   3) 重启电脑后依然有效（文件已写入系统目录）"
echo
echo " 卸载: sudo ./uninstall.sh"
echo "=================================================="
