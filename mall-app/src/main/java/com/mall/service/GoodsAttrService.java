package com.mall.service;

import com.mall.entity.CategoryAttr;
import com.mall.entity.ProductAttr;

import java.util.Map;

public interface GoodsAttrService {
    // Attribute Category
    Map<String, Object> categoryList(String keyword, Integer page, Integer pageSize);
    CategoryAttr categoryGetById(String uuid);
    void categorySave(CategoryAttr category);
    void categoryUpdate(CategoryAttr category);
    void categoryDelete(String uuid);

    // Attribute
    Map<String, Object> attrList(String categoryId, Integer page, Integer pageSize);
    ProductAttr attrGetById(String uuid);
    void attrSave(ProductAttr attr);
    void attrUpdate(ProductAttr attr);
    void attrDelete(String uuid);

    // Attribute Value
    Map<String, Object> valueList(String attrId, Integer page, Integer pageSize);
    Object valueGetById(String id);
    void valueSave(String attrId, String name, String lang);
    void valueUpdate(String id, String name, String lang);
    void valueDelete(String id);
}
