package com.mall.service;

import java.util.Map;

public interface GeetestService {
    Map<String, String> preProcess(Map<String, String> data);
    String getVersionInfo();
    int enhencedValidateRequest(Map<String, String> data);
    int failbackValidateRequest(Map<String, String> data);
}
