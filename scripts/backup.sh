#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP=/backup/mall_${DATE}
mkdir -p $BACKUP
docker exec mall-db mysqldump -u root -p${DB_ROOT_PASSWORD} malldb > $BACKUP/malldb.sql
cp -r /opt/mall/uploads $BACKUP/ 2>/dev/null
echo "备份完成：$BACKUP ($(du -sh $BACKUP 2>/dev/null | cut -f1))"
find /backup -name "mall_*" -mtime +30 -exec rm -rf {} \; 2>/dev/null
