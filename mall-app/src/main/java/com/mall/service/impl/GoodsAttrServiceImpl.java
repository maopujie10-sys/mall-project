package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.CategoryAttr;
import com.mall.entity.ProductAttr;
import com.mall.entity.ProductAttrValue;
import com.mall.entity.ProductAttrValueLang;
import com.mall.mapper.CategoryAttrMapper;
import com.mall.mapper.ProductAttrMapper;
import com.mall.mapper.ProductAttrValueMapper;
import com.mall.mapper.ProductAttrValueLangMapper;
import com.mall.service.GoodsAttrService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class GoodsAttrServiceImpl implements GoodsAttrService {

    private final CategoryAttrMapper categoryAttrMapper;
    private final ProductAttrMapper productAttrMapper;
    private final ProductAttrValueMapper productAttrValueMapper;
    private final ProductAttrValueLangMapper productAttrValueLangMapper;

    // === Attribute Category ===

    @Override
    public Map<String, Object> categoryList(String keyword, Integer page, Integer pageSize) {
        LambdaQueryWrapper<CategoryAttr> w = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) {
            w.like(CategoryAttr::getName, keyword);
        }
        w.orderByAsc(CategoryAttr::getSort).orderByDesc(CategoryAttr::getCreateTime);
        IPage<CategoryAttr> pg = categoryAttrMapper.selectPage(new Page<>(page, pageSize), w);
        Map<String, Object> result = new HashMap<>();
        result.put("records", pg.getRecords());
        result.put("total", pg.getTotal());
        result.put("page", pg.getCurrent());
        return result;
    }

    @Override
    public CategoryAttr categoryGetById(String uuid) {
        CategoryAttr cat = categoryAttrMapper.selectById(uuid);
        if (cat == null) throw new BizException("属性分类不存在");
        return cat;
    }

    @Override
    public void categorySave(CategoryAttr category) {
        if (category.getCreateTime() == null) {
            category.setCreateTime(LocalDateTime.now());
        }
        categoryAttrMapper.insert(category);
    }

    @Override
    public void categoryUpdate(CategoryAttr category) {
        CategoryAttr existing = categoryAttrMapper.selectById(category.getId());
        if (existing == null) throw new BizException("属性分类不存在");
        category.setCreateTime(existing.getCreateTime());
        categoryAttrMapper.updateById(category);
    }

    @Override
    public void categoryDelete(String uuid) {
        categoryAttrMapper.deleteById(uuid);
    }

    // === Attribute ===

    @Override
    public Map<String, Object> attrList(String categoryId, Integer page, Integer pageSize) {
        LambdaQueryWrapper<ProductAttr> w = new LambdaQueryWrapper<>();
        if (categoryId != null && !categoryId.isBlank()) {
            w.eq(ProductAttr::getCategoryId, categoryId);
        }
        w.orderByAsc(ProductAttr::getSort).orderByDesc(ProductAttr::getCreateTime);
        IPage<ProductAttr> pg = productAttrMapper.selectPage(new Page<>(page, pageSize), w);
        Map<String, Object> result = new HashMap<>();
        result.put("records", pg.getRecords());
        result.put("total", pg.getTotal());
        result.put("page", pg.getCurrent());
        return result;
    }

    @Override
    public ProductAttr attrGetById(String uuid) {
        ProductAttr attr = productAttrMapper.selectById(uuid);
        if (attr == null) throw new BizException("属性不存在");
        return attr;
    }

    @Override
    public void attrSave(ProductAttr attr) {
        if (attr.getCreateTime() == null) {
            attr.setCreateTime(LocalDateTime.now());
        }
        productAttrMapper.insert(attr);
    }

    @Override
    public void attrUpdate(ProductAttr attr) {
        ProductAttr existing = productAttrMapper.selectById(attr.getId());
        if (existing == null) throw new BizException("属性不存在");
        attr.setCreateTime(existing.getCreateTime());
        productAttrMapper.updateById(attr);
    }

    @Override
    public void attrDelete(String uuid) {
        productAttrMapper.deleteById(uuid);
    }

    // === Attribute Value ===

    @Override
    public Map<String, Object> valueList(String attrId, Integer page, Integer pageSize) {
        LambdaQueryWrapper<ProductAttrValue> vw = new LambdaQueryWrapper<>();
        vw.eq(ProductAttrValue::getGoodAttributeId, attrId);
        vw.orderByDesc(ProductAttrValue::getCreateTime);
        IPage<ProductAttrValue> pg = productAttrValueMapper.selectPage(new Page<>(page, pageSize), vw);

        List<Map<String, Object>> records = new ArrayList<>();
        for (ProductAttrValue v : pg.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", v.getId());
            item.put("attrId", v.getGoodAttributeId());
            ProductAttrValueLang lang = getValueLang(v.getId(), "en");
            item.put("name", lang != null ? lang.getName() : "");
            item.put("lang", lang != null ? lang.getLang() : "en");
            records.add(item);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("records", records);
        result.put("total", pg.getTotal());
        result.put("page", pg.getCurrent());
        return result;
    }

    @Override
    public Object valueGetById(String id) {
        ProductAttrValue v = productAttrValueMapper.selectById(id);
        if (v == null) throw new BizException("属性值不存在");
        Map<String, Object> item = new HashMap<>();
        item.put("id", v.getId());
        item.put("attrId", v.getGoodAttributeId());
        item.put("createTime", v.getCreateTime());
        // find all langs
        LambdaQueryWrapper<ProductAttrValueLang> lw = new LambdaQueryWrapper<>();
        lw.eq(ProductAttrValueLang::getAttrValueId, id).eq(ProductAttrValueLang::getType, 0);
        item.put("langs", productAttrValueLangMapper.selectList(lw));
        return item;
    }

    @Override
    public void valueSave(String attrId, String name, String lang) {
        ProductAttr attr = productAttrMapper.selectById(attrId);
        if (attr == null) throw new BizException("属性不存在");

        String valueId = UUID.randomUUID().toString().replace("-", "");
        ProductAttrValue v = new ProductAttrValue();
        v.setId(valueId);
        v.setGoodAttributeId(attrId);
        v.setCreateTime(LocalDateTime.now());
        productAttrValueMapper.insert(v);

        ProductAttrValueLang vl = new ProductAttrValueLang();
        vl.setId(UUID.randomUUID().toString().replace("-", ""));
        vl.setAttrValueId(valueId);
        vl.setName(name);
        vl.setLang(lang != null ? lang : "en");
        vl.setType(0);
        productAttrValueLangMapper.insert(vl);
    }

    @Override
    public void valueUpdate(String id, String name, String lang) {
        ProductAttrValue v = productAttrValueMapper.selectById(id);
        if (v == null) throw new BizException("属性值不存在");

        String l = lang != null ? lang : "en";
        ProductAttrValueLang existing = getValueLang(id, l);
        if (existing == null) {
            existing = new ProductAttrValueLang();
            existing.setId(UUID.randomUUID().toString().replace("-", ""));
            existing.setAttrValueId(id);
            existing.setLang(l);
            existing.setType(0);
            existing.setName(name);
            productAttrValueLangMapper.insert(existing);
        } else {
            existing.setName(name);
            productAttrValueLangMapper.updateById(existing);
        }
    }

    @Override
    public void valueDelete(String id) {
        ProductAttrValue v = productAttrValueMapper.selectById(id);
        if (v == null) throw new BizException("属性值不存在");

        // hard delete lang records, then hard delete value (matches old system behavior)
        LambdaQueryWrapper<ProductAttrValueLang> lw = new LambdaQueryWrapper<>();
        lw.eq(ProductAttrValueLang::getAttrValueId, id);
        productAttrValueLangMapper.delete(lw);
        productAttrValueMapper.deleteById(id);
    }

    private ProductAttrValueLang getValueLang(String attrValueId, String lang) {
        LambdaQueryWrapper<ProductAttrValueLang> lw = new LambdaQueryWrapper<>();
        lw.eq(ProductAttrValueLang::getAttrValueId, attrValueId)
          .eq(ProductAttrValueLang::getLang, lang)
          .eq(ProductAttrValueLang::getType, 0);
        return productAttrValueLangMapper.selectOne(lw);
    }
}
