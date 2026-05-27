package com.mall.common;

import com.mall.entity.UserBalance;

import java.math.BigDecimal;

public final class UserBalanceUtil {

    private UserBalanceUtil() {}

    public static BigDecimal getAvailable(UserBalance balance) {
        if (balance == null) return BigDecimal.ZERO;
        BigDecimal bd = balance.getBalance() != null ? balance.getBalance() : BigDecimal.ZERO;
        BigDecimal fz = balance.getFrozen() != null ? balance.getFrozen() : BigDecimal.ZERO;
        return bd.subtract(fz);
    }
}
