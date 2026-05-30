"""统一语言：所有产品标题→纯英文, cn记录同步为英文(平台前端自动适配多语言)"""
import os
import re
import sys
import pymysql
import httpx

DB_CONFIG = {"host": "127.0.0.1", "port": 3306, "user": "root", "password": "Root@123", "database": "mall", "charset": "utf8mb4"}
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-0efa2e0529ff46b8932911a3e729ed35")
BATCH = 20

def has_cn(s):
    return bool(re.search(r'[一-鿿]', s or ''))

def batch_clean_to_en(texts):
    """批量把标题转为纯英文（纯英文不动，含中文的提取/翻译为英文）"""
    items = "\n".join(f"{i+1}. {t[:250]}" for i, t in enumerate(texts))
    r = httpx.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": (
                f"For each product title below, output it in pure English.\n"
                f"If already English, keep as-is. If mixed or Chinese, translate/extract to English.\n"
                f"Keep brand names, model numbers, specs unchanged.\n"
                f"Return ONLY one line per title, numbered, no extra text.\n\n{items}"
            )}],
            "max_tokens": len(texts) * 120, "temperature": 0.2,
        }, timeout=90
    )
    if r.status_code == 200:
        content = r.json()["choices"][0]["message"]["content"]
        results = []
        for line in content.strip().split("\n"):
            m = re.match(r'^\d+[\.\)\s]\s*(.+)', line.strip())
            if m and len(m.group(1)) > 2:
                results.append(m.group(1)[:255])
        while len(results) < len(texts):
            results.append(texts[len(results)])
        return results[:len(texts)]
    print(f"API错误: {r.status_code}")
    return texts

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 1. 修复 en 记录中混入中文的
    cur.execute("SELECT UUID, GOODS_ID, NAME FROM T_MALL_SYSTEM_GOODS_LANG WHERE LANG='en' AND NAME REGEXP '[一-鿿]'")
    en_bad = cur.fetchall()
    print(f"en含中文: {len(en_bad)} 条")

    fixed = 0
    for i in range(0, len(en_bad), BATCH):
        batch = en_bad[i:i+BATCH]
        cleaned = batch_clean_to_en([r[2] for r in batch])
        for (uid, gid, orig), clean in zip(batch, cleaned):
            if clean and clean != orig:
                cur.execute("UPDATE T_MALL_SYSTEM_GOODS_LANG SET NAME=%s WHERE UUID=%s", (clean[:255], uid))
                fixed += 1
        conn.commit()
        print(f"  en: {min(i+BATCH, len(en_bad))}/{len(en_bad)} fixed={fixed}")

    # 2. cn 记录统一改为对应的英文标题
    cur.execute("""
        SELECT cn.UUID, cn.NAME, en.NAME
        FROM T_MALL_SYSTEM_GOODS_LANG cn
        JOIN T_MALL_SYSTEM_GOODS_LANG en ON cn.GOODS_ID = en.GOODS_ID AND en.LANG='en'
        WHERE cn.LANG='cn'
    """)
    cn_rows = cur.fetchall()
    print(f"\ncn记录同步: {len(cn_rows)} 条")

    updated = 0
    for uid, cn_name, en_name in cn_rows:
        if cn_name != en_name:
            cur.execute("UPDATE T_MALL_SYSTEM_GOODS_LANG SET NAME=%s WHERE UUID=%s", (en_name[:255], uid))
            updated += 1
    conn.commit()
    print(f"  cn已同步: {updated} 条")

    # 3. 验证
    cur.execute("SELECT LANG, COUNT(*) FROM T_MALL_SYSTEM_GOODS_LANG GROUP BY LANG")
    print("\n=== 最终 ===")
    for r in cur.fetchall():
        cur.execute("SELECT COUNT(*) FROM T_MALL_SYSTEM_GOODS_LANG WHERE LANG=%s AND NAME REGEXP '[一-鿿]'", (r[0],))
        print(f"  {r[0]}: {r[1]} 条 (含中文: {cur.fetchone()[0]})")

    conn.close()
    print("完成")

if __name__ == "__main__":
    main()
