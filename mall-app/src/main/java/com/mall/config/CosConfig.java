package com.mall.config;

import com.qcloud.cos.COSClient;
import com.qcloud.cos.ClientConfig;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.region.Region;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(CosProperties.class)
public class CosConfig {

    private static final Logger log = LoggerFactory.getLogger(CosConfig.class);

    @Bean
    @ConditionalOnExpression("T(org.springframework.util.StringUtils).hasText('${cos.secret-id:}')")
    public COSClient cosClient(CosProperties props) {
        log.info("COS configured: bucket={}, region={}", props.getBucketName(), props.getRegion());
        COSCredentials cred = new BasicCOSCredentials(props.getSecretId(), props.getSecretKey());
        ClientConfig clientConfig = new ClientConfig(new Region(props.getRegion()));
        return new COSClient(cred, clientConfig);
    }
}
