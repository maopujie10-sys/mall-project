package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.LotteryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class LotteryServiceImpl implements LotteryService {

    private final MallActivityLibraryMapper activityLibraryMapper;
    private final MallActivityPrizeMapper activityPrizeMapper;
    private final MallActivityUserPointsMapper activityUserPointsMapper;
    private final MallActivityUserMapper activityUserMapper;
    private final MallLotteryRecordMapper lotteryRecordMapper;
    private final MallLotteryReceiveMapper lotteryReceiveMapper;
    private final UserBalanceMapper userBalanceMapper;

    private static String str(Long v) { return v != null ? v.toString() : null; }

    @Override
    public Map<String, Object> getCurrentActivity(String lang) {
        List<MallActivityLibrary> activities = activityLibraryMapper.selectList(
            new QueryWrapper<MallActivityLibrary>()
                .in("type", java.util.Arrays.asList("SIMPLE_LOTTERY", "TURNTABLE", "RECHARGE_LOTTERY"))
                .eq("is_show", 1)
                .eq("deleted", 0)
                .orderByAsc("location"));

        Map<String, Object> result = new HashMap<>();
        if (!activities.isEmpty()) {
            MallActivityLibrary activity = activities.get(0);
            LocalDateTime now = LocalDateTime.now();
            result.put("id", activity.getId());
            result.put("detailUrl", activity.getDetailUrl());
            result.put("title", "cn".equals(lang) || "zh".equals(lang) ?
                activity.getTitleCn() : activity.getTitleEn());
            result.put("status", activity.getStatus());
            result.put("running", (activity.getStartTime().isAfter(now) || activity.getEndTime().isBefore(now)) ? "0" : "1");
        }
        return result;
    }

    @Override
    public Map<String, Object> getActivityDetail(String activityId, Long userId, String lang) {
        MallActivityLibrary activity = activityLibraryMapper.selectById(activityId);
        if (activity == null) throw new BizException("活动不存在");

        Map<String, Object> dto = new HashMap<>();
        dto.put("id", activity.getId());
        dto.put("startTime", activity.getStartTime());
        dto.put("endTime", activity.getEndTime());
        dto.put("images", activity.getImageUrl());
        dto.put("link", activity.getDetailUrl());
        dto.put("name", "cn".equals(lang) || "zh".equals(lang) ? activity.getTitleCn() : activity.getTitleEn());
        dto.put("description", "cn".equals(lang) || "zh".equals(lang) ? activity.getDescriptionCn() : activity.getDescriptionEn());
        dto.put("state", activity.getStatus());

        Map<String, String> config = parseActivityConfig(activity.getActivityConfig());
        dto.put("invitePoints", 0);
        dto.put("lotteryCondition", BigDecimal.ZERO);
        dto.put("lotteryNumber", 0);
        dto.put("pointsToNumber", Integer.parseInt(config.getOrDefault("scoreExchangeLotteryTimeRatio", "100")));
        dto.put("minPoints", new BigDecimal(config.getOrDefault("minReceiveMoneyThreshold", "10")));
        dto.put("createTime", activity.getCreateTime() != null ? activity.getCreateTime().toString() : null);
        dto.put("updateTime", activity.getUpdateTime() != null ? activity.getUpdateTime().toString() : null);

        // Prizes
        List<MallActivityPrize> prizes = activityPrizeMapper.selectList(
            new QueryWrapper<MallActivityPrize>().eq("activity_id", activityId).eq("status", 1).eq("deleted", 0));
        List<Map<String, Object>> prizeList = new ArrayList<>();
        List<String> prizeIds = new ArrayList<>();
        for (MallActivityPrize p : prizes) {
            Map<String, Object> pm = new HashMap<>();
            pm.put("id", p.getId());
            pm.put("prizeName", "cn".equals(lang) || "zh".equals(lang) ? p.getPrizeNameCn() : p.getPrizeNameEn());
            pm.put("prizeType", p.getPrizeType());
            pm.put("prizeAmount", p.getPrizeAmount());
            pm.put("odds", p.getOdds());
            pm.put("image", p.getImage());
            pm.put("defaultPrize", p.getDefaultPrize());
            prizeList.add(pm);
            prizeIds.add(p.getId());
        }
        dto.put("prizeList", prizeList);
        dto.put("prizeIds", prizeIds);

        MallActivityUserPoints userPoints = getOrCreateUserPoints(userId, "0");
        dto.put("points", userPoints.getPoints() != null ? userPoints.getPoints() : 0);
        return dto;
    }

    @Override
    public int getPoints(String activityId, Long userId) {
        MallActivityLibrary activity = activityLibraryMapper.selectById(activityId);
        String lookupId = (activity != null && "SIMPLE_LOTTERY".equals(activity.getType())) ? "0" : activityId;
        MallActivityUserPoints up = activityUserPointsMapper.selectOne(
            new QueryWrapper<MallActivityUserPoints>().eq("party_id", str(userId)).eq("activity_id", lookupId));
        return (up != null && up.getPoints() != null) ? up.getPoints() : 0;
    }

    @Override
    public Map<String, Object> getCountPoints(String activityId, Long userId) {
        Map<String, Object> result = new HashMap<>();
        result.put("number", 0);
        MallActivityUserPoints up = getOrCreateUserPoints(userId, "0");
        result.put("points", up.getPoints() != null ? up.getPoints() : 0);
        return result;
    }

    @Override
    @Transactional
    public Map<String, Object> draw(String activityId, Long userId, int drawTimes, String lang) {
        MallActivityLibrary activity = activityLibraryMapper.selectById(activityId);
        if (activity == null) throw new BizException("活动不存在");
        if (activity.getStatus() != 1) throw new BizException("活动未开启");

        LocalDateTime now = LocalDateTime.now();
        if (activity.getStartTime().isAfter(now)) throw new BizException("活动未开始");
        if (activity.getEndTime().isBefore(now)) throw new BizException("活动已结束");

        if (drawTimes <= 0) throw new BizException("抽奖次数无效");

        Map<String, String> config = parseActivityConfig(activity.getActivityConfig());
        int exchangeRatio = Integer.parseInt(config.getOrDefault("scoreExchangeLotteryTimeRatio", "100"));

        MallActivityUserPoints userPoints = getOrCreateUserPoints(userId, "0");
        MallActivityUser activityUser = getOrCreateActivityUser(activity, userId);

        int leftTimes = Math.max(0,
            (activityUser.getAllowJoinTimes() != null ? activityUser.getAllowJoinTimes() : 0) -
            (activityUser.getJoinTimes() != null ? activityUser.getJoinTimes() : 0));

        if (leftTimes < drawTimes) {
            int extraNeeded = drawTimes - leftTimes;
            int pointsNeeded = extraNeeded * exchangeRatio;
            if (userPoints.getPoints() < pointsNeeded) throw new BizException("积分不足");
            activityUserPointsMapper.update(null,
                new UpdateWrapper<MallActivityUserPoints>().eq("id", userPoints.getId())
                    .setSql("points = points - " + pointsNeeded));
            activityUserMapper.update(null,
                new UpdateWrapper<MallActivityUser>().eq("id", activityUser.getId())
                    .setSql("allow_join_times = allow_join_times + " + extraNeeded));
        }

        // Load prizes
        List<MallActivityPrize> allPrizes = activityPrizeMapper.selectList(
            new QueryWrapper<MallActivityPrize>().eq("activity_id", activityId).eq("status", 1).eq("deleted", 0));

        MallActivityPrize defaultPrize = allPrizes.stream()
            .filter(p -> p.getDefaultPrize() != null && p.getDefaultPrize() == 1).findFirst().orElse(null);

        List<Map<String, Object>> drawResults = new ArrayList<>();
        for (int i = 0; i < drawTimes; i++) {
            MallActivityPrize won = spinWheel(allPrizes, defaultPrize);
            if (won == null) continue;

            String prizeName = "cn".equals(lang) || "zh".equals(lang) ? won.getPrizeNameCn() : won.getPrizeNameEn();

            if (won.getPrizeType() != null && won.getPrizeType() != 3) {
                MallLotteryRecord record = new MallLotteryRecord();
                record.setId(UUID.randomUUID().toString());
                record.setPartyId(str(userId));
                record.setPrizeId(won.getId());
                record.setPrizeName(prizeName);
                record.setPrizeType(won.getPrizeType());
                record.setPrizeAmount(won.getPrizeAmount());
                record.setPrizeImage(won.getImage());
                record.setActivityId(activityId);
                record.setLotteryName("cn".equals(lang) || "zh".equals(lang) ? activity.getTitleCn() : activity.getTitleEn());
                record.setLotteryTime(LocalDateTime.now());
                record.setReceiveState(0);
                record.setCreateTime(LocalDateTime.now());
                lotteryRecordMapper.insert(record);

                if (won.getMaxQuantity() != null && won.getMaxQuantity() > 0) {
                    activityPrizeMapper.update(null,
                        new UpdateWrapper<MallActivityPrize>().eq("id", won.getId())
                            .gt("left_quantity", 0).setSql("left_quantity = left_quantity - 1"));
                }
            }

            Map<String, Object> prizeDto = new HashMap<>();
            prizeDto.put("id", won.getId());
            prizeDto.put("prizeAmount", won.getPrizeAmount());
            prizeDto.put("prizeName", prizeName);
            prizeDto.put("prizeType", won.getPrizeType());
            drawResults.add(prizeDto);
        }

        activityUserMapper.update(null,
            new UpdateWrapper<MallActivityUser>().eq("id", activityUser.getId())
                .setSql("join_times = join_times + " + drawTimes));

        Map<String, Object> result = new HashMap<>();
        result.put("prizes", drawResults);
        result.put("points", getPoints(activityId, userId));
        return result;
    }

    @Override
    public Map<String, Object> countPrize(String activityId, Long userId) {
        List<MallLotteryRecord> records = lotteryRecordMapper.selectList(
            new QueryWrapper<MallLotteryRecord>().eq("activity_id", activityId).eq("party_id", str(userId)));
        Map<String, Object> sum = new HashMap<>();
        sum.put("totalCount", records.size());
        BigDecimal totalAmount = records.stream()
            .map(r -> r.getPrizeAmount() != null ? r.getPrizeAmount() : BigDecimal.ZERO)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        sum.put("totalAmount", totalAmount);
        return sum;
    }

    @Override
    @Transactional
    public Map<String, Object> receivePrize(String activityId, Long userId, int prizeType) {
        List<MallLotteryRecord> records = lotteryRecordMapper.selectList(
            new QueryWrapper<MallLotteryRecord>().eq("activity_id", activityId)
                .eq("party_id", str(userId)).eq("receive_state", 0).eq("prize_type", prizeType));

        if (records.isEmpty()) throw new BizException("没有可领取的奖品");

        BigDecimal totalAmount = records.stream()
            .map(r -> r.getPrizeAmount() != null ? r.getPrizeAmount() : BigDecimal.ZERO)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        // Add to balance
        userBalanceMapper.addBalance(userId, totalAmount);

        StringBuilder prizeIds = new StringBuilder();
        for (MallLotteryRecord r : records) {
            if (prizeIds.length() > 0) prizeIds.append(",");
            prizeIds.append(r.getPrizeId());
            lotteryRecordMapper.update(null,
                new UpdateWrapper<MallLotteryRecord>().eq("id", r.getId())
                    .set("receive_state", 1).set("receive_time", LocalDateTime.now()));
        }

        MallLotteryReceive receive = new MallLotteryReceive();
        receive.setId(UUID.randomUUID().toString());
        receive.setActivityId(activityId);
        receive.setPartyId(str(userId));
        receive.setPrizeIds(prizeIds.toString());
        receive.setPrizeType(prizeType);
        receive.setPrizeAmount(totalAmount);
        receive.setState(1);
        receive.setApplyTime(LocalDateTime.now());
        receive.setIssueTime(LocalDateTime.now());
        receive.setCreateTime(LocalDateTime.now());
        lotteryReceiveMapper.insert(receive);

        Map<String, Object> result = new HashMap<>();
        result.put("amount", totalAmount);
        result.put("count", records.size());
        return result;
    }

    @Override
    public Map<String, Object> pageMyPrizes(String activityId, Long userId, int page, int size) {
        Page<MallLotteryRecord> pageObj = new Page<>(page, size);
        Page<MallLotteryRecord> result = lotteryRecordMapper.selectPage(pageObj,
            new QueryWrapper<MallLotteryRecord>().eq("activity_id", activityId)
                .eq("party_id", str(userId)).orderByDesc("lottery_time"));

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", page, "pageSize", size, "totalElements", result.getTotal()));
        data.put("pageList", result.getRecords());
        return data;
    }

    /**
     * 充值审核通过后调用：根据充值金额赠送大转盘/充值抽奖次数
     */
    @Transactional
    public void onRechargeApproved(Long userId, BigDecimal amount) {
        List<MallActivityLibrary> activities = activityLibraryMapper.selectList(
            new QueryWrapper<MallActivityLibrary>()
                .in("type", java.util.Arrays.asList("RECHARGE_LOTTERY", "TURNTABLE"))
                .eq("status", 1).eq("deleted", 0)
                .le("start_time", LocalDateTime.now())
                .ge("end_time", LocalDateTime.now()));
        for (MallActivityLibrary act : activities) {
            Map<String, String> config = parseActivityConfig(act.getActivityConfig());
            int pointsPerUsdt = Integer.parseInt(config.getOrDefault("rechargePointsPerUsdt", "10"));
            int points = amount.multiply(new BigDecimal(pointsPerUsdt)).intValue();
            MallActivityUserPoints up = getOrCreateUserPoints(userId, act.getId());
            activityUserPointsMapper.update(null,
                new UpdateWrapper<MallActivityUserPoints>().eq("id", up.getId())
                    .setSql("points = points + " + points));
        }
    }

    @Override
    public List<Map<String, Object>> listActivityPrize(String activityId) {
        return activityPrizeMapper.selectList(
            new QueryWrapper<MallActivityPrize>().eq("activity_id", activityId).eq("status", 1).eq("deleted", 0))
            .stream().map(p -> {
                Map<String, Object> m = new HashMap<>();
                m.put("id", p.getId());
                m.put("prizeNameCn", p.getPrizeNameCn());
                m.put("prizeNameEn", p.getPrizeNameEn());
                m.put("prizeType", p.getPrizeType());
                m.put("prizeAmount", p.getPrizeAmount());
                m.put("odds", p.getOdds());
                m.put("image", p.getImage());
                m.put("maxQuantity", p.getMaxQuantity());
                m.put("leftQuantity", p.getLeftQuantity());
                return m;
            }).collect(Collectors.toList());
    }

    // === helpers ===

    private MallActivityUserPoints getOrCreateUserPoints(Long userId, String activityId) {
        MallActivityUserPoints points = activityUserPointsMapper.selectOne(
            new QueryWrapper<MallActivityUserPoints>().eq("party_id", str(userId)).eq("activity_id", activityId));
        if (points == null) {
            points = new MallActivityUserPoints();
            points.setId(UUID.randomUUID().toString());
            points.setPartyId(str(userId));
            points.setActivityType("SIMPLE_LOTTERY");
            points.setActivityId(activityId);
            points.setPoints(0);
            points.setCreateTime(LocalDateTime.now());
            activityUserPointsMapper.insert(points);
        }
        return points;
    }

    private MallActivityUser getOrCreateActivityUser(MallActivityLibrary activity, Long userId) {
        MallActivityUser user = activityUserMapper.selectOne(
            new QueryWrapper<MallActivityUser>().eq("activity_id", activity.getId())
                .eq("user_id", str(userId)).eq("trigger_type", "LOTTERY"));
        if (user == null) {
            user = new MallActivityUser();
            user.setId(UUID.randomUUID().toString());
            user.setActivityId(activity.getId());
            user.setActivityType(activity.getType());
            user.setUserId(str(userId));
            user.setTriggerType("LOTTERY");
            user.setAllowJoinTimes(0);
            user.setJoinTimes(0);
            user.setStatus(0);
            user.setUserType(1);
            user.setCreateTime(LocalDateTime.now());
            activityUserMapper.insert(user);
        }
        return user;
    }

    private Map<String, String> parseActivityConfig(String configJson) {
        Map<String, String> config = new HashMap<>();
        if (configJson == null || configJson.isEmpty()) {
            config.put("scoreExchangeLotteryTimeRatio", "100");
            config.put("minReceiveMoneyThreshold", "10");
            return config;
        }
        configJson = configJson.trim();
        if (configJson.startsWith("[")) {
            String content = configJson.substring(1, configJson.length() - 1);
            for (String pair : content.split("\\},\\{")) {
                pair = pair.replace("{", "").replace("}", "").replace("\"", "");
                String key = null, val = null;
                for (String item : pair.split(",")) {
                    if (item.startsWith("name:")) key = item.substring(5);
                    else if (item.startsWith("value:")) val = item.substring(6);
                }
                if (key != null && val != null) config.put(key, val);
            }
        }
        config.putIfAbsent("scoreExchangeLotteryTimeRatio", "100");
        config.putIfAbsent("minReceiveMoneyThreshold", "10");
        return config;
    }

    private MallActivityPrize spinWheel(List<MallActivityPrize> prizes, MallActivityPrize defaultPrize) {
        long r = randomNum(1, 100000000);
        long temp = 0;
        for (MallActivityPrize prize : prizes) {
            double odds = prize.getOdds() != null ? prize.getOdds().doubleValue() : 0;
            int c = (int) (odds * 100000000);
            temp += c;
            long line = 100000000 - temp;
            if (c != 0 && r > line && r <= (line + c)) return prize;
        }
        return defaultPrize;
    }

    private static long randomNum(int min, int max) {
        return min + Math.round(Math.random() * (max - min));
    }

    // ======================== Admin Methods ========================

    @Override
    public Map<String, Object> adminActivityList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallActivityLibrary> qw = new QueryWrapper<>();
        qw.eq("deleted", 0);
        if (status != null) qw.eq("status", status);
        if (keyword != null && !keyword.isEmpty())
            qw.and(w -> w.like("title_cn", keyword).or().like("title_en", keyword));
        qw.orderByDesc("create_time");
        Page<MallActivityLibrary> pg = new Page<>(p, ps);
        Page<MallActivityLibrary> result = activityLibraryMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords());
        return r;
    }

    @Override
    public Map<String, Object> adminActivityDetail(String id) {
        MallActivityLibrary activity = activityLibraryMapper.selectById(id);
        if (activity == null) throw new BizException("活动不存在");
        Map<String, Object> dto = new HashMap<>();
        dto.put("id", activity.getId());
        dto.put("templateId", activity.getTemplateId());
        dto.put("type", activity.getType());
        dto.put("titleCn", activity.getTitleCn());
        dto.put("titleEn", activity.getTitleEn());
        dto.put("tags", activity.getTags());
        dto.put("startTime", activity.getStartTime());
        dto.put("endTime", activity.getEndTime());
        dto.put("allowJoinTimes", activity.getAllowJoinTimes());
        dto.put("status", activity.getStatus());
        dto.put("isShow", activity.getIsShow());
        dto.put("activityConfig", activity.getActivityConfig());
        dto.put("joinRule", activity.getJoinRule());
        dto.put("awardRule", activity.getAwardRule());
        dto.put("detailUrl", activity.getDetailUrl());
        dto.put("imageUrl", activity.getImageUrl());
        dto.put("location", activity.getLocation());
        dto.put("descriptionCn", activity.getDescriptionCn());
        dto.put("descriptionEn", activity.getDescriptionEn());
        dto.put("createTime", activity.getCreateTime());
        dto.put("updateTime", activity.getUpdateTime());
        List<MallActivityPrize> prizes = activityPrizeMapper.selectList(
            new QueryWrapper<MallActivityPrize>().eq("activity_id", id).eq("deleted", 0));
        dto.put("prizeList", prizes);
        return dto;
    }

    @Override
    @Transactional
    public void adminActivitySave(Map<String, Object> dto) {
        MallActivityLibrary a = new MallActivityLibrary();
        a.setId(UUID.randomUUID().toString().replace("-", ""));
        a.setTemplateId((String) dto.getOrDefault("templateId", ""));
        a.setType((String) dto.getOrDefault("type", "SIMPLE_LOTTERY"));
        a.setTitleCn((String) dto.get("titleCn"));
        a.setTitleEn((String) dto.get("titleEn"));
        a.setTags((String) dto.get("tags"));
        a.setStartTime(parseDateTime(dto.get("startTime")));
        a.setEndTime(parseDateTime(dto.get("endTime")));
        a.setAllowJoinTimes((Integer) dto.getOrDefault("allowJoinTimes", 0));
        a.setStatus((Integer) dto.getOrDefault("status", 0));
        a.setIsShow((Integer) dto.getOrDefault("isShow", 0));
        a.setActivityConfig((String) dto.get("activityConfig"));
        a.setJoinRule((String) dto.get("joinRule"));
        a.setAwardRule((String) dto.get("awardRule"));
        a.setDetailUrl((String) dto.get("detailUrl"));
        a.setImageUrl((String) dto.get("imageUrl"));
        a.setLocation((Integer) dto.getOrDefault("location", 0));
        a.setDescriptionCn((String) dto.get("descriptionCn"));
        a.setDescriptionEn((String) dto.get("descriptionEn"));
        a.setCreateTime(LocalDateTime.now());
        a.setUpdateTime(LocalDateTime.now());
        a.setDeleted(0);
        activityLibraryMapper.insert(a);
    }

    @Override
    @Transactional
    public void adminActivityUpdate(Map<String, Object> dto) {
        String id = (String) dto.get("id");
        MallActivityLibrary a = activityLibraryMapper.selectById(id);
        if (a == null) throw new BizException("活动不存在");
        if (dto.containsKey("titleCn")) a.setTitleCn((String) dto.get("titleCn"));
        if (dto.containsKey("titleEn")) a.setTitleEn((String) dto.get("titleEn"));
        if (dto.containsKey("tags")) a.setTags((String) dto.get("tags"));
        if (dto.containsKey("startTime")) a.setStartTime(parseDateTime(dto.get("startTime")));
        if (dto.containsKey("endTime")) a.setEndTime(parseDateTime(dto.get("endTime")));
        if (dto.containsKey("allowJoinTimes")) a.setAllowJoinTimes((Integer) dto.get("allowJoinTimes"));
        if (dto.containsKey("status")) a.setStatus((Integer) dto.get("status"));
        if (dto.containsKey("isShow")) a.setIsShow((Integer) dto.get("isShow"));
        if (dto.containsKey("activityConfig")) a.setActivityConfig((String) dto.get("activityConfig"));
        if (dto.containsKey("joinRule")) a.setJoinRule((String) dto.get("joinRule"));
        if (dto.containsKey("awardRule")) a.setAwardRule((String) dto.get("awardRule"));
        if (dto.containsKey("detailUrl")) a.setDetailUrl((String) dto.get("detailUrl"));
        if (dto.containsKey("imageUrl")) a.setImageUrl((String) dto.get("imageUrl"));
        if (dto.containsKey("location")) a.setLocation((Integer) dto.get("location"));
        if (dto.containsKey("descriptionCn")) a.setDescriptionCn((String) dto.get("descriptionCn"));
        if (dto.containsKey("descriptionEn")) a.setDescriptionEn((String) dto.get("descriptionEn"));
        a.setUpdateTime(LocalDateTime.now());
        activityLibraryMapper.updateById(a);
    }

    @Override
    public void adminActivityToggleShow(String id, Integer isShow) {
        MallActivityLibrary a = activityLibraryMapper.selectById(id);
        if (a == null) throw new BizException("活动不存在");
        activityLibraryMapper.update(null,
            new UpdateWrapper<MallActivityLibrary>().eq("id", id).set("is_show", isShow));
    }

    @Override
    @Transactional
    public void adminActivityDelete(String id) {
        MallActivityLibrary a = activityLibraryMapper.selectById(id);
        if (a == null) return;
        if (a.getStatus() == 1) throw new BizException("活动已启用，不允许删除");
        activityPrizeMapper.update(null,
            new UpdateWrapper<MallActivityPrize>().eq("activity_id", id).set("deleted", 1));
        activityLibraryMapper.update(null,
            new UpdateWrapper<MallActivityLibrary>().eq("id", id).set("deleted", 1));
    }

    @Override
    public List<Map<String, Object>> adminPrizeListByActivity(String activityId) {
        return activityPrizeMapper.selectList(
            new QueryWrapper<MallActivityPrize>().eq("activity_id", activityId).eq("deleted", 0))
            .stream().map(p -> {
                Map<String, Object> m = new HashMap<>();
                m.put("id", p.getId());
                m.put("activityId", p.getActivityId());
                m.put("prizeNameCn", p.getPrizeNameCn());
                m.put("prizeNameEn", p.getPrizeNameEn());
                m.put("prizeType", p.getPrizeType());
                m.put("prizeAmount", p.getPrizeAmount());
                m.put("maxQuantity", p.getMaxQuantity());
                m.put("leftQuantity", p.getLeftQuantity());
                m.put("odds", p.getOdds());
                m.put("status", p.getStatus());
                m.put("defaultPrize", p.getDefaultPrize());
                m.put("image", p.getImage());
                m.put("remark", p.getRemark());
                return m;
            }).collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void adminPrizeSave(Map<String, Object> dto) {
        MallActivityPrize p = new MallActivityPrize();
        p.setId(UUID.randomUUID().toString().replace("-", ""));
        p.setActivityId((String) dto.get("activityId"));
        p.setPoolId((String) dto.getOrDefault("poolId", p.getId()));
        p.setPrizeNameCn((String) dto.get("prizeNameCn"));
        p.setPrizeNameEn((String) dto.get("prizeNameEn"));
        p.setPrizeType((Integer) dto.getOrDefault("prizeType", 1));
        p.setPrizeAmount(new BigDecimal(dto.getOrDefault("prizeAmount", "0").toString()));
        p.setMaxQuantity((Integer) dto.getOrDefault("maxQuantity", 0));
        p.setLeftQuantity((Integer) dto.getOrDefault("leftQuantity", p.getMaxQuantity()));
        p.setOdds(new BigDecimal(dto.getOrDefault("odds", "0").toString()));
        p.setStatus((Integer) dto.getOrDefault("status", 1));
        p.setDefaultPrize((Integer) dto.getOrDefault("defaultPrize", 0));
        p.setImage((String) dto.get("image"));
        p.setRemark((String) dto.get("remark"));
        p.setCreateTime(LocalDateTime.now());
        p.setUpdateTime(LocalDateTime.now());
        p.setDeleted(0);
        activityPrizeMapper.insert(p);
    }

    @Override
    @Transactional
    public void adminPrizeUpdate(Map<String, Object> dto) {
        String id = (String) dto.get("id");
        MallActivityPrize p = activityPrizeMapper.selectById(id);
        if (p == null) throw new BizException("奖品不存在");
        if (dto.containsKey("prizeNameCn")) p.setPrizeNameCn((String) dto.get("prizeNameCn"));
        if (dto.containsKey("prizeNameEn")) p.setPrizeNameEn((String) dto.get("prizeNameEn"));
        if (dto.containsKey("prizeType")) p.setPrizeType((Integer) dto.get("prizeType"));
        if (dto.containsKey("prizeAmount")) p.setPrizeAmount(new BigDecimal(dto.get("prizeAmount").toString()));
        if (dto.containsKey("maxQuantity")) p.setMaxQuantity((Integer) dto.get("maxQuantity"));
        if (dto.containsKey("leftQuantity")) p.setLeftQuantity((Integer) dto.get("leftQuantity"));
        if (dto.containsKey("odds")) p.setOdds(new BigDecimal(dto.get("odds").toString()));
        if (dto.containsKey("status")) p.setStatus((Integer) dto.get("status"));
        if (dto.containsKey("defaultPrize")) p.setDefaultPrize((Integer) dto.get("defaultPrize"));
        if (dto.containsKey("image")) p.setImage((String) dto.get("image"));
        if (dto.containsKey("remark")) p.setRemark((String) dto.get("remark"));
        p.setUpdateTime(LocalDateTime.now());
        activityPrizeMapper.updateById(p);
    }

    @Override
    @Transactional
    public void adminPrizeDelete(String prizeId) {
        activityPrizeMapper.update(null,
            new UpdateWrapper<MallActivityPrize>().eq("id", prizeId).set("deleted", 1));
    }

    @Override
    public Map<String, Object> adminRecordList(String username, Integer prizeType, String startTime, String endTime, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallLotteryRecord> qw = new QueryWrapper<>();
        if (prizeType != null) qw.eq("prize_type", prizeType);
        if (username != null && !username.isEmpty()) qw.like("party_id", username);
        qw.orderByDesc("lottery_time");
        Page<MallLotteryRecord> pg = new Page<>(p, ps);
        Page<MallLotteryRecord> result = lotteryRecordMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords());
        return r;
    }

    private LocalDateTime parseDateTime(Object val) {
        if (val == null) return null;
        String s = val.toString();
        try { return LocalDateTime.parse(s); } catch (Exception e) {
            try { return LocalDateTime.parse(s + "T00:00:00"); } catch (Exception e2) {
                return null;
            }
        }
    }
}
