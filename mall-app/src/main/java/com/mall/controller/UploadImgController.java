package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.CosService;
import com.mall.service.UploadImgService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/upload")
public class UploadImgController {

    private final UploadImgService uploadImgService;
    private final CosService cosService;
    private final String uploadPath;

    public UploadImgController(UploadImgService uploadImgService,
                               @Value("${upload.path:/home/data/uploads}") String uploadPath,
                               Optional<CosService> cosService) {
        this.uploadImgService = uploadImgService;
        this.uploadPath = uploadPath;
        this.cosService = cosService.orElse(null);
    }

    private static final Set<String> ALLOWED_MIME = Set.of(
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "image/bmp", "image/svg+xml");

    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg");

    @PostMapping
    public Result<?> upload(@RequestAttribute(required = false) Long userId,
                            @RequestParam("file") MultipartFile file,
                            @RequestParam(defaultValue = "PRODUCT") String uploadType,
                            @RequestParam(required = false) String relatedId) throws IOException {
        if (file.isEmpty()) {
            return Result.fail("文件为空");
        }
        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_MIME.contains(contentType)) {
            return Result.fail("不支持的文件类型，仅允许图片上传");
        }

        // 校验文件扩展名，防止绕过MIME伪造
        String originalName = file.getOriginalFilename();
        if (originalName != null && originalName.contains(".")) {
            String ext = originalName.substring(originalName.lastIndexOf(".")).toLowerCase();
            if (!ALLOWED_EXTENSIONS.contains(ext)) {
                return Result.fail("不支持的文件扩展名: " + ext);
            }
        }

        String fileUrl;
        if (cosService != null) {
            try {
                fileUrl = cosService.upload(file);
            } catch (Exception e) {
                return Result.fail("COS上传失败: " + e.getMessage());
            }
        } else {
            String dateDir = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));
            Path dir = Paths.get(uploadPath, dateDir);
            Files.createDirectories(dir);
            String ext = "";
            if (originalName != null && originalName.contains(".")) {
                ext = originalName.substring(originalName.lastIndexOf(".")).toLowerCase();
            }
            String savedName = UUID.randomUUID().toString().replace("-", "") + ext;
            Path target = dir.resolve(savedName);
            file.transferTo(target.toFile());
            fileUrl = "/uploads/" + dateDir + "/" + savedName;
        }

        if (userId != null) {
            Map<String, Object> result = uploadImgService.upload(
                    userId, originalName, fileUrl, file.getSize(),
                    contentType, uploadType, relatedId);
            return Result.ok(result);
        }
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("url", fileUrl);
        result.put("name", originalName);
        result.put("size", file.getSize());
        return Result.ok(result);
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(required = false) String uploadType,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(uploadImgService.list(userId, uploadType, pageNum, pageSize));
    }

    @DeleteMapping("/{id}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable Long id) {
        String fileUrl = uploadImgService.delete(userId, id);
        if (fileUrl != null && fileUrl.startsWith("/uploads/")) {
            Path filePath = Paths.get(uploadPath, fileUrl.replace("/uploads/", ""));
            try {
                Files.deleteIfExists(filePath);
            } catch (IOException ignored) {
            }
        }
        return Result.ok();
    }
}
