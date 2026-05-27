package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.UserBalanceUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.ComboService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ComboServiceImpl implements ComboService {

    private final MallComboMapper comboMapper;
    private final MallComboLangMapper comboLangMapper;
    private final MallComboRecordMapper comboRecordMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;

    @Override
    public List<Map<String, Object>> list(String lang) {
        List<MallCombo> combos = comboMapper.selectList(
            new QueryWrapper<MallCombo>().orderByAsc("amount"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallCombo c : combos) {
            Map<String, Object> map = toMap(c);
            MallComboLang cl = comboLangMapper.selectOne(
                new QueryWrapper<MallComboLang>()
                    .eq("combo_id", c.getUuid())
                    .eq("lang", lang != null ? lang : "en"));
            if (cl != null) {
                map.put("name", cl.getName());
                map.put("content", cl.getContent());
            } else {
                map.put("name", "Combo " + c.getUuid().substring(0, 8));
                map.put("content", "");
            }
            result.add(map);
        }
        return result;
    }

    @Override
    public Map<String, Object> detail(String uuid, String lang) {
        MallCombo c = comboMapper.selectById(uuid);
        if (c == null) throw new BizException("套餐不存在");
        Map<String, Object> map = toMap(c);

        List<MallComboLang> langs = comboLangMapper.selectList(
            new QueryWrapper<MallComboLang>().eq("combo_id", uuid));
        List<Map<String, Object>> langList = new ArrayList<>();
        for (MallComboLang cl : langs) {
            Map<String, Object> lm = new LinkedHashMap<>();
            lm.put("uuid", cl.getUuid());
            lm.put("name", cl.getName());
            lm.put("content", cl.getContent());
            lm.put("lang", cl.getLang());
            lm.put("status", cl.getStatus());
            langList.add(lm);
            if (cl.getLang().equals(lang)) {
                map.put("name", cl.getName());
                map.put("content", cl.getContent());
            }
        }
        map.put("langs", langList);
        if (!map.containsKey("name")) {
            map.put("name", "Combo " + uuid.substring(0, 8));
            map.put("content", "");
        }
        return map;
    }

    @Override
    @Transactional
    public void create(Map<String, Object> dto) {
        MallCombo c = new MallCombo();
        c.setUuid(UUID.randomUUID().toString().replace("-", ""));
        c.setIconImg((String) dto.getOrDefault("iconImg", ""));
        c.setPromoteNum((Integer) dto.getOrDefault("promoteNum", 0));
        c.setAmount(toBigDecimal(dto.get("amount")));
        c.setDay((Integer) dto.getOrDefault("day", 30));
        c.setBaseAccessNum((Integer) dto.getOrDefault("baseAccessNum", 1));
        c.setAutoAccMin((Integer) dto.getOrDefault("autoAccMin", 1));
        c.setAutoAccMax((Integer) dto.getOrDefault("autoAccMax", 1));
        c.setAccInterval((Integer) dto.getOrDefault("accInterval", 3600));
        c.setCreateTime(LocalDateTime.now());
        comboMapper.insert(c);

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> langs = (List<Map<String, Object>>) dto.get("langs");
        if (langs != null) {
            for (Map<String, Object> lm : langs) {
                MallComboLang cl = new MallComboLang();
                cl.setUuid(UUID.randomUUID().toString().replace("-", ""));
                cl.setComboId(c.getUuid());
                cl.setName((String) lm.get("name"));
                cl.setContent((String) lm.getOrDefault("content", ""));
                cl.setLang((String) lm.get("lang"));
                cl.setStatus(1);
                comboLangMapper.insert(cl);
            }
        }
    }

    @Override
    @Transactional
    public void update(String uuid, Map<String, Object> dto) {
        MallCombo c = comboMapper.selectById(uuid);
        if (c == null) throw new BizException("套餐不存在");

        if (dto.containsKey("iconImg")) c.setIconImg((String) dto.get("iconImg"));
        if (dto.containsKey("promoteNum")) c.setPromoteNum((Integer) dto.get("promoteNum"));
        if (dto.containsKey("amount")) c.setAmount(toBigDecimal(dto.get("amount")));
        if (dto.containsKey("day")) c.setDay((Integer) dto.get("day"));
        if (dto.containsKey("baseAccessNum")) c.setBaseAccessNum((Integer) dto.get("baseAccessNum"));
        if (dto.containsKey("autoAccMin")) c.setAutoAccMin((Integer) dto.get("autoAccMin"));
        if (dto.containsKey("autoAccMax")) c.setAutoAccMax((Integer) dto.get("autoAccMax"));
        if (dto.containsKey("accInterval")) c.setAccInterval((Integer) dto.get("accInterval"));
        comboMapper.updateById(c);

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> langs = (List<Map<String, Object>>) dto.get("langs");
        if (langs != null) {
            comboLangMapper.delete(
                new QueryWrapper<MallComboLang>().eq("combo_id", uuid));
            for (Map<String, Object> lm : langs) {
                MallComboLang cl = new MallComboLang();
                cl.setUuid(UUID.randomUUID().toString().replace("-", ""));
                cl.setComboId(uuid);
                cl.setName((String) lm.get("name"));
                cl.setContent((String) lm.getOrDefault("content", ""));
                cl.setLang((String) lm.get("lang"));
                cl.setStatus(1);
                comboLangMapper.insert(cl);
            }
        }
    }

    @Override
    @Transactional
    public void delete(String uuid) {
        MallCombo c = comboMapper.selectById(uuid);
        if (c == null) throw new BizException("套餐不存在");
        comboMapper.deleteById(uuid);
        comboLangMapper.delete(
            new QueryWrapper<MallComboLang>().eq("combo_id", uuid));
    }

    @Override
    @Transactional
    public void buy(Long userId, String comboId) {
        MallCombo c = comboMapper.selectById(comboId);
        if (c == null) throw new BizException("套餐不存在");

        String partyId = userId.toString();
        long now = System.currentTimeMillis();

        // 检查是否有未过期的同款套餐（从购买记录查）
        long active = comboRecordMapper.selectCount(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", partyId)
                .eq("combo_id", comboId)
                .gt("stop_time", now));
        if (active > 0) throw new BizException("已有生效中的该套餐");

        BigDecimal amount = c.getAmount();
        if (amount.compareTo(BigDecimal.ZERO) <= 0) throw new BizException("套餐金额异常");

        // 查余额，乐观锁扣减
        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null) throw new BizException("余额账户不存在");

        BigDecimal available = UserBalanceUtil.getAvailable(balance);
        if (available.compareTo(amount) < 0) throw new BizException("可用余额不足");

        int rows = userBalanceMapper.update(null,
            new UpdateWrapper<UserBalance>()
                .eq("user_id", userId)
                .eq("version", balance.getVersion())
                .setSql("balance = balance - " + amount)
                .setSql("version = version + 1")
                .set("update_time", LocalDateTime.now()));
        if (rows == 0) throw new BizException("扣款失败，请重试");

        // 写余额日志
        BalanceLog log = BalanceLog.builder()
            .userId(userId)
            .amount(amount.negate())
            .type("COMBO_BUY")
            .remark("购买套餐: " + comboId)
            .createTime(LocalDateTime.now())
            .build();
        balanceLogMapper.insert(log);

        // 创建购买记录（同时作为"我的套餐"的数据源）
        long stopTime = now + c.getDay() * 86400000L;

        MallComboRecord cr = new MallComboRecord();
        cr.setUuid(UUID.randomUUID().toString().replace("-", ""));
        cr.setPartyId(partyId);
        cr.setComboId(comboId);
        cr.setPromoteNum(c.getPromoteNum());
        cr.setAmount(c.getAmount());
        cr.setDay(c.getDay());
        cr.setBaseAccessNum(c.getBaseAccessNum());
        cr.setAutoAccMin(c.getAutoAccMin());
        cr.setAutoAccMax(c.getAutoAccMax());
        cr.setAccInterval(c.getAccInterval());
        cr.setCreateTime(LocalDateTime.now());
        cr.setBeginTime(now);
        cr.setStopTime(stopTime);
        comboRecordMapper.insert(cr);
    }

    @Override
    public List<Map<String, Object>> myCombos(Long userId) {
        String partyId = userId.toString();
        long now = System.currentTimeMillis();
        // 从购买记录查未过期的套餐
        List<MallComboRecord> list = comboRecordMapper.selectList(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", partyId)
                .gt("stop_time", now)
                .orderByDesc("stop_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallComboRecord cr : list) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("uuid", cr.getUuid());
            map.put("comboId", cr.getComboId());
            map.put("promoteNum", cr.getPromoteNum());
            map.put("amount", cr.getAmount());
            map.put("day", cr.getDay());
            map.put("name", cr.getName());
            map.put("beginTime", cr.getBeginTime());
            map.put("stopTime", cr.getStopTime());
            map.put("createTime", cr.getCreateTime());

            MallCombo c = comboMapper.selectById(cr.getComboId());
            if (c != null) {
                map.put("iconImg", c.getIconImg());
                map.put("baseAccessNum", c.getBaseAccessNum());
                map.put("autoAccMin", c.getAutoAccMin());
                map.put("autoAccMax", c.getAutoAccMax());
                map.put("accInterval", c.getAccInterval());
            }
            result.add(map);
        }
        return result;
    }

    @Override
    public List<Map<String, Object>> myRecords(Long userId, int page, int pageSize) {
        String partyId = userId.toString();
        Page<MallComboRecord> p = new Page<>(page, pageSize);
        Page<MallComboRecord> result = comboRecordMapper.selectPage(p,
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", partyId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallComboRecord cr : result.getRecords()) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("uuid", cr.getUuid());
            map.put("comboId", cr.getComboId());
            map.put("promoteNum", cr.getPromoteNum());
            map.put("amount", cr.getAmount());
            map.put("day", cr.getDay());
            map.put("name", cr.getName());
            map.put("beginTime", cr.getBeginTime());
            map.put("stopTime", cr.getStopTime());
            map.put("createTime", cr.getCreateTime());
            list.add(map);
        }
        return list;
    }

    private Map<String, Object> toMap(MallCombo c) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("uuid", c.getUuid());
        map.put("iconImg", c.getIconImg());
        map.put("promoteNum", c.getPromoteNum());
        map.put("amount", c.getAmount());
        map.put("day", c.getDay());
        map.put("baseAccessNum", c.getBaseAccessNum());
        map.put("autoAccMin", c.getAutoAccMin());
        map.put("autoAccMax", c.getAutoAccMax());
        map.put("accInterval", c.getAccInterval());
        map.put("createTime", c.getCreateTime());
        return map;
    }

    // =================== Admin ===================

    @Override
    public Map<String, Object> adminComboList(String name, String startTime, String endTime, Integer page, Integer pageSize) {
        QueryWrapper<MallCombo> qw = new QueryWrapper<MallCombo>().orderByDesc("create_time");
        Page<MallCombo> p = new Page<>(page != null ? page : 1, pageSize != null ? pageSize : 20);
        Page<MallCombo> result = comboMapper.selectPage(p, qw);
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallCombo c : result.getRecords()) {
            Map<String, Object> map = toMap(c);
            List<MallComboLang> langs = comboLangMapper.selectList(
                new QueryWrapper<MallComboLang>().eq("combo_id", c.getUuid()));
            map.put("langs", langs);
            list.add(map);
        }
        Map<String, Object> ret = new LinkedHashMap<>();
        ret.put("records", list);
        ret.put("total", result.getTotal());
        ret.put("page", page != null ? page : 1);
        ret.put("pageSize", pageSize != null ? pageSize : 20);
        return ret;
    }

    @Override
    @Transactional
    public void adminComboSave(String name, String iconImg, BigDecimal amount, Integer day, Integer promoteNum,
                                Integer baseAccessNum, Integer autoAccMin, Integer autoAccMax) {
        MallCombo c = new MallCombo();
        c.setUuid(UUID.randomUUID().toString().replace("-", ""));
        c.setIconImg(iconImg != null ? iconImg : "");
        c.setAmount(amount != null ? amount : BigDecimal.ZERO);
        c.setDay(day != null ? day : 30);
        c.setPromoteNum(promoteNum != null ? promoteNum : 1);
        c.setBaseAccessNum(baseAccessNum != null ? baseAccessNum : 1);
        c.setAutoAccMin(autoAccMin != null ? autoAccMin : 1);
        c.setAutoAccMax(autoAccMax != null ? autoAccMax : 1);
        c.setAccInterval(3600);
        c.setCreateTime(LocalDateTime.now());
        comboMapper.insert(c);

        MallComboLang cl = new MallComboLang();
        cl.setUuid(UUID.randomUUID().toString().replace("-", ""));
        cl.setComboId(c.getUuid());
        cl.setName(name);
        cl.setContent("");
        cl.setLang("en");
        cl.setStatus(1);
        comboLangMapper.insert(cl);
    }

    @Override
    @Transactional
    public void adminComboUpdate(String uuid, String name, String iconImg, BigDecimal amount, Integer day,
                                  Integer promoteNum, Integer baseAccessNum, Integer autoAccMin, Integer autoAccMax) {
        MallCombo c = comboMapper.selectById(uuid);
        if (c == null) throw new BizException("套餐不存在");
        c.setIconImg(iconImg != null ? iconImg : c.getIconImg());
        c.setAmount(amount != null ? amount : c.getAmount());
        c.setDay(day != null ? day : c.getDay());
        c.setPromoteNum(promoteNum != null ? promoteNum : c.getPromoteNum());
        c.setBaseAccessNum(baseAccessNum != null ? baseAccessNum : c.getBaseAccessNum());
        c.setAutoAccMin(autoAccMin != null ? autoAccMin : c.getAutoAccMin());
        c.setAutoAccMax(autoAccMax != null ? autoAccMax : c.getAutoAccMax());
        comboMapper.updateById(c);

        if (name != null && !name.isEmpty()) {
            comboLangMapper.delete(new QueryWrapper<MallComboLang>().eq("combo_id", uuid));
            MallComboLang cl = new MallComboLang();
            cl.setUuid(UUID.randomUUID().toString().replace("-", ""));
            cl.setComboId(uuid);
            cl.setName(name);
            cl.setContent("");
            cl.setLang("en");
            cl.setStatus(1);
            comboLangMapper.insert(cl);
        }
    }

    @Override
    @Transactional
    public void adminComboDelete(String uuid) {
        comboMapper.deleteById(uuid);
        comboLangMapper.delete(new QueryWrapper<MallComboLang>().eq("combo_id", uuid));
    }

    @Override
    public Map<String, Object> adminComboRecordList(String userCode, String sellerName, String startTime,
                                                     String endTime, Integer page, Integer pageSize) {
        QueryWrapper<MallComboRecord> qw = new QueryWrapper<MallComboRecord>().orderByDesc("create_time");
        Page<MallComboRecord> p = new Page<>(page != null ? page : 1, pageSize != null ? pageSize : 20);
        Page<MallComboRecord> result = comboRecordMapper.selectPage(p, qw);
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallComboRecord cr : result.getRecords()) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("uuid", cr.getUuid());
            map.put("partyId", cr.getPartyId());
            map.put("comboId", cr.getComboId());
            map.put("promoteNum", cr.getPromoteNum());
            map.put("amount", cr.getAmount());
            map.put("day", cr.getDay());
            map.put("name", cr.getName());
            map.put("beginTime", cr.getBeginTime());
            map.put("stopTime", cr.getStopTime());
            map.put("createTime", cr.getCreateTime());
            list.add(map);
        }
        Map<String, Object> ret = new LinkedHashMap<>();
        ret.put("records", list);
        ret.put("total", result.getTotal());
        ret.put("page", page != null ? page : 1);
        ret.put("pageSize", pageSize != null ? pageSize : 20);
        return ret;
    }

    private BigDecimal toBigDecimal(Object val) {
        if (val == null) return BigDecimal.ZERO;
        if (val instanceof BigDecimal) return (BigDecimal) val;
        return new BigDecimal(val.toString());
    }
}
