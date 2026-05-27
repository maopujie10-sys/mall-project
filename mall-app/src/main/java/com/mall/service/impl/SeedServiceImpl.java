package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.SeedService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class SeedServiceImpl implements SeedService {

    private final UserMapper userMapper;
    private final ProductMapper productMapper;
    private final MallOrderMapper orderMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final MallCartMapper cartMapper;
    private final MallUserAddressMapper addressMapper;
    private final MerchantMapper merchantMapper;
    private final MallCommentMapper commentMapper;

    private static final String[] PRODUCT_NAMES = {
        "Wireless Bluetooth Earbuds", "Portable Charger 20000mAh", "LED Desk Lamp",
        "Stainless Steel Water Bottle", "Yoga Mat Premium", "Mechanical Keyboard RGB",
        "USB-C Hub 7-in-1", "Smart Watch Fitness Tracker", "Noise Cancelling Headphones",
        "Phone Stand Adjustable", "Webcam 1080p HD", "Electric Toothbrush",
        "Backpack Laptop 15.6", "Sunglasses UV400", "Running Shoes Lightweight",
        "Coffee Maker Portable", "Camping Tent 4-Person", "Desk Organizer Bamboo",
        "Wireless Mouse Silent", "Screen Protector Tempered Glass", "HDMI Cable 4K",
        "Car Phone Holder", "Ring Light for Streaming", "Massage Gun Deep Tissue",
        "Air Fryer Digital", "Robot Vacuum Cleaner", "Bluetooth Speaker Waterproof",
        "Power Bank Solar", "Fitness Resistance Bands", "Travel Pillow Memory Foam"
    };

    private static final String[] CATEGORIES = {
        "Electronics", "Home & Garden", "Sports & Outdoors", "Fashion",
        "Health & Beauty", "Toys & Hobbies", "Automotive", "Office Supplies"
    };

    private static final String[] USERNAMES = {
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace",
        "Henry", "Ivy", "Jack", "Kate", "Leo", "Mia", "Noah", "Olivia"
    };

    private static final String[] STREETS = {
        "123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm St",
        "654 Maple Dr", "987 Cedar Ln", "147 Birch Blvd", "258 Walnut Ct"
    };

    @Override
    public Map<String, Object> generateProducts(int count) {
        List<Product> existing = productMapper.selectList(new QueryWrapper<Product>().eq("deleted", 0));
        int existingCount = existing.size();

        int added = 0;
        for (int i = 0; i < count; i++) {
            String name = PRODUCT_NAMES[(existingCount + i) % PRODUCT_NAMES.length];
            String seed = UUID.randomUUID().toString().substring(0, 8);
            Product p = Product.builder()
                .categoryId((long) (new Random().nextInt(8) + 1))
                .name(name + " " + seed)
                .subtitle("High quality " + name.toLowerCase())
                .mainImage("https://picsum.photos/seed/" + seed + "/400/400")
                .detailImages("[\"https://picsum.photos/seed/" + seed + "a/800/800\",\"https://picsum.photos/seed/" + seed + "b/800/800\"]")
                .price(BigDecimal.valueOf(9.99 + Math.random() * 990))
                .originalPrice(BigDecimal.valueOf(19.99 + Math.random() * 1900))
                .costPrice(BigDecimal.valueOf(5.0 + Math.random() * 500))
                .totalStock(10 + new Random().nextInt(990))
                .sales(new Random().nextInt(500))
                .virtualSales(new Random().nextInt(2000))
                .virtualViews(new Random().nextInt(10000))
                .status(1)
                .isHot(new Random().nextInt(5) == 0 ? 1 : 0)
                .isNew(new Random().nextInt(3) == 0 ? 1 : 0)
                .sort(i)
                .unit("piece")
                .description("This is a " + name + ". Great value for money.")
                .build();
            productMapper.insert(p);
            added++;
        }

        return Map.of("added", added, "total", existingCount + added);
    }

    @Override
    public Map<String, Object> generateOrders(int count) {
        List<User> users = userMapper.selectList(new QueryWrapper<User>().eq("status", 0));
        List<Product> products = productMapper.selectList(new QueryWrapper<Product>().eq("status", 1).eq("deleted", 0));
        if (users.isEmpty()) return Map.of("error", "No users found");
        if (products.isEmpty()) return Map.of("error", "No products found");

        int added = 0;
        Random rnd = new Random();
        for (int i = 0; i < count; i++) {
            User u = users.get(rnd.nextInt(users.size()));
            Product p = products.get(rnd.nextInt(products.size()));
            String orderId = UUID.randomUUID().toString().replace("-", "");

            int qty = rnd.nextInt(3) + 1;
            BigDecimal price = p.getPrice();
            BigDecimal total = price.multiply(BigDecimal.valueOf(qty));
            BigDecimal shipping = BigDecimal.valueOf(5.99 + rnd.nextInt(10));
            BigDecimal tax = total.multiply(BigDecimal.valueOf(0.08));

            // Order
            MallOrder order = new MallOrder();
            order.setUuid(orderId);
            order.setOrderNo("ORD" + System.currentTimeMillis() + String.format("%04d", i));
            order.setPartyId(String.valueOf(u.getId()));
            order.setTotalAmount(total.add(shipping).add(tax));
            order.setPayAmount(total.add(shipping).add(tax));
            order.setDiscountAmount(BigDecimal.ZERO);
            order.setOrderStatus(new int[]{2, 3, 6}[rnd.nextInt(3)]); // paid/shipped/completed
            order.setPayStatus(2);
            order.setDeliveryStatus(order.getOrderStatus() >= 3 ? 2 : 0);
            if (order.getOrderStatus() >= 3) {
                order.setLogisticsNo("SF" + (100000000 + rnd.nextInt(900000000)));
                order.setLogisticsCompany("SF Express");
            }
            order.setReceiverName(u.getNickname());
            order.setReceiverPhone(u.getPhone());
            order.setReceiverAddress("Random Street " + rnd.nextInt(999) + ", City");
            orderMapper.insert(order);

            // Order items
            MallOrdersGoods item = new MallOrdersGoods();
            item.setUuid(UUID.randomUUID().toString().replace("-", ""));
            item.setOrderId(orderId);
            item.setGoodsId(String.valueOf(p.getId()));
            item.setGoodsNum(qty);
            item.setGoodsPrize(price);
            item.setGoodsReal(price);
            item.setSystemPrice(price);
            item.setFees(shipping);
            item.setTax(tax);
            item.setGoodsSort(1);
            ordersGoodsMapper.insert(item);

            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> generateCart(int count) {
        List<User> users = userMapper.selectList(new QueryWrapper<User>().eq("status", 0));
        List<Product> products = productMapper.selectList(new QueryWrapper<Product>().eq("status", 1).eq("deleted", 0));
        if (users.isEmpty() || products.isEmpty()) return Map.of("error", "No users or products");

        int added = 0;
        Random rnd = new Random();
        for (int i = 0; i < count; i++) {
            User u = users.get(rnd.nextInt(users.size()));
            Product p = products.get(rnd.nextInt(products.size()));
            MallCart cart = MallCart.builder()
                .userId(u.getId())
                .productId(p.getId())
                .quantity(rnd.nextInt(5) + 1)
                .price(p.getPrice())
                .status(0)
                .build();
            cartMapper.insert(cart);
            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> generateAddresses(int count) {
        List<User> users = userMapper.selectList(new QueryWrapper<User>().eq("status", 0));
        if (users.isEmpty()) return Map.of("error", "No users");

        int added = 0;
        Random rnd = new Random();
        for (int i = 0; i < count; i++) {
            User u = users.get(rnd.nextInt(users.size()));
            MallUserAddress addr = new MallUserAddress();
            addr.setUuid(UUID.randomUUID().toString().replace("-", ""));
            addr.setPartyId(String.valueOf(u.getId()));
            addr.setReceiverName(u.getNickname());
            addr.setReceiverPhone(u.getPhone());
            addr.setAddressDetail(STREETS[rnd.nextInt(STREETS.length)] + ", Apt " + (rnd.nextInt(20) + 1));
            addr.setZipCode(String.valueOf(10000 + rnd.nextInt(90000)));
            addr.setIsDefault(i == 0 ? 1 : 0);
            addr.setStatus(1);
            addressMapper.insert(addr);
            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> generateMerchants(int count) {
        List<User> users = userMapper.selectList(new QueryWrapper<User>().eq("status", 0));
        if (users.isEmpty()) return Map.of("error", "No users");

        int added = 0;
        Random rnd = new Random();
        String[] shopTypes = {"ElectroHub", "FashionPlus", "HomeEssential", "SportZone", "BeautyLab"};
        for (int i = 0; i < count; i++) {
            User u = users.get(rnd.nextInt(users.size()));
            String shopName = shopTypes[rnd.nextInt(shopTypes.length)] + " " + rnd.nextInt(99);
            Merchant m = Merchant.builder()
                .userId(u.getId())
                .shopName(shopName)
                .shopPhone(u.getPhone())
                .shopAddress(STREETS[rnd.nextInt(STREETS.length)] + ", Shop " + rnd.nextInt(10))
                .shopRemark("Welcome to " + shopName + "! Best quality guaranteed.")
                .avatar("https://picsum.photos/seed/shop" + rnd.nextInt(1000) + "/100/100")
                .status(1)
                .contact(u.getNickname())
                .build();
            merchantMapper.insert(m);
            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> generateComments(int count) {
        List<Product> products = productMapper.selectList(new QueryWrapper<Product>().eq("deleted", 0));
        if (products.isEmpty()) return Map.of("error", "No products");

        String[] comments = {
            "Great product, highly recommend!", "Good quality for the price.",
            "Fast shipping, item as described.", "Works perfectly, very happy!",
            "Decent quality, would buy again.", "Excellent build quality.",
            "Arrived on time, well packaged.", "Better than expected!",
            "Solid product, good value.", "Satisfied with this purchase."
        };

        int added = 0;
        Random rnd = new Random();
        for (int i = 0; i < count; i++) {
            Product p = products.get(rnd.nextInt(products.size()));
            MallComment c = new MallComment();
            c.setUuid(UUID.randomUUID().toString().replace("-", ""));
            c.setGoodId(String.valueOf(p.getId()));
            c.setUsername(USERNAMES[rnd.nextInt(USERNAMES.length)]);
            c.setContent(comments[rnd.nextInt(comments.length)]);
            c.setDate(String.valueOf(System.currentTimeMillis()));
            commentMapper.insert(c);
            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> generateUsers(int count) {
        int added = 0;
        for (int i = 0; i < count; i++) {
            String phone = "199" + String.format("%08d", new Random().nextInt(99999999));
            // Check if phone already exists
            if (userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone)) != null) {
                continue;
            }
            String name = USERNAMES[new Random().nextInt(USERNAMES.length)];
            User u = User.builder()
                .phone(phone)
                .password("$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh")
                .nickname(name)
                .avatar("https://picsum.photos/seed/avatar" + phone + "/100/100")
                .status(0)
                .build();
            userMapper.insert(u);
            added++;
        }

        return Map.of("added", added);
    }

    @Override
    public Map<String, Object> clearAll() {
        int deleted = 0;
        deleted += orderMapper.delete(new QueryWrapper<>()) ;
        deleted += ordersGoodsMapper.delete(new QueryWrapper<>());
        deleted += cartMapper.delete(new QueryWrapper<>());
        deleted += addressMapper.delete(new QueryWrapper<>());
        deleted += commentMapper.delete(new QueryWrapper<>());
        return Map.of("deleted", deleted, "tables", "order, orders_goods, cart, address, comment");
    }
}
