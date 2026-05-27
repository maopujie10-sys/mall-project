package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.CommentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/comment")
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    @GetMapping("/list/{goodId}")
    public Result<?> listByGoodId(@PathVariable String goodId,
                                  @RequestParam(required = false) Integer page,
                                  @RequestParam(required = false) Integer pageSize) {
        return Result.ok(commentService.listByGoodId(goodId, page, pageSize));
    }

    @PostMapping("/add")
    public Result<?> add(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        commentService.add(userId, dto);
        return Result.ok();
    }

    @DeleteMapping("/{uuid}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable String uuid) {
        commentService.delete(userId, uuid);
        return Result.ok();
    }
}
