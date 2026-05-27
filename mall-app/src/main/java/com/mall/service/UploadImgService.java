package com.mall.service;

import java.util.Map;

public interface UploadImgService {
    Map<String, Object> upload(Long userId, String fileName, String fileUrl, Long fileSize, String fileType, String uploadType, String relatedId);
    Map<String, Object> list(Long userId, String uploadType, Integer pageNum, Integer pageSize);
    String delete(Long userId, Long id);
}
