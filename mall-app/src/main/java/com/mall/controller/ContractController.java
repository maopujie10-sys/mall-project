package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.ContractService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/contract")
@RequiredArgsConstructor
public class ContractController {

    private final ContractService contractService;

    @GetMapping("/info")
    public Result<?> contractInfo() {
        return Result.ok(contractService.contractInfo());
    }

    @PostMapping("/sign")
    public Result<?> signContract(@RequestAttribute Long userId, @RequestBody Map<String, String> data) {
        contractService.signContract(userId, data.get("contractType"), data.get("contractContent"));
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> myContracts(@RequestAttribute Long userId) {
        return Result.ok(contractService.myContracts(userId));
    }
}
