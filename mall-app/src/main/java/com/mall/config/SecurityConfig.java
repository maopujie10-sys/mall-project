package com.mall.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(auth -> auth
                // === 公开接口（无需JWT）===
                .requestMatchers(
                    "/api/user/login", "/api/user/register",
                    "/api/user/reset-password/**",
                    "/api/product/**", "/api/category/**", "/api/categories/**", "/api/goods/**",
                    "/api/banners/**", "/api/health",
                    "/api/rotation/**",         // 域名轮值(公开)
                    "/api/idcode/**",           // W3: 验证码发送/验证
                    "/api/syspara/**",          // W3: GET公开参数
                    "/api/seller/**",           // W6: 商家列表/详情/商品
                    "/api/evaluation/product/**", // W5: 公开商品评价
                    "/api/malllevel/**",         // W2: 卖家等级(公开)
                    "/api/banner/list",         // W6: 公开轮播列表
                    "/api/combo/list",           // W5: 公开套餐列表
                    "/api/comment/list/**",      // W5: 公开商品评论
                    "/api/loan/config",          // W6: 公开贷款配置
                    "/admin/login", "/merchant/login", "/merchant/reset-password/**", "/merchant/settle", "/merchant/settle/status",
                "/api/upload",             // W10: 招商入驻公开上传
                "/api/area/**"             // 省市区联动(公开)
                ).permitAll()
                // === 客服：USER + MERCHANT 双角色 ===
                .requestMatchers("/api/chat/**").hasAnyRole("USER", "MERCHANT")
                // === USER 角色 ===
                .requestMatchers(
                    "/api/user/**", "/api/order/**",
                    "/api/cart/**", "/api/recharge/**",
                    "/api/withdraw/**", "/api/address/**",
                    "/api/upload/**",
                    "/api/kyc/**",
                    "/api/subscribe/**",
                    "/api/evaluation/**",
                    "/api/keep-goods/**",
                    "/api/focus-seller/**",
                    "/api/credit/**",
                    "/api/wallet/**",
                    "/api/promote/**",
                    "/api/invite/**",
                    "/api/contract/**",
                    "/api/notification/**",    // W4: 消息中心通知
                    "/api/combo/buy", "/api/combo/my",
                    "/api/combo/records",      // W5: 套餐购买+记录
                    "/api/rebate/**",           // W6: 返利分佣
                    "/api/logistics/**",        // W6: 物流查询
                    "/api/comment/**",          // W5: 用户评论增删
                    "/api/loan/apply", "/api/loan/list",
                    "/api/loan/*", "/api/loan/*/repay",  // W6: 贷款申请/还款
                    "/api/order-log/**"     // W6: 订单日志查询
                ).hasRole("USER")
                // 套餐详情(公开, GET only, 放在USER后面避免覆盖buy/my/records)
                .requestMatchers(HttpMethod.GET, "/api/combo/*").permitAll()
                // === MERCHANT 角色 ===
                .requestMatchers("/merchant/**").hasRole("MERCHANT")
                // === ADMIN 角色 ===
                .requestMatchers("/admin/**", "/api/loan/admin/**").hasRole("ADMIN")
                // === Agent（内部Token鉴权，不走Spring Security角色）===
                .requestMatchers("/agent/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
