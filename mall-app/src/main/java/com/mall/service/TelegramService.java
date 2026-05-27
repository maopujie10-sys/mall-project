package com.mall.service;

public interface TelegramService {
    void notifyAdmin(String message);
    void notifyUser(Long userId, String message);
}
