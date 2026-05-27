package com.mall.common;

import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class AgentAuthInterceptor implements HandlerInterceptor {

    @Value("${agent.token:}")
    private String agentToken;

    @PostConstruct
    public void init() {
        if (agentToken == null || agentToken.isBlank()) {
            throw new IllegalStateException(
                "agent.token 未配置！必须在 application.properties 中设置 agent.token=<你的安全Token>");
        }
    }

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response, Object handler) throws Exception {
        String token = request.getHeader("X-Agent-Token");
        if (!agentToken.equals(token)) {
            response.setStatus(403);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":403,\"message\":\"Agent Token无效\"}");
            return false;
        }
        return true;
    }
}
