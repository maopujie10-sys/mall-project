package com.mall.service;

public interface IdcodeService {
    void send(String target, String type, String ip);
    boolean verify(String target, String code, String type);
}
