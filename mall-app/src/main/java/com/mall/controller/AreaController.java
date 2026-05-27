package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.AreaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/area")
@RequiredArgsConstructor
public class AreaController {

    private final AreaService areaService;

    @GetMapping("/countries")
    public Result<?> countries(@RequestParam(defaultValue = "en") String lang) {
        return Result.ok(areaService.listAllCountries(lang));
    }

    @GetMapping("/states")
    public Result<?> states(@RequestParam Long countryId,
                            @RequestParam(defaultValue = "en") String lang) {
        return Result.ok(areaService.listStatesByCountry(countryId, lang));
    }

    @GetMapping("/cities")
    public Result<?> cities(@RequestParam Long stateId,
                            @RequestParam(defaultValue = "en") String lang) {
        return Result.ok(areaService.listCitiesByState(stateId, lang));
    }

    @GetMapping("/mobile-prefix")
    public Result<?> mobilePrefix() {
        return Result.ok(areaService.listAllMobilePrefix());
    }
}
