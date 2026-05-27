package com.mall.service.impl;

import com.mall.service.TelegramService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class TelegramServiceImpl implements TelegramService {

    private final RestTemplate restTemplate;

    public TelegramServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Value("${telegram.bot-token:}")
    private String botToken;

    @Value("${telegram.admin-chat-id:}")
    private String adminChatId;

    private static final String API_URL = "https://api.telegram.org/bot";

    @Override
    public void notifyAdmin(String message) {
        sendMessage(adminChatId, message);
    }

    @Override
    public void notifyUser(Long userId, String message) {
        // Telegram user notification requires user to have linked Telegram
        log.info("Telegram notify userId={}: {}", userId, message);
    }

    private void sendMessage(String chatId, String text) {
        if (!StringUtils.hasText(botToken) || !StringUtils.hasText(chatId)) return;
        try {
            String url = API_URL + botToken + "/sendMessage";
            Map<String, String> params = new HashMap<>();
            params.put("chat_id", chatId);
            params.put("text", text);
            params.put("parse_mode", "HTML");
            restTemplate.postForObject(url, params, String.class);
        } catch (Exception e) {
            log.error("Telegram发送失败：{}", e.getMessage());
        }
    }
}
