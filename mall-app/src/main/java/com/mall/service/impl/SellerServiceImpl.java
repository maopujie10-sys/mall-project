package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.JwtUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.IdcodeService;
import com.mall.service.SellerService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class SellerServiceImpl implements SellerService {

    private final MallSellerMapper sellerMapper;
    private final SellerGoodsMapper sellerGoodsMapper;
    private final MallClientSellerMapper clientSellerMapper;
    private final UserMapper userMapper;
    private final KycMapper kycMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final JwtUtil jwtUtil;
    private final IdcodeService idcodeService;
    private final PasswordEncoder passwordEncoder;

    @Override
    public List<Map<String, Object>> sellerList(Map<String, Object> params) {
        QueryWrapper<MallSeller> qw = new QueryWrapper<>();
        qw.eq("status", 1);
        if (params != null && params.containsKey("keyword")) {
            String kw = (String) params.get("keyword");
            qw.and(w -> w.like("name", kw).or().like("key_words", kw));
        }
        qw.orderByDesc("create_time");
        List<MallSeller> list = sellerMapper.selectList(qw);
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallSeller s : list) {
            result.add(toSellerMap(s));
        }
        return result;
    }

    @Override
    public Map<String, Object> sellerDetail(String sellerId) {
        MallSeller seller = sellerMapper.selectById(sellerId);
        if (seller == null || seller.getStatus() == 0) throw new BizException("商家不存在");
        Map<String, Object> map = toSellerMap(seller);
        long goodsCount = sellerGoodsMapper.selectCount(
            new QueryWrapper<SellerGoods>().eq("seller_id", sellerId).eq("status", 1));
        map.put("goodsCount", goodsCount);
        return map;
    }

    @Override
    public Map<String, Object> sellerGoods(String sellerId, Integer page, Integer pageSize) {
        MallSeller seller = sellerMapper.selectById(sellerId);
        if (seller == null || seller.getStatus() == 0) throw new BizException("商家不存在");

        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        Page<SellerGoods> pg = new Page<>(p, ps);
        Page<SellerGoods> result = sellerGoodsMapper.selectPage(pg,
            new QueryWrapper<SellerGoods>()
                .eq("seller_id", sellerId)
                .eq("status", 1)
                .eq("verify_status", 1)
                .orderByDesc("sale_count"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (SellerGoods g : result.getRecords()) {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", g.getUuid());
            m.put("sellerId", g.getSellerId());
            m.put("systemGoodsId", g.getSystemGoodsId());
            m.put("price", g.getPrice());
            m.put("stock", g.getStock());
            m.put("goodsName", g.getGoodsName());
            m.put("coverImg", g.getCoverImg());
            m.put("iconImg", g.getIconImg());
            m.put("saleCount", g.getSaleCount());
            m.put("viewCount", g.getViewCount());
            list.add(m);
        }
        Map<String, Object> pageResult = new HashMap<>();
        pageResult.put("total", result.getTotal());
        pageResult.put("page", p);
        pageResult.put("pageSize", ps);
        pageResult.put("list", list);
        return pageResult;
    }

    @Override
    public Map<String, Object> clientVersion() {
        MallClientSeller client = clientSellerMapper.selectOne(
            new QueryWrapper<MallClientSeller>()
                .eq("status", 1)
                .orderByDesc("latest_version")
                .last("LIMIT 1"));
        if (client == null) return Collections.emptyMap();
        Map<String, Object> map = new HashMap<>();
        map.put("title", client.getTitle());
        map.put("latestVersion", client.getLatestVersion());
        map.put("downloadlink", client.getDownloadlink());
        map.put("content", client.getContent());
        return map;
    }

    @Override
    public Map<String, Object> clientVersionByPlatform(String platform, String lang) {
        MallClientSeller client = clientSellerMapper.selectById(platform + lang);
        Map<String, Object> map = new HashMap<>();
        map.put("plantform", "0");
        if (client != null) {
            map.put("plantform", platform);
            map.put("latestVersion", client.getLatestVersion());
            map.put("title", client.getTitle());
            map.put("content", client.getContent());
            map.put("downloadlink", client.getDownloadlink());
            map.put("status", client.getStatus());
        }
        return map;
    }

    @Override
    @Transactional
    public Map<String, Object> registerSeller(Map<String, Object> dto) {
        String username = ((String) dto.get("username")).replace(" ", "");
        String password = ((String) dto.get("password")).replace(" ", "");
        String rePassword = ((String) dto.get("rePassword")).replace(" ", "");
        String usercode = (String) dto.get("usercode");
        String sellerName = (String) dto.get("sellerName");
        String type = (String) dto.get("type");

        if (isBlank(username)) throw new BizException("用户名不能为空");
        if (isBlank(password)) throw new BizException("登录密码不能为空");
        if (isBlank(rePassword)) throw new BizException("密码确认不能为空");
        if (password.length() < 6 || password.length() > 12) throw new BizException("密码必须6-12位");
        if (!password.equals(rePassword)) throw new BizException("两次输入的密码不相同");
        if (isBlank(type) || !List.of("1", "2").contains(type)) throw new BizException("类型不能为空");
        if (isBlank((String) dto.get("name"))) throw new BizException("实名姓名不能为空");
        if (isBlank(usercode)) throw new BizException("邀请码不能为空");
        if (isBlank(sellerName)) throw new BizException("店铺名称不能为空");

        User existUser = userMapper.selectOne(new QueryWrapper<User>().eq("phone", username));
        if (existUser != null) throw new BizException("用户名已存在");

        MallSeller existSeller = sellerMapper.selectOne(
            new QueryWrapper<MallSeller>().eq("name", sellerName));
        if (existSeller != null) throw new BizException("已存在同名商铺");

        User user = User.builder()
            .phone("1".equals(type) ? username : "")
            .email("2".equals(type) ? username : "")
            .password(passwordEncoder.encode(password))
            .nickname(sellerName)
            .status(0).levelId(1)
            .build();
        userMapper.insert(user);

        UserBalance balance = UserBalance.builder()
            .userId(user.getId()).balance(BigDecimal.ZERO)
            .frozen(BigDecimal.ZERO).version(0)
            .build();
        userBalanceMapper.insert(balance);

        Kyc kyc = new Kyc();
        kyc.setUserId(user.getId());
        kyc.setRealName((String) dto.get("name"));
        kyc.setIdCardNo((String) dto.get("idnumber"));
        kyc.setNationality((String) dto.get("nationality"));
        kyc.setIdCardType((String) dto.get("idname"));
        kyc.setFrontImg((String) dto.get("idimg1"));
        kyc.setBackImg((String) dto.get("idimg2"));
        kyc.setHandImg((String) dto.get("idimg3"));
        kyc.setStatus(1);
        kyc.setSubmitTime(LocalDateTime.now());
        kycMapper.insert(kyc);

        MallSeller seller = new MallSeller();
        seller.setId(user.getId().toString());
        seller.setName(sellerName);
        seller.setAvatar((String) dto.get("sellerImg"));
        seller.setCreateTime(LocalDateTime.now());
        seller.setStatus(0);
        sellerMapper.insert(seller);

        String token = jwtUtil.generateToken(user.getId(), "MERCHANT");

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", username);
        data.put("usercode", usercode);
        return data;
    }

    @Override
    @Transactional
    public Map<String, Object> registerSellerJs(Map<String, Object> dto) {
        String username = ((String) dto.get("username")).replace(" ", "");
        String phone = dto.get("phone") != null ? ((String) dto.get("phone")).replace(" ", "") : username;
        String password = ((String) dto.get("password")).replace(" ", "");
        String rePassword = ((String) dto.get("rePassword")).replace(" ", "");
        String usercode = (String) dto.get("usercode");
        String sellerName = (String) dto.get("sellerName");
        String type = (String) dto.get("type");
        String verifcode = (String) dto.get("verifcode");

        if (isBlank(username)) throw new BizException("用户名不能为空");
        if (isBlank(password)) throw new BizException("登录密码不能为空");
        if (isBlank(rePassword)) throw new BizException("密码确认不能为空");
        if (password.length() < 6 || password.length() > 12) throw new BizException("密码必须6-12位");
        if (!password.equals(rePassword)) throw new BizException("两次输入的密码不相同");
        if (isBlank(type) || !List.of("1", "2").contains(type)) throw new BizException("类型不能为空");
        if (isBlank((String) dto.get("name"))) throw new BizException("实名姓名不能为空");
        if (isBlank(usercode)) throw new BizException("邀请码不能为空");
        if (isBlank(sellerName)) throw new BizException("店铺名称不能为空");

        // 手机号注册需要校验验证码 (Argos2)
        if ("1".equals(type) && verifcode != null && !verifcode.isEmpty()) {
            if (!idcodeService.verify(phone, verifcode, "1"))
                throw new BizException("验证码不正确");
        }

        User existUser = userMapper.selectOne(new QueryWrapper<User>().eq("phone", username));
        if (existUser != null) throw new BizException("用户名已存在");

        MallSeller existSeller = sellerMapper.selectOne(
            new QueryWrapper<MallSeller>().eq("name", sellerName));
        if (existSeller != null) throw new BizException("已存在同名商铺");

        User user = User.builder()
            .phone("1".equals(type) ? username : phone)
            .email("2".equals(type) ? username : "")
            .password(passwordEncoder.encode(password))
            .nickname(sellerName)
            .status(0).levelId(1)
            .build();
        userMapper.insert(user);

        UserBalance balance = UserBalance.builder()
            .userId(user.getId()).balance(BigDecimal.ZERO)
            .frozen(BigDecimal.ZERO).version(0)
            .build();
        userBalanceMapper.insert(balance);

        Kyc kyc = new Kyc();
        kyc.setUserId(user.getId());
        kyc.setRealName((String) dto.get("name"));
        kyc.setIdCardNo((String) dto.get("idnumber"));
        kyc.setNationality((String) dto.get("nationality"));
        kyc.setIdCardType((String) dto.get("idname"));
        kyc.setFrontImg((String) dto.get("idimg1"));
        kyc.setBackImg((String) dto.get("idimg2"));
        kyc.setHandImg((String) dto.get("idimg3"));
        kyc.setStatus(1);
        kyc.setSubmitTime(LocalDateTime.now());
        kycMapper.insert(kyc);

        MallSeller seller = new MallSeller();
        seller.setId(user.getId().toString());
        seller.setName(sellerName);
        seller.setAvatar((String) dto.get("sellerImg"));
        seller.setCreateTime(LocalDateTime.now());
        seller.setStatus(0);
        sellerMapper.insert(seller);

        String token = jwtUtil.generateToken(user.getId(), "MERCHANT");

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", username);
        data.put("usercode", usercode);
        return data;
    }

    @Override
    public void updateSignPdf(Long userId, String signPdfUrl) {
        MallSeller seller = sellerMapper.selectById(userId.toString());
        if (seller == null) throw new BizException("商家不存在");
        sellerMapper.update(null, new com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<MallSeller>()
            .eq("id", userId.toString())
            .set("sign_pdf_url", signPdfUrl));
    }

    private Map<String, Object> toSellerMap(MallSeller s) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", s.getId());
        map.put("name", s.getName());
        map.put("keyWords", s.getKeyWords());
        map.put("avatar", s.getAvatar());
        map.put("contact", s.getContact());
        map.put("shopPhone", s.getShopPhone());
        map.put("shopRemark", s.getShopRemark());
        map.put("shopAddress", s.getShopAddress());
        map.put("banner1", s.getBanner1());
        map.put("banner2", s.getBanner2());
        return map;
    }

    private boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }
}
