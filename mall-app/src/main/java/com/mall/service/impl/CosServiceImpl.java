package com.mall.service.impl;

import com.mall.service.CosService;
import com.qcloud.cos.COSClient;
import com.qcloud.cos.model.ObjectMetadata;
import com.qcloud.cos.model.PutObjectRequest;
import com.qcloud.cos.model.CannedAccessControlList;
import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.util.UUID;

@Service
public class CosServiceImpl implements CosService {

    private static final Logger log = LoggerFactory.getLogger(CosServiceImpl.class);

    @Autowired(required = false)
    private COSClient cosClient;

    @Value("${cos.bucketName}")
    private String bucket;

    @Value("${cos.region}")
    private String region;

    @Value("${cos.domain:}")
    private String domain;

    @Override
    public String upload(MultipartFile file) throws Exception {
        if (cosClient == null) {
            throw new RuntimeException("COS client not available");
        }
        String ext = FilenameUtils.getExtension(file.getOriginalFilename());
        String key = "product/" + UUID.randomUUID() + "." + ext;
        ObjectMetadata meta = new ObjectMetadata();
        meta.setContentLength(file.getSize());
        meta.setContentType(file.getContentType());

        PutObjectRequest req = new PutObjectRequest(bucket, key, file.getInputStream(), meta);
        req.setCannedAcl(CannedAccessControlList.PublicRead);
        cosClient.putObject(req);

        String host = (domain != null && !domain.isBlank())
                ? domain
                : bucket + ".cos." + region + ".myqcloud.com";
        String url = "https://" + host + "/" + key;
        log.info("COS upload success: {}", url);
        return url;
    }
}
