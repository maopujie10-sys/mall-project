package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.NewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    /** 新闻分页列表 */
    @GetMapping("/list")
    public Result<?> list(@RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "20") Integer pageSize,
                          @RequestParam(required = false) String lang) {
        return Result.ok(newsService.list(pageNum, pageSize, lang));
    }

    /** CMS内容按语言获取单条（对应旧CmsController.get） */
    @GetMapping("/by-lang")
    public Result<?> getByLang(@RequestParam String lang) {
        Map<String, Object> cms = newsService.getByLang(lang);
        if (cms == null) {
            return Result.fail("内容不存在");
        }
        return Result.ok(cms);
    }

    /** 新闻详情 */
    @GetMapping("/{id}")
    public Result<?> detail(@PathVariable Long id) {
        Map<String, Object> news = newsService.detail(id);
        if (news == null) {
            return Result.fail("新闻不存在");
        }
        return Result.ok(news);
    }
}
