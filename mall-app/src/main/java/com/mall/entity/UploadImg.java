package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_upload_img")
public class UploadImg {
    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String fileName;

    private String fileUrl;

    private Long fileSize;

    private String fileType;

    private String uploadType;

    private String relatedId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
