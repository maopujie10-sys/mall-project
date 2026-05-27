package com.mall.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "cos")
@Data
public class CosProperties {
    private String secretId;
    private String secretKey;
    private String region;
    private String bucketName;
}
