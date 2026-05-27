package com.mall.service;

import java.util.Map;

public interface UserService {
    Map<String, Object> login(String account, String password, String ip);
    void register(String email, String phone, String password);
    Object getInfo(Long userId);
    Object getBalance(Long userId);
    void resetPasswordSendCode(String phone, String ip);
    void resetPassword(String phone, String code, String newPassword);

    /** 获取用户安全验证方式绑定状态 */
    Map<String, Object> getVerifyMethods(Long userId);
    /** 获取谷歌验证器绑定信息（QR+密钥） */
    Map<String, Object> getGoogleAuth(Long userId);
    /** 绑定谷歌验证器 */
    boolean bindGoogleAuth(Long userId, String secret, int code);
    /** 设置/修改资金密码 */
    void setSafeword(Long userId, String oldSafeword, String safeword, String reSafeword);
    /** 验证资金密码（含Redis限流） */
    boolean verifySafeword(Long userId, String safeword);

    /** 修改登录密码（需验证旧密码） */
    void changePassword(Long userId, String oldPassword, String newPassword);
    /** 发送绑定验证码 */
    void bindSendCode(Long userId, String target, String type, String ip);
    /** 绑定/换绑手机号（loginPassword在换绑时必填） */
    void bindPhone(Long userId, String phone, String code, String loginPassword);
    /** 绑定/换绑邮箱（loginPassword在换绑时必填） */
    void bindEmail(Long userId, String email, String code, String loginPassword);

    /** 提交资金密码/安全重置申请（operate: 0=重置资金密码 1=解绑谷歌 2=解绑手机 3=解绑邮箱） */
    void applySafewordReset(Long userId, String safeword, String reSafeword, Integer operate,
                            String idcardFront, String idcardBack, String idcardHold, String remark);
    /** 获取用户自己的安全重置申请列表 */
    java.util.List<java.util.Map<String, Object>> getMySafewordApplies(Long userId);

    /** 投诉卖家 */
    void submitComplaint(Long userId, String type, String reason, String images);
    /** 投诉列表 */
    java.util.List<java.util.Map<String, Object>> complaintList(Long userId, Integer pageNum, Integer pageSize);

    /** 账号注销 */
    void logoff(Long userId, String reason, String cashPassword);

    /** 图片验证码 */
    Map<String, String> getImageCode();
    /** 推广分享信息 */
    Map<String, Object> getShare(Long userId);
    /** 更新头像 */
    void refreshAvatar(Long userId, Integer idx);
}
