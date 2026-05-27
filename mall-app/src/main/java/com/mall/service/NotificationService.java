package com.mall.service;

import java.util.List;
import java.util.Map;

public interface NotificationService {
    Map<String, Object> list(Long userId, Integer pageNum, Integer pageSize, String type);
    Long unread(Long userId);
    /** 按类型查未读数 */
    Long unreadByType(Long userId, Integer type, Integer module, String language);
    /** 通知详情 */
    Map<String, Object> detail(Long userId, Long id);
    /** 标记已读 */
    void markRead(Long userId, Long id);
    /** 批量标记已读 */
    void markReadBatch(Long userId, List<Long> ids);
    /** 全部已读 */
    void markReadAll(Long userId);
    void delete(Long userId, Long id);
    void send(Long userId, String title, String content, String type, String relatedId);
    /** 游标分页滑动列表 */
    List<Map<String, Object>> slideList(Long userId, Long lastLocation, Integer pageSize, String type);

    // === Admin ===
    Map<String, Object> adminSentList(Integer pageNum, Integer pageSize, String type, String keyword);
}
