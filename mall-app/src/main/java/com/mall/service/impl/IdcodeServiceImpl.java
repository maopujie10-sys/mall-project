package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.Idcode;
import com.mall.mapper.IdcodeMapper;
import com.mall.service.IdcodeService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class IdcodeServiceImpl implements IdcodeService {

    private final IdcodeMapper idcodeMapper;
    private final PasswordEncoder passwordEncoder;

    private static final Logger auditLog = LoggerFactory.getLogger("AUDIT");
    private static final int CODE_EXPIRE_MINUTES = 5;
    private static final int SEND_INTERVAL_SECONDS = 60;
    private static final SecureRandom RNG = new SecureRandom();

    @Override
    @Transactional
    public void send(String target, String type, String ip) {
        Idcode last = idcodeMapper.selectOne(
            new QueryWrapper<Idcode>()
                .eq("target", target)
                .eq("type", type)
                .gt("create_time", LocalDateTime.now().minusSeconds(SEND_INTERVAL_SECONDS))
                .orderByDesc("create_time")
                .last("LIMIT 1"));
        if (last != null) {
            throw new BizException("发送过于频繁，请" + SEND_INTERVAL_SECONDS + "秒后再试");
        }

        String code = String.format("%06d", RNG.nextInt(1000000));

        Idcode idcode = new Idcode();
        idcode.setTarget(target);
        idcode.setCode(passwordEncoder.encode(code));
        idcode.setType(type);
        idcode.setExpireAt(LocalDateTime.now().plusMinutes(CODE_EXPIRE_MINUTES));
        idcode.setUsed(0);
        idcode.setIp(ip);
        idcodeMapper.insert(idcode);

        auditLog.info("IDCODE_SEND target={} type={} ip={}", target, type, ip);

        // TODO: send code via SMS or email when gateway is integrated
    }

    @Override
    @Transactional
    public boolean verify(String target, String code, String type) {
        // Query all unused codes for this target+type that haven't expired
        List<Idcode> list = idcodeMapper.selectList(
            new QueryWrapper<Idcode>()
                .eq("target", target)
                .eq("type", type)
                .eq("used", 0)
                .gt("expire_at", LocalDateTime.now())
                .orderByDesc("create_time")
                .last("LIMIT 5"));

        for (Idcode idcode : list) {
            if (passwordEncoder.matches(code, idcode.getCode())) {
                int rows = idcodeMapper.update(null,
                    new UpdateWrapper<Idcode>()
                        .eq("id", idcode.getId())
                        .eq("used", 0)
                        .set("used", 1));
                if (rows > 0) {
                    auditLog.info("IDCODE_VERIFY_OK target={} type={}", target, type);
                    return true;
                }
            }
        }

        auditLog.warn("IDCODE_VERIFY_FAIL target={} type={}", target, type);
        throw new BizException("验证码错误或已使用");
    }
}
