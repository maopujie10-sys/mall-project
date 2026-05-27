package com.mall.common;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final JwtAuthInterceptor jwtAuthInterceptor;
    private final AgentAuthInterceptor agentAuthInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtAuthInterceptor)
            .addPathPatterns("/**")
            .excludePathPatterns(
                "/api/user/login", "/api/user/register",
                "/api/user/reset-password/**",
                "/api/product/**", "/api/category/**", "/api/categories/**",
                "/api/goods/**", "/api/banners/**", "/api/health",
                "/api/idcode/**",
                "/api/syspara/**",
                "/api/seller/**",
                "/api/evaluation/product/**",
                "/api/malllevel/**",
                "/api/comment/list/**",
                "/api/loan/config",
                "/api/combo/list", "/api/combo/*",
                "/api/promote/lottery/current",
                "/api/rotation/**",
                "/api/banner/list",
                "/api/area/**",
                "/api/upload",
                "/admin/login", "/merchant/login", "/merchant/reset-password/**", "/merchant/settle", "/merchant/settle/status",
                "/agent/**"
            );
        registry.addInterceptor(agentAuthInterceptor)
            .addPathPatterns("/agent/**");
    }
}
