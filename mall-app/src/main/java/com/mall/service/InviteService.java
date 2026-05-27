package com.mall.service;

import java.util.Map;

public interface InviteService {
    Map<String, Object> inviteInfo(Long userId);
    Map<String, Object> inviteRecords(Long userId, Integer pageNum, Integer pageSize);
}
