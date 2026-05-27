package com.mall.service.impl;

import com.mall.entity.MallLevel;
import com.mall.mapper.MallLevelMapper;
import com.mall.service.MallLevelService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class MallLevelServiceImpl implements MallLevelService {

    private final MallLevelMapper mallLevelMapper;

    @Override
    public List<Map<String, Object>> levelList() {
        List<MallLevel> list = mallLevelMapper.selectList(null);
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallLevel l : list) {
            result.add(toMap(l));
        }
        return result;
    }

    @Override
    public Map<String, Object> levelDetail(String uuid) {
        MallLevel l = mallLevelMapper.selectById(uuid);
        if (l == null) return Collections.emptyMap();
        return toMap(l);
    }

    @Override
    public Map<String, Object> levelConfig() {
        Map<String, Object> config = new HashMap<>();
        config.put("title", "卖家等级体系");
        config.put("description", "平台为鼓励广大创业者，提供升级奖励和销售利润比例提升");
        List<Map<String, Object>> levels = levelList();
        config.put("levels", levels);
        config.put("totalLevels", levels.size());
        return config;
    }

    private Map<String, Object> toMap(MallLevel l) {
        Map<String, Object> m = new HashMap<>();
        m.put("uuid", l.getUuid());
        m.put("level", l.getLevel());
        m.put("title", l.getTitle());
        m.put("condExpr", l.getCondExpr());
        m.put("profitRationMin", l.getProfitRationMin());
        m.put("profitRationMax", l.getProfitRationMax());
        m.put("promoteViewDaily", l.getPromoteViewDaily());
        m.put("awardBaseView", l.getAwardBaseView());
        m.put("awardViewMin", l.getAwardViewMin());
        m.put("awardViewMax", l.getAwardViewMax());
        m.put("upgradeCash", l.getUpgradeCash());
        m.put("hasExclusiveService", l.getHasExclusiveService());
        m.put("recommendAtFirstPage", l.getRecommendAtFirstPage());
        m.put("deliveryDays", l.getDeliveryDays());
        m.put("sellerDiscount", l.getSellerDiscount());
        m.put("teamNum", l.getTeamNum());
        return m;
    }
}
