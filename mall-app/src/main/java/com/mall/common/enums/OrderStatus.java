package com.mall.common.enums;

public enum OrderStatus {
    PENDING(0, "待付款"),
    PAID(2, "已付款"),
    SHIPPED(3, "已发货"),
    CANCELLED(4, "已取消"),
    REFUNDING(5, "退款中"),
    COMPLETED(6, "已完成");

    private final int code;
    private final String desc;

    OrderStatus(int code, String desc) {
        this.code = code;
        this.desc = desc;
    }

    public int getCode() { return code; }
    public String getDesc() { return desc; }
}
