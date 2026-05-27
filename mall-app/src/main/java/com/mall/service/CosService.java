package com.mall.service;

import org.springframework.web.multipart.MultipartFile;

public interface CosService {
    String upload(MultipartFile file) throws Exception;
}
