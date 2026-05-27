package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mall.entity.DomainRotation;
import com.mall.mapper.DomainRotationMapper;
import com.mall.service.DomainRotationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.*;

@Service
@RequiredArgsConstructor
public class DomainRotationServiceImpl implements DomainRotationService {

    private final DomainRotationMapper mapper;
    private static final String CHARS = "abcdefghijklmnopqrstuvwxyz0123456789";
    private static final SecureRandom RANDOM = new SecureRandom();

    private String randomPrefix() {
        int len = 8 + RANDOM.nextInt(8);
        StringBuilder sb = new StringBuilder(len);
        for (int i = 0; i < len; i++) {
            sb.append(CHARS.charAt(RANDOM.nextInt(CHARS.length())));
        }
        return sb.toString();
    }

    @Override
    public Map<String, Object> jump() {
        List<DomainRotation> list = mapper.selectList(
            new LambdaQueryWrapper<DomainRotation>()
                .eq(DomainRotation::getRole, "rotation")
                .eq(DomainRotation::getStatus, "active")
                .orderByAsc(DomainRotation::getUpdateTime)
        );

        if (list.isEmpty()) {
            DomainRotation primary = mapper.selectOne(
                new LambdaQueryWrapper<DomainRotation>()
                    .eq(DomainRotation::getRole, "primary")
            );
            String base = primary != null ? primary.getDomain() : "tiktook.eu.cc";
            String fullDomain = randomPrefix() + "." + base;
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("url", "https://" + fullDomain);
            fallback.put("domain", fullDomain);
            fallback.put("fallback", true);
            return fallback;
        }

        DomainRotation picked = list.get(0);
        String fullDomain = randomPrefix() + "." + picked.getDomain();

        mapper.incrementClick(picked.getId());

        Map<String, Object> result = new HashMap<>();
        result.put("url", "https://" + fullDomain);
        result.put("domain", fullDomain);
        return result;
    }

    @Override
    public List<DomainRotation> listDomains() {
        return mapper.selectList(null);
    }

    @Override
    public void blockDomain(String domain, String reason) {
        mapper.blockDomain(domain, reason);
    }

    @Override
    public void unblockDomain(String domain) {
        mapper.unblockDomain(domain);
    }

    @Override
    public Map<String, Object> stats() {
        List<DomainRotation> all = mapper.selectList(
            new LambdaQueryWrapper<DomainRotation>()
                .orderByDesc(DomainRotation::getClicks)
        );
        long totalClicks = all.stream().mapToLong(DomainRotation::getClicks).sum();
        Map<String, Object> result = new HashMap<>();
        result.put("totalClicks", totalClicks);
        result.put("domains", all);
        return result;
    }
}
