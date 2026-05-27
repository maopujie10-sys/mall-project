package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.DomainRotation;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface DomainRotationMapper extends BaseMapper<DomainRotation> {

    @Update("UPDATE mall_domain_rotation SET clicks = clicks + 1, update_time = NOW() WHERE id = #{id}")
    void incrementClick(Long id);

    @Update("UPDATE mall_domain_rotation SET status = 'blocked', blocked_reason = #{reason}, update_time = NOW() WHERE domain = #{domain}")
    void blockDomain(String domain, String reason);

    @Update("UPDATE mall_domain_rotation SET status = 'active', blocked_reason = NULL, update_time = NOW() WHERE domain = #{domain}")
    void unblockDomain(String domain);
}
