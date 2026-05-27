package com.mall.service;

import java.util.List;
import java.util.Map;

public interface AreaService {
    Map<String, Object> countryList(String countryName, Integer flag, Integer page, Integer pageSize);
    void countrySave(Map<String, Object> dto);
    void countryUpdate(Long id, Map<String, Object> dto);
    void countryDelete(Long id);
    Map<String, Object> cityList(String cityName, Long countryId, Integer flag, Integer page, Integer pageSize);
    void citySave(Map<String, Object> dto);
    void cityUpdate(Long id, Map<String, Object> dto);
    void cityDelete(Long id);

    // Public listing APIs for address cascading (no auth, multi-language)
    List<Map<String, String>> listAllCountries(String lang);
    List<Map<String, String>> listStatesByCountry(Long countryId, String lang);
    List<Map<String, String>> listCitiesByState(Long stateId, String lang);
    List<Map<String, String>> listAllMobilePrefix();
}
