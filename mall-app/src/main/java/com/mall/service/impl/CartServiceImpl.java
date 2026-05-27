package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.CartService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class CartServiceImpl implements CartService {

    private final MallCartMapper cartMapper;
    private final ProductMapper productMapper;
    private final ProductSkuMapper skuMapper;

    @Override
    public void add(Long userId, Long productId, Long skuId, Integer quantity) {
        ProductSku sku = skuMapper.selectById(skuId.toString());
        if (sku == null) throw new BizException("商品规格不存在");
        if (sku.getSale() < quantity) throw new BizException("库存不足");

        MallCart existing = cartMapper.selectOne(new QueryWrapper<MallCart>()
            .eq("user_id", userId).eq("sku_id", skuId).eq("status", 0));
        if (existing != null) {
            existing.setQuantity(existing.getQuantity() + quantity);
            cartMapper.updateById(existing);
        } else {
            Product product = productMapper.selectById(productId);
            MallCart cart = MallCart.builder()
                .userId(userId).productId(productId)
                .skuId(skuId).quantity(quantity)
                .price(product != null ? product.getPrice() : BigDecimal.ZERO)
                .status(0).build();
            cartMapper.insert(cart);
        }
    }

    @Override
    public List<Map<String, Object>> list(Long userId) {
        List<MallCart> carts = cartMapper.selectList(
            new QueryWrapper<MallCart>().eq("user_id", userId).eq("status", 0));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallCart cart : carts) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", cart.getId());
            item.put("productId", cart.getProductId());
            item.put("skuId", cart.getSkuId());
            item.put("quantity", cart.getQuantity());
            item.put("price", cart.getPrice());
            Product product = productMapper.selectById(cart.getProductId());
            if (product != null) {
                item.put("productName", product.getName());
                item.put("mainImage", product.getMainImage());
            }
            result.add(item);
        }
        return result;
    }

    @Override
    public void update(Long userId, Long cartId, Integer quantity) {
        MallCart cart = cartMapper.selectById(cartId);
        if (cart == null || !cart.getUserId().equals(userId))
            throw new BizException("购物车记录不存在");
        if (quantity <= 0) {
            cartMapper.deleteById(cartId);
        } else {
            cart.setQuantity(quantity);
            cartMapper.updateById(cart);
        }
    }

    @Override
    public void remove(Long userId, Long cartId) {
        MallCart cart = cartMapper.selectById(cartId);
        if (cart == null || !cart.getUserId().equals(userId))
            throw new BizException("购物车记录不存在");
        cartMapper.deleteById(cartId);
    }
}
