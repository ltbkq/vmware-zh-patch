#!/bin/bash
#
# VMware 中文语言包卸载脚本：恢复备份或删除安装的字典
#
set -e

LOCALE="zh_CN"
CANDIDATES=(
    /usr/lib/vmware/messages
    /usr/lib/vmware-player/messages
    /usr/lib/vmware-workstation/messages
)
DEST=""
for d in "${CANDIDATES[@]}"; do
    if [ -d "$d" ]; then DEST="$d"; break; fi
done
[ -n "$DEST" ] || { echo "错误: 未找到 VMware messages 目录"; exit 1; }

TARGET_DIR="$DEST/$LOCALE"
TARGET="$TARGET_DIR/vmware.vmsg"

[ "$(id -u)" -ne 0 ] && SUDO="sudo" || SUDO=""

if [ -f "$TARGET.orig" ]; then
    $SUDO cp -p "$TARGET.orig" "$TARGET"
    $SUDO rm -f "$TARGET.orig"
    echo "已恢复原文件: $TARGET"
elif [ -f "$TARGET" ]; then
    $SUDO rm -f "$TARGET"
    echo "已删除中文字典: $TARGET"
else
    echo "未找到已安装的字典，无需卸载"
fi

# 清理空目录
rmdir "$TARGET_DIR" 2>/dev/null || true

echo "卸载完成（重启 VMware 后恢复英文界面）"
