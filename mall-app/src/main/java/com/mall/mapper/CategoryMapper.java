package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.Category;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;

@Mapper
public interface CategoryMapper extends BaseMapper<Category> {

    @Select("SELECT * FROM mall_category WHERE status = 1 ORDER BY sort ASC")
    List<Category> selectActiveCategories();

    @Select("SELECT * FROM mall_category ORDER BY sort ASC")
    List<Category> selectAllCategories();
}
