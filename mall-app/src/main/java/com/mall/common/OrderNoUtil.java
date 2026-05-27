package com.mall.common;

public class OrderNoUtil {

    private static final SnowflakeIdGenerator snowflake = new SnowflakeIdGenerator(1, 1);

    public static String generateOrderNo() {
        return "ORD" + snowflake.nextId();
    }

    public static String generateRechargeNo() {
        return "RC" + snowflake.nextId();
    }

    public static String generateWithdrawNo() {
        return "WD" + snowflake.nextId();
    }
}
