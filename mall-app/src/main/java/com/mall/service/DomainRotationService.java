package com.mall.service;

import com.mall.entity.DomainRotation;
import java.util.List;
import java.util.Map;

public interface DomainRotationService {
    Map<String, Object> jump();
    List<DomainRotation> listDomains();
    void blockDomain(String domain, String reason);
    void unblockDomain(String domain);
    Map<String, Object> stats();
}
