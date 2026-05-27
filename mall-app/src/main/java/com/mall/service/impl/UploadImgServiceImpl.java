package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.UploadImg;
import com.mall.mapper.UploadImgMapper;
import com.mall.service.UploadImgService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class UploadImgServiceImpl implements UploadImgService {

    private final UploadImgMapper uploadImgMapper;

    @Override
    public Map<String, Object> upload(Long userId, String fileName, String fileUrl,
                                       Long fileSize, String fileType, String uploadType, String relatedId) {
        UploadImg img = new UploadImg();
        img.setUserId(userId);
        img.setFileName(fileName);
        img.setFileUrl(fileUrl);
        img.setFileSize(fileSize);
        img.setFileType(fileType);
        img.setUploadType(uploadType);
        img.setRelatedId(relatedId);
        uploadImgMapper.insert(img);

        Map<String, Object> result = new HashMap<>();
        result.put("id", img.getId());
        result.put("url", fileUrl);
        return result;
    }

    @Override
    public Map<String, Object> list(Long userId, String uploadType, Integer pageNum, Integer pageSize) {
        QueryWrapper<UploadImg> qw = new QueryWrapper<UploadImg>()
                .eq("user_id", userId)
                .orderByDesc("create_time");
        if (uploadType != null && !uploadType.isEmpty()) {
            qw.eq("upload_type", uploadType);
        }
        Page<UploadImg> page = new Page<>(pageNum, pageSize);
        Page<UploadImg> result = uploadImgMapper.selectPage(page, qw);

        List<Map<String, Object>> list = new ArrayList<>();
        for (UploadImg img : result.getRecords()) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", img.getId());
            map.put("fileName", img.getFileName());
            map.put("fileUrl", img.getFileUrl());
            map.put("fileSize", img.getFileSize());
            map.put("fileType", img.getFileType());
            map.put("uploadType", img.getUploadType());
            map.put("createTime", img.getCreateTime());
            list.add(map);
        }
        Map<String, Object> ret = new HashMap<>();
        ret.put("total", result.getTotal());
        ret.put("pages", result.getPages());
        ret.put("list", list);
        return ret;
    }

    @Override
    public String delete(Long userId, Long id) {
        UploadImg img = uploadImgMapper.selectById(id);
        if (img == null || !img.getUserId().equals(userId)) {
            throw new BizException("文件不存在");
        }
        uploadImgMapper.deleteById(id);
        return img.getFileUrl();
    }
}
