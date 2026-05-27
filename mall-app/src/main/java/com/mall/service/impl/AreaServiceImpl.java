package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallCities;
import com.mall.entity.MallCountries;
import com.mall.entity.MallStates;
import com.mall.mapper.MallCitiesMapper;
import com.mall.mapper.MallCountriesMapper;
import com.mall.mapper.MallStatesMapper;
import com.mall.service.AreaService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AreaServiceImpl implements AreaService {

    private final MallCountriesMapper countriesMapper;
    private final MallCitiesMapper citiesMapper;
    private final MallStatesMapper statesMapper;

    @Override
    public Map<String, Object> countryList(String countryName, Integer flag, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallCountries> qw = new QueryWrapper<>();
        if (countryName != null && !countryName.isEmpty())
            qw.and(w -> w.like("country_name_cn", countryName).or().like("country_name_en", countryName));
        if (flag != null) qw.eq("flag", flag);
        qw.orderByAsc("id");
        Page<MallCountries> pg = new Page<>(p, ps);
        Page<MallCountries> result = countriesMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords());
        return r;
    }

    @Override
    @Transactional
    public void countrySave(Map<String, Object> dto) {
        MallCountries c = new MallCountries();
        c.setCountryNameEn((String) dto.get("countryNameEn"));
        c.setCountryNameCn((String) dto.getOrDefault("countryNameCn", ""));
        c.setCountryNameTw((String) dto.getOrDefault("countryNameTw", ""));
        c.setFlag((Integer) dto.getOrDefault("flag", 1));
        c.setCreatedAt(LocalDateTime.now());
        c.setUpdatedAt(LocalDateTime.now());
        countriesMapper.insert(c);
    }

    @Override
    @Transactional
    public void countryUpdate(Long id, Map<String, Object> dto) {
        MallCountries c = countriesMapper.selectById(id);
        if (c == null) throw new BizException("国家不存在");
        if (dto.containsKey("countryNameEn")) c.setCountryNameEn((String) dto.get("countryNameEn"));
        if (dto.containsKey("countryNameCn")) c.setCountryNameCn((String) dto.get("countryNameCn"));
        if (dto.containsKey("countryNameTw")) c.setCountryNameTw((String) dto.get("countryNameTw"));
        if (dto.containsKey("flag")) c.setFlag((Integer) dto.get("flag"));
        c.setUpdatedAt(LocalDateTime.now());
        countriesMapper.updateById(c);
    }

    @Override
    @Transactional
    public void countryDelete(Long id) {
        MallCountries c = countriesMapper.selectById(id);
        if (c == null) throw new BizException("国家不存在");
        // Also delete associated cities
        citiesMapper.delete(new QueryWrapper<MallCities>().eq("country_id", id));
        countriesMapper.deleteById(id);
    }

    @Override
    public Map<String, Object> cityList(String cityName, Long countryId, Integer flag, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallCities> qw = new QueryWrapper<>();
        if (cityName != null && !cityName.isEmpty())
            qw.and(w -> w.like("city_name_cn", cityName).or().like("city_name_en", cityName));
        if (countryId != null) qw.eq("country_id", countryId);
        if (flag != null) qw.eq("flag", flag);
        qw.orderByAsc("id");
        Page<MallCities> pg = new Page<>(p, ps);
        Page<MallCities> result = citiesMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords());
        return r;
    }

    @Override
    @Transactional
    public void citySave(Map<String, Object> dto) {
        MallCities c = new MallCities();
        c.setCityNameEn((String) dto.get("cityNameEn"));
        c.setCityNameCn((String) dto.getOrDefault("cityNameCn", ""));
        c.setCityNameTw((String) dto.getOrDefault("cityNameTw", ""));
        c.setCountryId((Long) dto.get("countryId"));
        c.setStateId((Long) dto.getOrDefault("stateId", 0L));
        c.setFlag((Integer) dto.getOrDefault("flag", 1));
        c.setCreatedAt(LocalDateTime.now());
        c.setUpdatedAt(LocalDateTime.now());
        citiesMapper.insert(c);
    }

    @Override
    @Transactional
    public void cityUpdate(Long id, Map<String, Object> dto) {
        MallCities c = citiesMapper.selectById(id);
        if (c == null) throw new BizException("城市不存在");
        if (dto.containsKey("cityNameEn")) c.setCityNameEn((String) dto.get("cityNameEn"));
        if (dto.containsKey("cityNameCn")) c.setCityNameCn((String) dto.get("cityNameCn"));
        if (dto.containsKey("cityNameTw")) c.setCityNameTw((String) dto.get("cityNameTw"));
        if (dto.containsKey("countryId")) c.setCountryId((Long) dto.get("countryId"));
        if (dto.containsKey("stateId")) c.setStateId((Long) dto.get("stateId"));
        if (dto.containsKey("flag")) c.setFlag((Integer) dto.get("flag"));
        c.setUpdatedAt(LocalDateTime.now());
        citiesMapper.updateById(c);
    }

    @Override
    @Transactional
    public void cityDelete(Long id) {
        MallCities c = citiesMapper.selectById(id);
        if (c == null) throw new BizException("城市不存在");
        citiesMapper.deleteById(id);
    }

    @Override
    public List<Map<String, String>> listAllCountries(String lang) {
        List<MallCountries> list = countriesMapper.selectList(
            new QueryWrapper<MallCountries>().eq("flag", 1).orderByAsc("id"));
        return list.stream().map(c -> {
            Map<String, String> m = new HashMap<>();
            m.put("id", c.getId().toString());
            m.put("name", countryNameByLang(c, lang));
            return m;
        }).collect(Collectors.toList());
    }

    @Override
    public List<Map<String, String>> listStatesByCountry(Long countryId, String lang) {
        List<MallStates> list = statesMapper.selectList(
            new QueryWrapper<MallStates>().eq("country_id", countryId).eq("flag", 1).orderByAsc("id"));
        return list.stream().map(s -> {
            Map<String, String> m = new HashMap<>();
            m.put("id", s.getId().toString());
            m.put("name", stateNameByLang(s, lang));
            m.put("countryId", s.getCountryId().toString());
            return m;
        }).collect(Collectors.toList());
    }

    @Override
    public List<Map<String, String>> listCitiesByState(Long stateId, String lang) {
        List<MallCities> list = citiesMapper.selectList(
            new QueryWrapper<MallCities>().eq("state_id", stateId).eq("flag", 1).orderByAsc("id"));
        return list.stream().map(c -> {
            Map<String, String> m = new HashMap<>();
            m.put("id", c.getId().toString());
            m.put("name", cityNameByLang(c, lang));
            m.put("stateId", c.getStateId().toString());
            return m;
        }).collect(Collectors.toList());
    }

    @Override
    public List<Map<String, String>> listAllMobilePrefix() {
        // Return common mobile prefixes; can be extended to DB-backed
        List<Map<String, String>> list = new ArrayList<>();
        String[] codes = {"+86","+1","+44","+81","+82","+91","+61","+33","+49","+852","+886","+65","+60","+62","+66","+84","+7"};
        String[] names = {"China","USA/Canada","UK","Japan","Korea","India","Australia","France","Germany",
                          "Hong Kong","Taiwan","Singapore","Malaysia","Indonesia","Thailand","Vietnam","Russia"};
        for (int i = 0; i < codes.length; i++) {
            Map<String, String> m = new HashMap<>();
            m.put("code", codes[i]);
            m.put("name", names[i]);
            list.add(m);
        }
        return list;
    }

    private String countryNameByLang(MallCountries c, String lang) {
        if ("cn".equalsIgnoreCase(lang)) return c.getCountryNameCn();
        if ("tw".equalsIgnoreCase(lang)) return c.getCountryNameTw();
        return c.getCountryNameEn();
    }

    private String stateNameByLang(MallStates s, String lang) {
        if ("cn".equalsIgnoreCase(lang)) return s.getStateNameCn();
        if ("tw".equalsIgnoreCase(lang)) return s.getStateNameTw();
        return s.getStateNameEn();
    }

    private String cityNameByLang(MallCities c, String lang) {
        if ("cn".equalsIgnoreCase(lang)) return c.getCityNameCn();
        if ("tw".equalsIgnoreCase(lang)) return c.getCityNameTw();
        return c.getCityNameEn();
    }
}
